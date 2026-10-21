/* ==========================================================================
   charts.js - Tab 3: Analisis & Grafik (Chart.js, offline dari assets/vendor)
   Fitur:
     1. Simulator Kurva Hukum Amdahl (slider f, slider P maks).
     2. Overlay titik empiris (mean speedup Skenario B) pada kurva Amdahl.
     3. Plot dinamis Skenario A (waktu & speedup vs resolusi).
     4. Plot dinamis Skenario B (skalabilitas worker P=1..8).
     5. Plot dinamis Skenario C (speedup & efisiensi per kompleksitas).
   Prinsip: hasil agregasi dihitung di JS dari /api/benchmark/results/latest
   (mean per kombinasi), tanpa menggandakan logika server.
   ========================================================================== */
(function () {
  "use strict";

  const ChartsTab = { booted: false, charts: {} };
  const $ = (id) => App.el(id);

  const COLORS = {
    "Grayscale": "#64748B",
    "Gaussian Blur": "#3B82F6",
    "Sobel": "#7C3AED",
  };
  const PRIMARY = "#1E40AF";
  const HIGHLIGHT = "#D97706"; /* Amber - garis asimtot & aksen */
  const GRAY = "#94A3B8";
  const GRID = "#E2E8F0";
  const TEXT = "#0F172A";

  const hexToRgba = (hex, alpha = 0.08) => {
    if (!hex || !hex.startsWith("#")) return hex;
    const clean = hex.replace("#", "");
    const r = parseInt(clean.substring(0, 2), 16);
    const g = parseInt(clean.substring(2, 4), 16);
    const b = parseInt(clean.substring(4, 6), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  };

  /** Spline + isian gradasi area (DESIGN.md 7.5: tension 0.4). */
  const TENSION = 0.4;

  /**
   * Isian gradasi vertikal untuk area chart (menggantikan flat rgba).
   * Aman dipanggil sebelum chartArea Chart.js siap (fallback ke rgba datar).
   */
  const areaFill = (ctx, color, alphaTop = 0.22) => {
    const chart = ctx.chart;
    const area = chart.chartArea;
    if (!area) return hexToRgba(color, 0.12);
    const grad = chart.ctx.createLinearGradient(0, area.top, 0, area.bottom);
    grad.addColorStop(0, hexToRgba(color, alphaTop));
    grad.addColorStop(1, hexToRgba(color, 0));
    return grad;
  };

  /* ------------------------------------------------- default kartu axis */
  const baseScales = () => ({
    x: {
      grid: { color: GRID, drawBorder: false },
      ticks: { color: TEXT, font: { size: 10 } },
      title: { display: true, color: TEXT, font: { size: 10, weight: "bold" } },
    },
    y: {
      grid: { color: GRID, drawBorder: false },
      ticks: { color: TEXT, font: { size: 10 } },
      title: { display: true, color: TEXT, font: { size: 10, weight: "bold" } },
    },
  });

  const baseOptions = () => ({
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 250 },
    elements: {
      point: { hoverRadius: 6, hoverBorderWidth: 0 },
      line: { borderCapStyle: "round", borderJoinStyle: "round" },
    },
    plugins: {
      legend: {
        position: "top",
        labels: {
          usePointStyle: true,
          pointStyle: "circle",
          boxWidth: 8,
          boxHeight: 8,
          padding: 14,
          font: { size: 11 },
          color: TEXT,
        },
      },
      tooltip: {
        backgroundColor: "#FFFFFF",
        titleColor: TEXT,
        bodyColor: "#475569",
        borderColor: "#DBEAFE",
        borderWidth: 1,
        cornerRadius: 10,
        padding: 10,
        boxPadding: 5,
        usePointStyle: true,
        titleFont: { size: 11, weight: "bold" },
        bodyFont: { size: 11 },
      },
    },
    scales: baseScales(),
  });

  /* ------------------------------------------------------------ export utilities */
  ChartsTab.downloadCanvasAsPng = function (canvasId, fileName) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
      console.warn(`Canvas dengan ID "${canvasId}" tidak ditemukan.`);
      return;
    }
    try {
      // Buat canvas sementara berlatar putih pekat (mencegah latar transparan saat di-paste ke Word)
      const exportCanvas = document.createElement("canvas");
      exportCanvas.width = canvas.width;
      exportCanvas.height = canvas.height;
      const ctx = exportCanvas.getContext("2d");
      ctx.fillStyle = "#FFFFFF";
      ctx.fillRect(0, 0, exportCanvas.width, exportCanvas.height);
      ctx.drawImage(canvas, 0, 0);

      const url = exportCanvas.toDataURL("image/png");
      const a = document.createElement("a");
      a.href = url;
      a.download = fileName.endsWith(".png") ? fileName : `${fileName}.png`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    } catch (err) {
      console.error("Gagal mengunduh canvas grafik:", err);
    }
  };

  /* ------------------------------------------------------------ init */
  ChartsTab.init = async function () {
    ChartsTab.booted = true;

    $("amdahl-f").addEventListener("input", ChartsTab.rebuildAmdahl);
    $("amdahl-p").addEventListener("input", ChartsTab.rebuildAmdahl);
    ChartsTab.rebuildAmdahl();

    // Unduh PNG canvas simulasi Amdahl
    const btnAmdahl = $("btn-dl-amdahl-png");
    if (btnAmdahl) {
      btnAmdahl.addEventListener("click", () => {
        const f = Number($("amdahl-f").value).toFixed(2);
        ChartsTab.downloadCanvasAsPng("amdahl-chart", `simulasi_kurva_hukum_amdahl_f${f}`);
      });
    }

    // Unduh PNG per kanvas grafik empiris
    document.querySelectorAll(".btn-dl-canvas").forEach((btn) => {
      btn.addEventListener("click", () => {
        const targetId = btn.getAttribute("data-canvas");
        const name = btn.getAttribute("data-name") || "grafik_komputasi_paralel";
        ChartsTab.downloadCanvasAsPng(targetId, name);
      });
    });

    // Unduh plot publikasi ilmiah 300 DPI Matplotlib per skenario aktif
    const btnScenPlot = $("btn-dl-scenario-plot-300dpi");
    if (btnScenPlot) {
      btnScenPlot.addEventListener("click", () => {
        const which = $("plot-select").value || "A";
        window.location.assign(`/api/benchmark/plots/single/${which}`);
      });
    }

    // Unduh paket lengkap seluruh plot 300 DPI dalam arsip ZIP
    const btnZip = $("btn-dl-all-plots-zip");
    if (btnZip) {
      btnZip.addEventListener("click", () => {
        window.location.assign("/api/benchmark/plots/bundle/zip");
      });
    }

    $("plot-select").addEventListener("change", ChartsTab.renderScenario);
    await ChartsTab.refreshData();
  };

  /* ------------------------------------------------------------ data */
  ChartsTab.refreshData = async function () {
    try {
      const res = await App.api("/api/benchmark/results/latest");
      App.state.results = res;
      $("plot-empty").hidden = true;
    } catch (_err) {
      App.state.results = null;
      $("plot-empty").hidden = false;
      $("plot-empty").textContent =
        "Belum ada data pengujian. Jalankan eksperimen pada panel Orkestrator Benchmark terlebih dahulu.";
    }
    if (ChartsTab.booted) ChartsTab.rebuildAmdahl(); // overlay empiris ikut diperbarui
    ChartsTab.renderScenario();
  };

  /* --------------------------------------------------- agregasi mean */
  /**
   * Group mean empiris.
   * rows       : baris hasil benchmark
   * outerKey   : dimensi utama (mis. "filter")
   * valueKey   : dimensi x-axis (mis. "resolution"|"p")
   * return: Map<outer, {labels: [] , map: Map<value, {Ts,Tp,S}>}>
   */
  ChartsTab.aggregate = function (rows, outerKey, valueKey) {
    const getters = {
      Ts: (r) => r.t_serial,
      Tp: (r) => r.t_parallel,
      S: (r) => r.speedup,
      E: (r) => r.efficiency,
    };
    // buckets[outer][value] = [rows]
    const buckets = new Map();
    for (const r of rows) {
      if (!buckets.has(r[outerKey])) buckets.set(r[outerKey], new Map());
      const inner = buckets.get(r[outerKey]);
      if (!inner.has(r[valueKey])) inner.set(r[valueKey], []);
      inner.get(r[valueKey]).push(r);
    }
    const avg = (list, getter) => list.reduce((s, r) => s + getter(r), 0) / list.length;

    const result = new Map();
    for (const [outer, inner] of buckets.entries()) {
      const stats = new Map();
      for (const [value, list] of inner.entries()) {
        const s = {};
        for (const [name, getter] of Object.entries(getters)) {
          s[name] = avg(list, getter);
        }
        stats.set(value, s);
      }
      result.set(outer, stats);
    }
    return result;
  };

  /* --------------------------------------------------- Amdahl simulator */
  ChartsTab.rebuildAmdahl = function () {
    const f = Number($("amdahl-f").value);
    const pMax = Number($("amdahl-p").value);
    $("amdahl-f-label").textContent = f.toFixed(2);
    $("amdahl-p-label").textContent = String(pMax);

    const asymptote = 1 / (1 - f);
    $("amdahl-asym").textContent = `${asymptote.toFixed(2)}x`;
    $("amdahl-serial").textContent = `${((1 - f) * 100).toFixed(1)}%`;

    const labels = [];
    const curve = [];
    const ideal = [];
    for (let p = 1; p <= pMax; p++) {
      labels.push(String(p));
      curve.push(Number((1 / ((1 - f) + f / p)).toFixed(4)));
      ideal.push(p);
    }
    const asmLine = labels.map(() => asymptote.toFixed(4));

    const datasets = [
      {
        label: `Kurva Amdahl (f = ${f.toFixed(2)})`,
        data: curve,
        borderColor: PRIMARY,
        backgroundColor: (ctx) => areaFill(ctx, PRIMARY),
        fill: true,
        borderWidth: 2.5,
        pointRadius: 0,
        tension: TENSION,
      },
      {
        label: `Batas Asimtot (${asymptote.toFixed(2)}x)`,
        data: asmLine.map(Number),
        borderColor: HIGHLIGHT,
        borderDash: [6, 5],
        borderWidth: 1.4,
        pointRadius: 0,
      },
      {
        label: "Linier Ideal (S = P)",
        data: ideal,
        borderColor: GRAY,
        borderDash: [2, 3],
        borderWidth: 1.2,
        pointRadius: 0,
      },
    ];

    // Overlay empiris: mean speedup Skenario B per filter (jika ada)
    const results = App.state.results;
    if (results) {
      const rowsB = results.rows.filter((r) => r.scenario === "B");
      const agg = ChartsTab.aggregate(rowsB, "filter", "p");
      for (const [fname, stats] of agg.entries()) {
        const color = COLORS[fname] || PRIMARY;
        const plist = [...stats.keys()].sort((a, b) => a - b).filter((p) => p <= pMax);
        if (!plist.length) continue;
        datasets.push({
          label: `Empiris ${fname}`,
          data: plist.map((p) => Number(stats.get(p).S.toFixed(3))),
          borderColor: color,
          backgroundColor: color,
          showLine: false,
          pointRadius: 4.5,
          pointStyle: "circle",
        });
      }
    }

    ChartsTab.attachChart(
      "amdahl-chart",
      "line",
      { labels, datasets },
      { yTitle: "Speedup (S)", xTitle: "Jumlah Worker Proses (P)", yMax: asymptote * 1.15 }
    );
  };

  /* ------------------------------------------------- plot per skenario */
  ChartsTab.renderScenario = function () {
    const which = $("plot-select").value || "A";
    const results = App.state.results;

    // Sembunyikan SELURUH bingkai chart saat tidak ada data (jangan sisakan
    // kotak ber-border kosong di bawah catatan peringatan).
    ["a", "b", "c"].forEach((id) => {
      const wrap = $(`plot-wrap-${id}`);
      if (wrap) wrap.hidden = !results || id !== which.toLowerCase();
    });
    $("plot-empty").hidden = !!results;

    if (!results) {
      ["chart-a-time", "chart-a-speedup", "chart-b", "chart-c-speedup", "chart-c-eff"].forEach(
        (id) => ChartsTab.destroy(id)
      );
      return;
    }
    if (which === "A") ChartsTab.drawScenarioA(results);
    else if (which === "B") ChartsTab.drawScenarioB(results);
    else ChartsTab.drawScenarioC(results);
  };

  ChartsTab.drawScenarioA = function (results) {
    const rows = results.rows.filter((r) => r.scenario === "A");
    const agg = ChartsTab.aggregate(rows, "filter", "resolution");
    const labels = [...new Set(rows.map((r) => r.resolution))].sort((a, b) => a - b);

    const timeDatasets = [];
    const spDatasets = [];
    for (const [fname, stats] of agg.entries()) {
      const color = COLORS[fname] || PRIMARY;
      timeDatasets.push({
        label: `${fname} (Tp)`,
        data: labels.map((v) => (stats.has(v) ? Number(stats.get(v).Tp.toFixed(4)) : null)),
        borderColor: color,
        backgroundColor: (ctx) => areaFill(ctx, color),
        fill: true,
        borderWidth: 2.2,
        pointRadius: 4,
        tension: TENSION,
      });
      timeDatasets.push({
        label: `${fname} (Ts)`,
        data: labels.map((v) => (stats.has(v) ? Number(stats.get(v).Ts.toFixed(4)) : null)),
        borderColor: color,
        borderDash: [5, 4],
        borderWidth: 1.5,
        pointRadius: 0,
        tension: TENSION,
      });
      spDatasets.push({
        label: fname,
        data: labels.map((v) => (stats.has(v) ? Number(stats.get(v).S.toFixed(3)) : null)),
        borderColor: color,
        backgroundColor: (ctx) => areaFill(ctx, color),
        fill: true,
        borderWidth: 2.2,
        pointRadius: 4,
        pointStyle: "triangle",
        tension: TENSION,
      });
    }

    ChartsTab.attachChart("chart-a-time", "line", { labels, datasets: timeDatasets }, {
      yTitle: "Waktu (detik)", xTitle: "Resolusi (px)",
    });
    ChartsTab.attachChart("chart-a-speedup", "line", { labels, datasets: spDatasets }, {
      yTitle: "Speedup (S)", xTitle: "Resolusi (px)",
    });
  };

  ChartsTab.drawScenarioB = function (results) {
    const rows = results.rows.filter((r) => r.scenario === "B");
    if (!rows.length) {
      const wrap = $("plot-wrap-b");
      if (wrap) wrap.hidden = true;
      $("plot-empty").hidden = false;
      $("plot-empty").textContent = "Data Skenario B belum tersedia dalam berkas hasil pengujian.";
      return;
    }
    const labels = [...new Set(rows.map((r) => r.p))].sort((a, b) => a - b);
    const agg = ChartsTab.aggregate(rows, "filter", "p");

    const datasets = [
      {
        label: "Linier Ideal (S = P)",
        data: labels.map(Number),
        borderColor: GRAY,
        borderDash: [2, 3],
        borderWidth: 1.2,
        pointRadius: 0,
      },
    ];
    for (const [fname, stats] of agg.entries()) {
      const color = COLORS[fname] || PRIMARY;
      datasets.push({
        label: `Empiris ${fname}`,
        data: labels.map((p) => Number(stats.get(p).S.toFixed(3))),
        borderColor: color,
        backgroundColor: (ctx) => areaFill(ctx, color),
        fill: true,
        borderWidth: 2.2,
        pointRadius: 4.5,
        tension: TENSION,
      });
    }

    ChartsTab.attachChart("chart-b", "line", { labels, datasets }, {
      yTitle: "Speedup (S)", xTitle: "Jumlah Worker Proses (P)",
    });
  };

  ChartsTab.drawScenarioC = function (results) {
    const rows = results.rows.filter((r) => r.scenario === "C");
    const prefers = ["Grayscale", "Gaussian Blur", "Sobel"];
    const filters = [...new Set(rows.map((r) => r.filter))]
      .sort((a, b) => { // reindex sesuai urutan konvensional
        const ia = prefers.indexOf(a), ib = prefers.indexOf(b);
        return (ia < 0 ? 9 : ia) - (ib < 0 ? 9 : ib);
      });
    if (!filters.length) {
      const wrap = $("plot-wrap-c");
      if (wrap) wrap.hidden = true;
      $("plot-empty").hidden = false;
      $("plot-empty").textContent = "Data Skenario C belum tersedia dalam berkas hasil pengujian.";
      return;
    }

    const speedups = filters.map((f) => {
      const list = rows.filter((r) => r.filter === f);
      return list.reduce((s, r) => s + r.speedup, 0) / list.length;
    });
    const efficiencies = filters.map((f) => {
      const list = rows.filter((r) => r.filter === f);
      return list.reduce((s, r) => s + r.efficiency, 0) / list.length;
    });
    const barColors = filters.map((f) => COLORS[f] || PRIMARY);

    ChartsTab.attachChart("chart-c-speedup", "bar", {
      labels: filters,
      datasets: [{
        label: "Speedup (S)",
        data: speedups.map((v) => Number(v.toFixed(3))),
        backgroundColor: barColors,
        borderRadius: 8,
        borderSkipped: false,
        maxBarThickness: 64,
      }],
    }, { yTitle: "Speedup (S)", xTitle: "Filter" });

    ChartsTab.attachChart("chart-c-eff", "bar", {
      labels: filters,
      datasets: [{
        label: "Efisiensi (%)",
        data: efficiencies.map((v) => Number(v.toFixed(2))),
        backgroundColor: barColors,
        borderRadius: 8,
        borderSkipped: false,
        maxBarThickness: 64,
      }],
    }, { yTitle: "Efisiensi (%)", xTitle: "Filter" });
  };

  /* --------------------------------------------------- helper chart */
  ChartsTab.attachChart = function (canvasId, type, data, opt = {}) {
    const options = baseOptions();
    if (opt.yTitle) options.scales.y.title.text = opt.yTitle;
    if (opt.xTitle) options.scales.x.title.text = opt.xTitle;
    if (opt.yMax && Number.isFinite(opt.yMax)) options.scales.y.max = opt.yMax + 0.001;

    ChartsTab.destroy(canvasId);
    const canvas = $(canvasId);
    if (!canvas || typeof window.Chart === "undefined") return;
    ChartsTab.charts[canvasId] = new window.Chart(canvas, { type, data, options });
  };

  ChartsTab.destroy = function (canvasId) {
    if (ChartsTab.charts[canvasId]) {
      ChartsTab.charts[canvasId].destroy();
      delete ChartsTab.charts[canvasId];
    }
  };

  window.ChartsTab = ChartsTab;
})();

