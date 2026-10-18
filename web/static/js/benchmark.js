/* ==========================================================================
   benchmark.js - Tab 2: Orkestrator Benchmark (SSE streaming) + Riwayat
   Alur:
     1. init(): muat konfigurasi & riwayat hasil dari server.
     2. run(): fetch POST /api/benchmark/run -> parse SSE via ReadableStream;
        tiap event "progress" dipakai untuk progress bar + logger tabel.
     3. Dapat dibatalkan: POST /api/benchmark/cancel lalu tunggu event
        "cancelled" (perlakuan berjalan diselesaikan lebih dulu); AbortController
        hanya dipakai sebagai katup pengaman bila server tidak merespons.
     4. Setelah selesai/dibatalkan, refresh tabel riwayat + ringkasan + CSV.
   ========================================================================== */
(function () {
  "use strict";

  const BenchTab = { booted: false, running: false, controller: null, abortTimer: null };
  const $ = (id) => App.el(id);

  const cols = [
    "timestamp", "scenario", "filter", "resolution", "p",
    "t_serial", "t_parallel", "speedup", "efficiency", "cpu_utilization",
    "is_identical",
  ];

  /* ------------------------------------------------------------ init */
  BenchTab.init = async function () {
    BenchTab.booted = true;
    $("bench-run").addEventListener("click", BenchTab.run);
    $("bench-cancel").addEventListener("click", BenchTab.cancel);

    // Unduhan CSV memakai <button> (bukan <a>) agar atribut disabled benar-benar
    // menghentikan aktivasi keyboard, bukan sekadar pointer-events CSS.
    ["bench-dl-raw", "bench-dl-summary"].forEach((id) => {
      $(id).addEventListener("click", () => {
        const url = id === "bench-dl-raw"
          ? "/api/benchmark/results/raw-csv"
          : "/api/benchmark/results/summary-csv";
        window.location.assign(url);
      });
    });

    try {
      const cfg = await App.api("/api/benchmark/config");
      App.state.benchConfig = cfg;
      const counts = cfg.dataset_counts;
      $("bench-target-note").innerHTML =
        `Target res: <span class="mono-sm">512:${counts["512"]} | 1024:${counts["1024"]} | ` +
        `2048:${counts["2048"]} | 4096:${counts["4096"]}</span> citra pada disk.`;
    } catch (err) {
      $("bench-target-note").textContent = `Konfigurasi gagal: ${err.message}`;
    }
    await BenchTab.loadResults();
  };

  /* ------------------------------------------------------- results */
  BenchTab.loadResults = async function () {
    try {
      const res = await App.api("/api/benchmark/results/latest");
      App.state.results = res;
      BenchTab.renderResults(res);
    } catch (_err) {
      // 404: belum ada data
      $("bench-summary-label").textContent =
        "Riwayat Pengujian: (kosong - jalankan eksperimen untuk mengisi tabel)";
      $("bench-rows").querySelector("tbody").innerHTML =
        `<tr><td colspan="${cols.length}">Belum ada data riwayat pengujian.</td></tr>`;
      $("bench-summary-details").hidden = true;
      $("bench-dl-raw").disabled = true;
      $("bench-dl-summary").disabled = true;
      $("bench-chart-refresh").disabled = true;
      App.setBtnLabel("bench-dl-raw", "Data Mentah");
      App.setBtnLabel("bench-dl-summary", "Ringkasan");
    }
    try {
      const sum = await App.api("/api/benchmark/results/summary");
      BenchTab.renderSummary(sum);
    } catch (_err) {
      $("bench-summary-details").hidden = true;
    }
  };

  BenchTab.renderResults = function (res) {
    $("bench-summary-label").textContent = `Riwayat Pengujian Terkini: ${res.count} Baris Data Empiris`;
    const tail = res.rows.slice(-15);
    $("bench-rows").querySelector("tbody").innerHTML = tail
      .map((r) => {
        return `<tr>${cols
          .map((c) => {
            let v = r[c];
            if (typeof r[c] === "number") v = Number(r[c]).toFixed(4);
            if (c === "is_identical") v = r[c] ? "PASS" : "FAIL";
            return `<td>${v}</td>`;
          })
          .join("")}</tr>`;
      })
      .join("");
    $("bench-dl-raw").disabled = false;
    $("bench-dl-summary").disabled = false;
    App.setBtnLabel("bench-dl-raw", `Data Mentah (${res.count} Baris)`);
    $("bench-chart-refresh").disabled = false;
  };

  BenchTab.renderSummary = function (sum) {
    $("bench-summary-details").hidden = false;
    $("bench-summary-count").textContent = `${sum.count} Baris`;
    const body = $("bench-summary-rows").querySelector("tbody");
    body.innerHTML = sum.rows
      .map((r) => {
        const cells = [
          r.scenario, r.filter, r.resolution, r.p,
          r.Sampel, r.Ts_Mean, r.Tp_Mean, r.Speedup_Mean,
          (r.Speedup_Std ?? 0).toFixed(3), r.Efisiensi_Mean, r.CPU_Util_Mean,
        ];
        return `<tr>${cells
          .map((v, i) => {
            const numeric = i >= 4 && i !== 0;
            return `<td>${numeric ? Number(v).toFixed(4) : v}</td>`;
          })
          .join("")}</tr>`;
      })
      .join("");
  };

  /* ----------------------------------------------------------- SSE */
  BenchTab.run = async function () {
    if (BenchTab.running) return;
    const scenarios = ["A", "B", "C"].filter((s) => $(`bench-scen-${s}`).checked);
    if (!scenarios.length) {
      BenchTab.logMessage("Pilih minimal satu skenario pengujian.", "warning");
      return;
    }
    const basis = document.querySelector('input[name="bench-basis"]:checked').value;
    const mode = document.querySelector('input[name="bench-mode"]:checked').value;

    // Gerbang konfirmasi untuk mode panjang: 30 sampel x 4 resolusi x skenario.
    if (mode === "full") {
      const ok = window.confirm(
        "Konfirmasi: Full Scientific Benchmark\n\n" +
          "Mode ini menjalankan ratusan perlakuan pengukuran (30 sampel per resolusi " +
          "pada 4 tingkat resolusi, dikali jumlah skenario terpilih) dan dapat berjalan " +
          "lama di laptop uji.\n\nLanjutkan menjalankan eksperimen penuh?"
      );
      if (!ok) {
        BenchTab.logMessage("Mode Full dibatalkan sebelum dijalankan.", "warning");
        return;
      }
    }

    let cancelled = false;
    let failed = false;

    BenchTab.running = true;
    BenchTab.controller = new AbortController();
    $("bench-run").disabled = true;
    App.setBtnLabel("bench-run", "Eksperimen Berjalan...");
    $("bench-cancel").hidden = false;
    $("bench-cancel").disabled = false;
    App.setBtnLabel("bench-cancel", "Batalkan Eksperimen");
    App.setRunStatus("running", "Benchmark berjalan · menyiapkan antrean…");
    BenchTab.setProgress(0, "Menginisialisasi pre-warmed pool & memverifikasi berkas...");
    $("bench-logger-body").innerHTML = "";

    try {
      const res = await fetch("/api/benchmark/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ basis, mode, scenarios }),
        signal: BenchTab.controller.signal,
      });
      if (!res.ok || !res.body) {
        const txt = await res.text();
        throw new Error(`Server menolak (${res.status}): ${txt.slice(0, 200)}`);
      }
      await BenchTab.consumeSSE(res.body);
    } catch (err) {
      if (err.name === "AbortError") {
        cancelled = true;
        BenchTab.logMessage(
          "Stream dihentikan paksa (server tidak menutup dalam batas waktu). " +
            "Hasil yang sudah terukur tetap tersimpan di CSV.",
          "warning"
        );
      } else {
        failed = true;
        BenchTab.logMessage(`Eksperimen gagal: ${err.message}`, "error");
      }
    } finally {
      if (BenchTab.abortTimer) {
        clearTimeout(BenchTab.abortTimer);
        BenchTab.abortTimer = null;
      }
      BenchTab.running = false;
      BenchTab.controller = null;
      $("bench-run").disabled = false;
      App.setBtnLabel("bench-run", "Jalankan Eksperimen Pengujian");
      $("bench-cancel").hidden = true;
      await BenchTab.loadResults();
      if (window.ChartsTab) window.ChartsTab.refreshData();

      const rows = App.state.results ? App.state.results.count : 0;
      if (failed) App.setRunStatus("error", "Eksperimen gagal — lihat logger untuk detail");
      else if (cancelled) App.setRunStatus("warning", "Eksperimen dibatalkan — baris terukur tetap tersimpan");
      else App.setRunStatus("ready", `Deterministic Engine Ready · ${rows} baris hasil`);
    }
  };

  /**
   * Pembatalan kooperatif: minta server berhenti di batas perlakuan berikutnya,
   * lalu tunggu event "cancelled". AbortController dijadikan katup pengaman
   * bila server tidak menutup stream dalam 5 detik.
   */
  BenchTab.cancel = async function () {
    if (!BenchTab.running) return;
    $("bench-cancel").disabled = true;
    App.setBtnLabel("bench-cancel", "Menunggu perlakuan selesai...");
    App.setRunStatus("warning", "Permintaan pembatalan dikirim — menunggu perlakuan berjalan selesai…");
    try {
      await App.api("/api/benchmark/cancel", { method: "POST" });
    } catch (err) {
      console.error("Permintaan pembatalan gagal:", err);
    }
    if (BenchTab.abortTimer) clearTimeout(BenchTab.abortTimer);
    BenchTab.abortTimer = setTimeout(() => {
      if (BenchTab.running && BenchTab.controller) BenchTab.controller.abort();
    }, 5000);
  };

  /** Parser SSE generik untuk stream fetch() (dukungan POST, tanpa EventSource) */
  BenchTab.consumeSSE = async function (stream) {
    const reader = stream.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    for (;;) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      let sep;
      while ((sep = buffer.indexOf("\n\n")) !== -1) {
        const chunk = buffer.slice(0, sep);
        buffer = buffer.slice(sep + 2);
        const lines = chunk
          .split("\n")
          .filter((l) => l.startsWith("data:"))
          .map((l) => l.slice(5).trim());
        if (!lines.length) continue;
        try {
          BenchTab.handleEvent(JSON.parse(lines.join("\n")));
        } catch (err) {
          console.error("Event SSE tidak valid:", err);
        }
      }
    }
  };

  BenchTab.handleEvent = function (e) {
    switch (e.type) {
      case "start":
        BenchTab.logMessage(
          `Mulai: basis=${e.basis}, mode=${e.quick ? "quick" : "full"}, skenario ${e.scenarios.join("+")}`
        );
        break;

      case "queued":
        BenchTab.setProgress(0, `Antrean eksekusi: ${e.total} perlakuan benchmark.`);
        App.setRunStatus("running", `Benchmark berjalan · 0/${e.total}`);
        break;

      case "progress":
        BenchTab.setProgress(
          e.index / e.total,
          `Skenario ${e.scenario} | Filter ${e.filter} | ${e.resolution}px (P=${e.p}) | Citra: ${e.image}`
        );
        App.setRunStatus("running", `Benchmark berjalan · ${e.index}/${e.total}`);
        BenchTab.appendRow(e.record);
        break;

      case "complete":
        BenchTab.setProgress(1, `${e.rows} baris data empiris tersimpan ke ${e.csv_path}!`);
        BenchTab.logMessage("Benchmark selesai & disimpan.", "success");
        break;

      case "cancelled":
        BenchTab.setProgress(
          e.total ? e.completed / e.total : 0,
          `Eksperimen dibatalkan: ${e.completed} dari ${e.total} perlakuan terukur & tersimpan.`
        );
        BenchTab.logMessage(
          `Dibatalkan pada ${e.completed}/${e.total} perlakuan — ${e.rows} baris tersimpan ke ${e.csv_path}.`,
          "warning"
        );
        break;

      case "error":
        BenchTab.logMessage(`Server melaporkan error: ${e.message}`, "error");
        break;
    }
  };

  BenchTab.setProgress = function (ratio, text) {
    const pct = Math.max(0, Math.min(100, Math.round((Number(ratio) || 0) * 100)));
    const track = document.querySelector(".progress-track");
    if (track) {
      track.setAttribute("aria-valuenow", String(pct));
      track.setAttribute("aria-valuetext", `${pct}% - ${text || ""}`);
    }
    $("bench-progress-fill").style.transform = `scaleX(${pct / 100})`;
    $("bench-progress-text").textContent = text || "";
  };

  BenchTab.appendRow = function (r) {
    const tbody = $("bench-logger-body");
    const cells = cols
      .map((c) => {
        let v = r[c];
        if (typeof r[c] === "number") v = Number(r[c]).toFixed(4);
        if (c === "is_identical") v = r[c] ? "PASS" : "FAIL";
        return `<td>${v}</td>`;
      })
      .join("");
    const tr = document.createElement("tr");
    tr.innerHTML = cells;
    tbody.appendChild(tr);
    while (tbody.children.length > 400) tbody.removeChild(tbody.firstChild);
    const scroll = $("bench-logger-scroll");
    scroll.scrollTop = scroll.scrollHeight;
  };

  BenchTab.logMessage = function (msg, level) {
    const tbody = $("bench-logger-body");
    const tr = document.createElement("tr");
    const cls = level === "error" ? "badge-danger" : level === "warning" ? "badge-warning" : "badge-success";
    tr.innerHTML = `<td colspan="${cols.length}"><span class="badge-inline ${cls}">${msg}</span></td>`;
    tbody.appendChild(tr);
    const scroll = $("bench-logger-scroll");
    scroll.scrollTop = scroll.scrollHeight;
  };

  window.BenchTab = BenchTab;
})();
