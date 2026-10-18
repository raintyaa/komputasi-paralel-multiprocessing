/* ==========================================================================
   app.js - State manager global & navigasi rail Parallel Vision Workbench
   Tanggung jawab:
   1. Menyimpan state aplikasi (spesifikasi sistem, konfigurasi, hasil).
   2. Navigasi rail kiri (live, benchmark, analysis, arch) - klik + keyboard
      penuh (ArrowUp/Down/Left/Right, Home, End) sesuai pola ARIA tablist.
   3. Indikator status run global di footer rail (App.setRunStatus).
   4. Inisialisasi modul lain (LiveTab, BenchTab, ChartsTab, ArchTab) saat
      pertama kali panel terkait diaktifkan.
   Catatan: id elemen (#tab-btn-*, #chip-*, #arch-*) dipertahankan persis
   karena seluruh listener modul lain bergantung padanya.
   ========================================================================== */
(function () {
  "use strict";

  const TAB_IDS = ["live", "benchmark", "analysis", "arch"];

  const App = {
    state: {
      specs: null,        // {cpu_model, physical_cores, logical_threads, ...}
      liveConfig: null,   // {resolutions, workers, filters[...]}
      benchConfig: null,  // {bases, modes, scenarios, dataset_counts}
      results: null,      // hasil benchmark terakhir (rows, count)
      chartsBuilt: false,
      lastLiveRun: null,  // hasil POST /api/live/process terakhir
    },
    activeTab: "live",

    /* ---------------------- util fetch ---------------------- */
    async api(path, options = {}) {
      const res = await fetch(path, {
        headers: { "Content-Type": "application/json" },
        ...options,
      });
      if (!res.ok) {
        let detail = `${res.status} ${res.statusText}`;
        try {
          const body = await res.json();
          if (body && body.detail) detail = body.detail;
        } catch (_) { /* ignore */ }
        throw new Error(detail);
      }
      return res.json();
    },

    fmt(value, digits = 4, suffix = "s") {
      return `${Number(value).toFixed(digits)}${suffix}`;
    },

    el(id) {
      return document.getElementById(id);
    },

    icon(name) {
      return window.Icon ? window.Icon.get(name) : "";
    },

    /**
     * Tulis teks ke dalam label tombol/tautan tanpa menghapus ikon SVG-nya.
     * Tombol yang punya <span class="btn-label"> memakai span tersebut;
     * bila tidak ada (mis. tombol polos), jatuh ke textContent biasa.
     */
    setBtnLabel(id, text) {
      const node = this.el(id);
      if (!node) return;
      const label = node.querySelector(".btn-label");
      if (label) label.textContent = text;
      else node.textContent = text;
    },

    /**
     * Indikator status run global di footer rail.
     * @param {"ready"|"running"|"warning"|"error"} state
     * @param {string} text
     */
    setRunStatus(state, text) {
      const box = this.el("rail-status");
      const label = this.el("run-status-text");
      if (label && typeof text === "string") label.textContent = text;
      if (box && state) box.setAttribute("data-state", state);
    },

    /* ---------------------- sistem ---------------------- */
    async loadSpecs() {
      const { specs } = await this.api("/api/system/specs");
      this.state.specs = specs;

      // Isi chip telemetri rail; nilai panjang diberi title agar tetap terbaca
      // penuh saat terpotong ellipsis di rail selebar 240px.
      const fill = (id, text, title) => {
        const node = this.el(id);
        if (!node) return;
        node.textContent = text;
        node.title = title || text;
      };
      fill("chip-cpu", specs.cpu_model);
      fill("chip-cores", `${specs.physical_cores} Core / ${specs.logical_threads} Utas`);
      fill("chip-ram", `${specs.ram_total_gb} GB`);
      fill("chip-dataset", `${specs.dataset_images} Citra PNG`);
      fill("arch-threads", `${specs.logical_threads}`);
      fill("arch-pcores", "4 Performance-Cores");
      fill("arch-ecores", "4 Efficient-Cores");
      fill("arch-ram", `${specs.ram_total_gb} GB RAM`);

      this.setRunStatus("ready", "Deterministic Engine Ready");
      return specs;
    },

    /* ---------------------- navigasi rail ---------------------- */
    switchTab(tabId) {
      if (!TAB_IDS.includes(tabId)) return;
      this.activeTab = tabId;
      TAB_IDS.forEach((id) => {
        const btn = this.el(`tab-btn-${id}`);
        const panel = this.el(`tab-${id}`);
        if (!btn || !panel) return;
        const on = id === tabId;
        btn.classList.toggle("is-active", on);
        btn.setAttribute("aria-selected", on ? "true" : "false");
        btn.tabIndex = on ? 0 : -1;
        panel.classList.toggle("is-active", on);
        if (on) panel.hidden = false;
      });
      // Bootstrap modul hari pertama kali panel dibuka.
      if (tabId === "live" && window.LiveTab && !window.LiveTab.booted) window.LiveTab.init();
      if (tabId === "benchmark" && window.BenchTab && !window.BenchTab.booted) window.BenchTab.init();
      if (tabId === "analysis" && window.ChartsTab && !window.ChartsTab.booted) window.ChartsTab.init();
      if (tabId === "arch" && window.ArchTab && !window.ArchTab.booted) window.ArchTab.init();
    },

    bindTabs() {
      TAB_IDS.forEach((id, i) => {
        const btn = this.el(`tab-btn-${id}`);
        if (!btn) return;
        btn.addEventListener("click", () => this.switchTab(id));
        btn.addEventListener("keydown", (e) => {
          const step = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 };
          let next = null;
          if (e.key in step) next = TAB_IDS[(i + step[e.key] + TAB_IDS.length) % TAB_IDS.length];
          else if (e.key === "Home") next = TAB_IDS[0];
          else if (e.key === "End") next = TAB_IDS[TAB_IDS.length - 1];
          if (!next) return;
          e.preventDefault();
          this.switchTab(next);
          const nb = this.el(`tab-btn-${next}`);
          if (nb) nb.focus();
        });
      });
    },

    /* ---------------------- sub-tab ---------------------- */
    bindSubTabs(rootEl) {
      const btns = Array.from(rootEl.querySelectorAll(".sub-tab-btn"));
      if (!btns.length) return;

      const groups = {};
      btns.forEach((b) => {
        const key = b.dataset.group || "default";
        (groups[key] = groups[key] || []).push(b);
      });

      const activate = (btn) => {
        const list = groups[btn.dataset.group || "default"] || [];
        list.forEach((b) => {
          const on = b === btn;
          b.classList.toggle("is-active", on);
          b.setAttribute("aria-selected", on ? "true" : "false");
          b.tabIndex = on ? 0 : -1;
          const panel = document.getElementById(b.getAttribute("aria-controls"));
          if (panel) panel.classList.toggle("is-active", on);
        });
      };

      Object.keys(groups).forEach((key) => {
        const list = groups[key];
        list.forEach((btn, i) => {
          btn.addEventListener("click", () => activate(btn));
          btn.addEventListener("keydown", (e) => {
            const step = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 };
            let next = null;
            if (e.key in step) next = list[(i + step[e.key] + list.length) % list.length];
            else if (e.key === "Home") next = list[0];
            else if (e.key === "End") next = list[list.length - 1];
            if (!next) return;
            e.preventDefault();
            activate(next);
            next.focus();
          });
        });
      });
    },

    /* ---------------------- boot ---------------------- */
    async init() {
      Icon.hydrate(document);
      this.bindTabs();
      this.bindSubTabs(document);
      this.switchTab("live");
      try {
        await this.loadSpecs();
      } catch (err) {
        console.error("Spesifikasi tidak tersedia:", err);
        ["chip-cpu", "chip-cores", "chip-ram", "chip-dataset"].forEach((id) => {
          const node = this.el(id);
          if (!node) return;
          node.textContent = "tidak tersedia";
          node.title = "Endpoint /api/system/specs tidak merespons";
        });
        this.setRunStatus("warning", "Backend tidak merespons (spesifikasi gagal dimuat)");
      }
    },
  };

  window.App = App;
  document.addEventListener("DOMContentLoaded", () => App.init());
})();