/* ==========================================================================
   ArchTab - Tab 4: Arsitektur Sistem (grafik utilisasi per-core + FAQ)
   ========================================================================== */
(function () {
  "use strict";

  const ArchTab = { booted: false, chart: null };
  const $ = (id) => App.el(id);

  ArchTab.init = async function () {
    ArchTab.booted = true;
    await ArchTab.refresh();
  };

  ArchTab.refresh = async function () {
    try {
      const res = await App.api("/api/system/cpu-utilization");
      const labels = res.cores.map((c) => `${c.core} (${c.role})`);
      const data = res.cores.map((c) => Number(c.percent.toFixed(1)));
      const colors = res.cores.map((c) => (c.role === "P-Core" ? "#1E40AF" : "#7C3AED"));

      if (ArchTab.chart) ArchTab.chart.destroy();
      if (typeof window.Chart === "undefined") {
        console.error("Chart.js tidak tersedia (vendor offline gagal dimuat).");
        return;
      }
      ArchTab.chart = new window.Chart($("arch-cpu-chart"), {
        type: "bar",
        data: {
          labels,
          datasets: [{ label: "Utilisasi (%)", data, backgroundColor: colors, borderRadius: 6, borderSkipped: false, maxBarThickness: 34 }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: { ticks: { color: "#0F172A", font: { size: 10 } } },
            y: {
              beginAtZero: true,
              suggestedMax: 100,
              ticks: { color: "#0F172A", font: { size: 10 } },
              title: { display: true, text: "Utilisasi (%)", color: "#0F172A", font: { size: 10, weight: "bold" } },
            },
          },
        },
      });
    } catch (err) {
      console.error("Gagal memuat utilisasi CPU:", err);
    }
  };

  window.ArchTab = ArchTab;
})();

/* ==========================================================================
   RefreshBridge - menghubungkan tombol "Segarkan Grafik" (Tab Benchmark)
   dengan pemuatan ulang data hasil + re-render seluruh grafik analisis.
   ========================================================================== */
(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById("bench-chart-refresh");
    if (!btn) return;
    btn.addEventListener("click", async () => {
      btn.disabled = true;
      try {
        if (window.BenchTab && window.BenchTab.booted) await window.BenchTab.loadResults();
        if (window.ChartsTab) await window.ChartsTab.refreshData();
      } catch (err) {
        console.error("Gagal menyegarkan data grafik:", err);
      } finally {
        btn.disabled = false;
      }
    });
  });
})();
