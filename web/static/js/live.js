/* ==========================================================================
   live.js - Tab 1: Uji Interaktif Citra (serial vs paralel, satu citra)
   Alur:
     1. Muat konfigurasi form dari /api/live/config (filter, resolusi, P).
     2. Saat sumber=dataset, muat daftar berkas dari /api/live/dataset/{res}.
     3. Saat sumber=unggah, baca berkas jadi dataURL (FileReader).
     4. POST /api/live/process, render 4 metrik + badge + 3 pane citra.
   ========================================================================== */
(function () {
  "use strict";

  const LiveTab = { booted: false };
  const $ = (id) => App.el(id);

  // Slider P memakai indeks: 0..4 -> 1,2,4,8,12 worker proses
  LiveTab.WORKERS = [1, 2, 4, 8, 12];

  /** Jumlah worker yang diminta saat ini (dari slider). */
  LiveTab.selectedP = function () {
    return LiveTab.WORKERS[Number($("live-p").value)] || 4;
  };

  /* ------------------------------------------------------------ init */
  LiveTab.init = async function () {
    LiveTab.booted = true;

    // Bind segmented source (bare radio - listener via change event)
    document
      .querySelectorAll('input[name="live-source"]')
      .forEach((r) => r.addEventListener("change", LiveTab.onSourceChange));

    $("live-syn-res").addEventListener("change", LiveTab.onSyntheticChange);
    $("live-dat-res").addEventListener("change", LiveTab.onDatasetResChange);
    $("live-filter").addEventListener("change", LiveTab.onFilterChange);
    $("live-upload").addEventListener("change", LiveTab.onUpload);
    $("live-warm-pool").addEventListener("change", LiveTab.updateFormCaption);
    $("live-p").addEventListener("input", LiveTab.updateFormCaption);
    $("live-run").addEventListener("click", LiveTab.run);

    try {
      const cfg = await App.api("/api/live/config");
      App.state.liveConfig = cfg;
      LiveTab.fillFilters(cfg.filters);
      LiveTab.onSourceChange();
      LiveTab.onFilterChange();
      LiveTab.updateFormCaption();
    } catch (err) {
      LiveTab.showErrorBadge(`Konfigurasi uji interaktif gagal dimuat: ${err.message}`);
    }
  };

  /* --------------------------------------------------- form helpers */
  LiveTab.fillFilters = function (filters) {
    const sel = $("live-filter");
    sel.innerHTML = filters
      .map(
        (f) =>
          `<option value="${f.key}" ${f.key === "gaussian" ? "selected" : ""}>${f.name}</option>`
      )
      .join("");
  };

  LiveTab.selectedFilter = function () {
    const cfg = App.state.liveConfig;
    const key = $("live-filter").value;
    return (cfg ? cfg.filters : []).find((f) => f.key === key) || key;
  };

  LiveTab.onFilterChange = function () {
    const f = LiveTab.selectedFilter();
    const cap = $("live-filter-caption");
    if (!f.complexity) return;
    cap.innerHTML = `Kompleksitas: <b>${f.complexity}</b> | Halo Radius: <span class="mono-sm">k=${f.k_radius}</span>`;
  };

  LiveTab.onSourceChange = function () {
    const source = document.querySelector('input[name="live-source"]:checked').value;
    $("live-row-dataset").hidden = source !== "dataset";
    $("live-row-synthetic").hidden = source !== "synthetic";
    $("live-row-upload").hidden = source !== "upload";
    // Pakai resolusi yang sedang dipilih, bukan DEFAULT_RES, agar daftar sampel
    // tidak desinkron dari select resolusi setelah pengguna mengganti nilai.
    if (source === "dataset") {
      LiveTab.loadDatasetList(Number($("live-dat-res").value) || DEFAULT_RES);
    }
  };

  const DEFAULT_RES = 1024;

  LiveTab.onSyntheticChange = function () {
    LiveTab.showInputPreview();
  };

  /* ---------------------- dataset listing ---------------------- */
  LiveTab.loadDatasetList = async function (resolution) {
    const sel = $("live-dat-image");
    sel.disabled = true;
    sel.innerHTML = `<option value="">Memuat daftar citra ${resolution}px...</option>`;
    try {
      const res = await App.api(`/api/live/dataset/${resolution}`);
      if (!res.images.length) {
        sel.innerHTML =
          '<option value="">(Dataset kosong - gunakan flag synthetic)</option>';
      } else {
        sel.innerHTML = res.images
          .map((n, i) => `<option value="${n}" ${i === 0 ? "selected" : ""}>${n}</option>`)
          .join("");
      }
      sel.disabled = false;
    } catch (err) {
      sel.innerHTML = `<option value="">(gagal memuat: ${err.message})</option>`;
    }
  };

  LiveTab.onDatasetResChange = function () {
    LiveTab.loadDatasetList(Number($("live-dat-res").value));
  };

  /* ---------------------- unggah ---------------------- */
  LiveTab.onUpload = function () {
    const input = $("live-upload");
    const label = $("live-upload-name");
    if (!input.files || !input.files[0]) {
      label.textContent = "Belum ada berkas dipilih.";
      return;
    }
    label.textContent = `Dipilih: ${input.files[0].name}`;
  };

  /* ekspos File->dataURL agar fungsi run() dapat aman dipakai ulang */
  LiveTab.readAsDataURL = function (file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = () => reject(new Error("Gagal membaca berkas"));
      reader.readAsDataURL(file);
    });
  };

  LiveTab.updateFormCaption = function () {
    const p = LiveTab.selectedP();
    const warm = $("live-warm-pool").checked;
    $("live-p-value").textContent = String(p);
    $("live-p").setAttribute("aria-valuetext", String(p));
    const note = $("live-warm-note");
    note.textContent = warm && p > 1
      ? `Pipeline: gunakan Pool pre-warmed persistent P=${p}`
      : p > 1
        ? "Pipeline: pool baru disiapkan saat eksekusi (tanpa pool pre-warmed)"
        : "P=1: mode serial murni (baseline single-core).";
  };

  /* ------------------------------------------------------- execution */
  LiveTab.buildSourcePayload = async function () {
    const source = document.querySelector('input[name="live-source"]:checked').value;
    if (source === "dataset") {
      const res = Number($("live-dat-res").value);
      const img = $("live-dat-image").value;
      if (!img) throw new Error("Pilih salah satu citra dataset nyata terlebih dahulu.");
      return { type: "dataset", resolution: res, image: img };
    }
    if (source === "upload") {
      const input = $("live-upload");
      if (!input.files || !input.files[0]) {
        // Jangan diam-diam mengganti ke citra sintetis: pengguna akan mengira
        // hasil berasal dari berkasnya sendiri. Lebih jujur menolak eksekusi.
        throw new Error("Belum ada berkas yang dipilih. Pilih berkas citra atau ganti sumber citra.");
      }
      const dataURL = await LiveTab.readAsDataURL(input.files[0]);
      return { type: "upload", resolution: 1024, b64: dataURL };
    }
    return { type: "synthetic", resolution: Number($("live-syn-res").value) };
  };

  LiveTab.run = async function () {
    const btn = $("live-run");
    btn.disabled = true;
    App.setBtnLabel("live-run", "Mengeksekusi...");
    App.setRunStatus("running", "Komputasi live berjalan (serial vs paralel)…");
    LiveTab.hideErrorBadge();

    try {
      const source = await LiveTab.buildSourcePayload();
      const payload = {
        source,
        filter_key: $("live-filter").value,
        p_workers: LiveTab.selectedP(),
        warm_pool: $("live-warm-pool").checked,
      };

      const result = await App.api("/api/live/process", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      App.state.lastLiveRun = result;
      LiveTab.render(result);
    } catch (err) {
      LiveTab.showErrorBadge(`Eksekusi gagal: ${err.message}`);
      App.setRunStatus("warning", "Eksekusi live gagal - lihat pesan di panel viewport");
    } finally {
      btn.disabled = false;
      App.setBtnLabel("live-run", "Jalankan Komputasi (Serial vs Paralel)");
      const last = App.state.lastLiveRun;
      if (last) {
        App.setRunStatus(
          "ready",
          `Deterministic Engine Ready · delta max ${last.max_diff.toFixed(6)}`
        );
      }
    }
  };

  /* --------------------------------------------------------- render */
  const IMG = (src, alt) => `<img class="image-viewer" src="${src}" alt="${alt}">`;

  LiveTab.render = function (r) {
    // Metadata strip
    const strip = $("live-meta-strip");
    strip.hidden = false;
    strip.innerHTML = `
      <div class="metadata-pill"><span class="meta-label">Sampel Citra</span><span class="meta-val">${r.meta.name}</span></div>
      <div class="metadata-pill"><span class="meta-label">Resolusi Matriks</span><span class="meta-val">${r.meta.width} &times; ${r.meta.height} px</span></div>
      <div class="metadata-pill"><span class="meta-label">Buffer Memori</span><span class="meta-val">${r.meta.mem_mb} MB</span></div>`;

    // Kartu metrik
    $("live-metrics").hidden = false;
    $("live-m-tserial").textContent = `${r.t_serial.toFixed(4)}s`;
    $("live-m-tparallel").textContent = `${r.t_parallel.toFixed(4)}s`;
    $("live-m-parallel-sub").textContent = `P = ${r.p_workers} Worker Proses`;
    $("live-m-speedup").textContent = `${r.speedup.toFixed(2)}x`;
    $("live-m-efficiency").textContent = `${r.efficiency.toFixed(1)}%`;
    $("live-m-cpu").textContent = `${r.cpu_utilization.toFixed(2)}%`;

    // Badge verifikasi
    const badge = $("live-badge");
    badge.classList.add("show");
    if (r.is_identical) {
      badge.className = "badge-pill badge-success badge-banner show";
      badge.innerHTML = `${Icon.get("check-circle")} VERIFIKASI 100% BIT-IDENTIK: &Delta;max = ${r.max_diff.toFixed(6)} (Hasil Paralel Presisi Bebas Artefak Seam)`;
    } else {
      badge.className = "badge-pill badge-warning badge-banner show";
      badge.innerHTML = `${Icon.get("alert-triangle")} TERDETEKSI PERBEDAAN PIKSEL: &Delta;max = ${r.max_diff.toFixed(6)}`;
    }

    // Citra pane
    $("live-img-parallel-a").innerHTML = IMG(
      r.images.parallel,
      `Hasil paralel filter ${r.filter.name} (P=${r.p_workers})`
    );
    $("live-caption-parallel-a").textContent = `Hasil Paralel (${r.filter.name}, P=${r.p_workers})`;
    $("live-img-input").innerHTML = IMG(r.images.input, "Citra masukan asli");
    $("live-caption-input").textContent = "Citra Masukan Asli";
    $("live-img-serial-b").innerHTML = IMG(
      r.images.serial,
      `Hasil serial (${r.t_serial.toFixed(4)} detik)`
    );
    $("live-caption-serial-b").textContent = `Hasil Serial (${r.t_serial.toFixed(4)} detik)`;
    $("live-img-parallel-b").innerHTML = IMG(
      r.images.parallel,
      `Hasil paralel (${r.t_parallel.toFixed(4)} detik)`
    );
    $("live-caption-parallel-b").textContent = `Hasil Paralel (${r.t_parallel.toFixed(4)} detik)`;
    $("live-img-diff").innerHTML = IMG(
      r.images.diff,
      "Matriks selisih absolut piksel"
    );
    $("live-caption-diff").textContent = `Matriks Selisih Absolut | Maksimum Selisih: ${r.max_diff.toFixed(6)} (Layar hitam pekat = 0 perbedaan piksel)`;
  };

  /* pratinjau input sebelum eksekusi: semua citra disajikan server
     dalam response, karena itu cukup tampil setelah proses selesai */
  LiveTab.showInputPreview = function () { /* placeholder: preview server-side */ };

  LiveTab.showErrorBadge = function (msg) {
    const badge = $("live-badge");
    badge.classList.add("show");
    badge.className = "badge-pill badge-danger badge-banner show";
    badge.innerHTML = `${Icon.get("alert-triangle")} ${msg}`;
  };

  LiveTab.hideErrorBadge = function () {
    const badge = $("live-badge");
    badge.className = "badge-pill badge-banner";
    badge.innerHTML = "";
  };

  window.LiveTab = LiveTab;
})();
