/* ==========================================================================
   benchmark.js - Tab 2: Orkestrator Benchmark (SSE streaming) + Riwayat
   Mendukung:
     1. Mode Terpandu (Guided Stepper): Pengujian bertahap runtut A -> B -> C
        dengan penyimpanan akumulatif tanpa menimpa data.
     2. Mode Otomatis Penuh (Full Batch Run): Eksekusi serentak seluruh skenario.
     3. 30x Repetisi Iterasi per perlakuan & jeda pendinginan termal CPU.
   ========================================================================== */
(function () {
  "use strict";

  const BenchTab = {
    booted: false,
    running: false,
    controller: null,
    abortTimer: null,
    lastRatio: 0,
    currentStepBtn: null,
  };
  const $ = (id) => App.el(id);

  const cols = [
    "timestamp", "scenario", "filter", "resolution", "iteration", "p",
    "t_serial", "t_parallel", "speedup", "efficiency", "cpu_utilization",
    "is_identical",
  ];

  /* ------------------------------------------------------------ init */
  BenchTab.init = async function () {
    BenchTab.booted = true;

    // Toggle alur pengujian: Stepper vs Batch
    document.querySelectorAll('input[name="bench-workflow"]').forEach((radio) => {
      radio.addEventListener("change", (e) => {
        const isStepper = e.target.value === "stepper";
        $("bench-flow-stepper").hidden = !isStepper;
        $("bench-flow-batch").hidden = isStepper;
      });
    });

    // Tombol Stepper Pengujian Bertahap
    $("btn-step-a").addEventListener("click", () => {
      BenchTab.runGuidedStep("A", ["A"], "Skenario A (Pengaruh Resolusi)");
    });
    $("btn-step-b").addEventListener("click", () => {
      BenchTab.runGuidedStep("B", ["B"], "Skenario B (Skalabilitas Worker)");
    });
    $("btn-step-c").addEventListener("click", () => {
      BenchTab.runGuidedStep("C", ["C"], "Skenario C (Analisis Kompleksitas)");
    });

    // Tombol Batch Run Penuh
    $("bench-run").addEventListener("click", BenchTab.runBatch);
    $("bench-cancel").addEventListener("click", BenchTab.cancel);

    // Unduhan CSV
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
    } catch (err) {
      console.warn("Gagal memuat konfigurasi benchmark:", err);
    }

    await BenchTab.loadResults();
  };

  /* ------------------------------------------------------- stepper state */
  BenchTab.updateStepperState = function (results) {
    if (!results || !results.rows || !results.rows.length) {
      BenchTab.setStepStatus("A", "ready", "Siap");
      BenchTab.setStepStatus("B", "locked", "Terkunci (Jalankan Tahap 1)");
      BenchTab.setStepStatus("C", "locked", "Terkunci (Jalankan Tahap 2)");
      return;
    }

    const scenarios = new Set(results.rows.map((r) => r.scenario));
    const countA = results.rows.filter((r) => r.scenario === "A").length;
    const countB = results.rows.filter((r) => r.scenario === "B").length;
    const countC = results.rows.filter((r) => r.scenario === "C").length;

    if (scenarios.has("A")) {
      BenchTab.setStepStatus("A", "done", `Selesai (${countA} data)`);
      BenchTab.setStepStatus("B", "ready", "Siap");
    } else {
      BenchTab.setStepStatus("A", "ready", "Siap");
      BenchTab.setStepStatus("B", "locked", "Terkunci (Jalankan Tahap 1)");
    }

    if (scenarios.has("B")) {
      BenchTab.setStepStatus("B", "done", `Selesai (${countB} data)`);
      BenchTab.setStepStatus("C", "ready", "Siap");
    } else if (scenarios.has("A")) {
      BenchTab.setStepStatus("C", "locked", "Terkunci (Jalankan Tahap 2)");
    }

    if (scenarios.has("C")) {
      BenchTab.setStepStatus("C", "done", `Selesai (${countC} data)`);
    }
  };

  BenchTab.setStepStatus = function (step, status, text) {
    const badge = $(`step-badge-${step.toLowerCase()}`);
    const btn = $(`btn-step-${step.toLowerCase()}`);
    const card = $(`card-step-${step.toLowerCase()}`);

    if (badge) {
      badge.textContent = text;
      badge.className = "badge-pill text-[11px] " + (
        status === "done" ? "badge-success text-emerald-800 bg-emerald-50 border-emerald-200" :
        status === "ready" ? "text-primary bg-primary/10 border-primary/20" :
        "text-text-muted bg-surface-subtle border-border"
      );
    }
    if (btn) {
      btn.disabled = status === "locked";
      if (status === "done") {
        btn.className = "btn btn-secondary text-xs py-1.5 px-3";
        btn.innerHTML = `<span data-icon="rotate-cw"></span> Uji Ulang Tahap ${step}`;
      } else if (status === "ready") {
        btn.className = "btn btn-primary text-xs py-1.5 px-3";
        btn.innerHTML = `<span data-icon="play"></span> Jalankan Tahap ${step}`;
      } else {
        btn.className = "btn btn-secondary text-xs py-1.5 px-3";
        btn.innerHTML = `<span data-icon="play"></span> Jalankan Tahap ${step}`;
      }
    }
    if (card) {
      card.classList.toggle("opacity-85", status === "locked");
    }
  };

  /* ------------------------------------------------------- results */
  BenchTab.loadResults = async function () {
    try {
      const res = await App.api("/api/benchmark/results/latest");
      App.state.results = res;
      BenchTab.renderResults(res);
      BenchTab.updateStepperState(res);
    } catch (_err) {
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
      BenchTab.updateStepperState(null);
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
    const tail = res.rows.slice(-20);
    $("bench-rows").querySelector("tbody").innerHTML = tail
      .map((r) => {
        return `<tr>${cols
          .map((c) => {
            let v = r[c];
            if (typeof r[c] === "number") v = Number(r[c]).toFixed(4);
            if (c === "is_identical") v = r[c] ? "PASS" : "FAIL";
            if (c === "iteration") v = `<span class="mono-sm font-semibold">${r[c] ?? 1}</span>`;
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
    $("bench-summary-count").textContent = `${sum.count} Kombinasi Perlakuan`;
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

  /* ----------------------------------------------------------- runners */
  BenchTab.runGuidedStep = async function (stepCode, scenarios, label) {
    const isAppend = stepCode !== "A"; // Langkah B dan C mengakumulasi ke data langkah sebelumnya
    await BenchTab.executeRun({
      scenarios,
      append_results: isAppend,
      stepCode,
      title: label,
    });
  };

  BenchTab.runBatch = async function () {
    const scenarios = ["A", "B", "C"].filter((s) => $(`bench-scen-${s}`).checked);
    if (!scenarios.length) {
      BenchTab.logMessage("Pilih minimal satu skenario pengujian.", "warning");
      return;
    }
    await BenchTab.executeRun({
      scenarios,
      append_results: false,
      stepCode: null,
      title: `Batch Run (${scenarios.join("+")})`,
    });
  };

  BenchTab.executeRun = async function ({ scenarios, append_results, stepCode, title }) {
    if (BenchTab.running) return;

    const basis = $("bench-basis-select").value;
    const repetitions = parseInt($("bench-reps-select").value, 10) || 30;
    const mode = repetitions <= 5 ? "quick" : "full";
    const cool_down_seconds = $("bench-thermal-pause").checked ? 2.0 : 0.0;

    let cancelled = false;
    let failed = false;

    BenchTab.running = true;
    BenchTab.controller = new AbortController();

    // Disable all run buttons
    $("bench-run").disabled = true;
    ["a", "b", "c"].forEach((s) => {
      const b = $(`btn-step-${s}`);
      if (b) b.disabled = true;
    });

    $("bench-cancel").hidden = false;
    $("bench-cancel").disabled = false;
    App.setBtnLabel("bench-cancel", "Batalkan Pengujian");
    App.setRunStatus("running", `${title} berjalan · menyiapkan antrean…`);
    BenchTab.setProgress(0, `Menginisialisasi ${title} (${repetitions}x repetisi)...`);
    $("bench-logger-body").innerHTML = "";

    try {
      const res = await fetch("/api/benchmark/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          basis,
          mode,
          scenarios,
          repetitions,
          append_results,
          cool_down_seconds,
        }),
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
        BenchTab.logMessage("Stream dihentikan paksa. Data terukur tetap tersimpan.", "warning");
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
      $("bench-cancel").hidden = true;

      await BenchTab.loadResults();
      if (window.ChartsTab) window.ChartsTab.refreshData();

      const rows = App.state.results ? App.state.results.count : 0;
      if (failed) App.setRunStatus("error", "Eksperimen gagal — periksa logger");
      else if (cancelled) App.setRunStatus("warning", "Eksperimen dibatalkan — data tersimpan");
      else App.setRunStatus("ready", `Deterministic Engine Ready · ${rows} baris hasil tersimpan`);
    }
  };

  /* ----------------------------------------------------------- cancel */
  BenchTab.cancel = async function () {
    if (!BenchTab.running) return;
    $("bench-cancel").disabled = true;
    App.setBtnLabel("bench-cancel", "Menunggu perlakuan selesai...");
    App.setRunStatus("warning", "Membatalkan pengujian secara aman…");
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

  /* ----------------------------------------------------------- SSE parser */
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
          `Mulai Pengujian: basis=${e.basis}, repetisi=${e.repetitions || (e.quick ? 3 : 30)}x, skenario=[${e.scenarios.join(", ")}]`
        );
        break;

      case "queued":
        BenchTab.setProgress(0, `Antrean eksekusi: ${e.total} perlakuan pengujian.`);
        App.setRunStatus("running", `Benchmark berjalan · 0/${e.total}`);
        break;

      case "progress": {
        const ratio = e.index / e.total;
        BenchTab.lastRatio = ratio;
        const itText = e.iteration ? `[Iterasi ${e.iteration}]` : "";
        BenchTab.setProgress(
          ratio,
          `Skenario ${e.scenario} · ${e.filter} · ${e.resolution}px (P=${e.p}) ${itText}`
        );
        App.setRunStatus("running", `Benchmark berjalan · ${e.index}/${e.total} ${itText}`);
        BenchTab.appendRow(e.record);
        break;
      }

      case "cooldown":
        BenchTab.setProgress(BenchTab.lastRatio, e.message);
        BenchTab.logMessage(e.message, "warning");
        break;

      case "complete":
        BenchTab.setProgress(1, `${e.rows} baris data empiris tersimpan ke ${e.csv_path}!`);
        BenchTab.logMessage("Pengujian selesai & seluruh data tersimpan.", "success");
        break;

      case "cancelled":
        BenchTab.setProgress(
          e.total ? e.completed / e.total : 0,
          `Eksperimen dibatalkan: ${e.completed} dari ${e.total} perlakuan tersimpan.`
        );
        BenchTab.logMessage(
          `Dibatalkan pada ${e.completed}/${e.total} perlakuan — ${e.rows} baris tersimpan.`,
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
        if (c === "iteration") v = `<span class="mono-sm font-semibold">${r[c] ?? 1}</span>`;
        return `<td>${v}</td>`;
      })
      .join("");
    const tr = document.createElement("tr");
    tr.innerHTML = cells;
    tbody.appendChild(tr);
    while (tbody.children.length > 500) tbody.removeChild(tbody.firstChild);
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
