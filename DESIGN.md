---
tokens:
  color:
    primary: "#1E40AF"
    primary-hover: "#1E3A8A"
    primary-light: "#EFF6FF"
    accent: "#D97706"
    accent-hover: "#B45309"
    accent-bg: "#FFFBEB"
    accent-border: "#FDE68A"
    canvas: "#F8FAFC"
    surface: "#FFFFFF"
    surface-subtle: "#E9EEF6"
    border: "#DBEAFE"
    border-subtle: "#F1F5F9"
    border-focus: "#1E40AF"
    text-main: "#0F172A"
    text-secondary: "#475569"
    text-muted: "#64748B"
    text-light: "#94A3B8"
    success: "#059669"
    success-bg: "#ECFDF5"
    success-border: "#A7F3D0"
    warning: "#D97706"
    warning-bg: "#FFFBEB"
    warning-border: "#FDE68A"
    danger: "#DC2626"
    danger-bg: "#FEF2F2"
    danger-border: "#FECACA"
  font:
    sans: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    mono: "'JetBrains Mono', 'Fira Code', Menlo, Monaco, Consolas, monospace"
  radius:
    sm: "6px"
    md: "10px"
    lg: "16px"
    card: "20px"
    full: "9999px"
  shadow:
    sm: "0 1px 2px 0 rgba(0, 0, 0, 0.04)"
    card: "0 10px 30px -4px rgba(15, 23, 42, 0.04), 0 2px 8px -2px rgba(15, 23, 42, 0.02)"
    card-hover: "0 20px 35px -5px rgba(15, 23, 42, 0.06), 0 4px 12px -2px rgba(15, 23, 42, 0.03)"
    pill: "0 2px 6px rgba(15, 23, 42, 0.06)"
    nav: "0 4px 20px -2px rgba(15, 23, 42, 0.05)"
---

# Design System: Parallel Vision Workbench

<!-- impeccable:design-schema 1 -->

Dokumen ini mendefinisikan sistem desain visual, arsitektur tata letak, dan spesifikasi komponen untuk aplikasi web **Parallel Vision Workbench** (Laboratorium Komputasi Paralel FMIPA UNTAN).

Arsitektur tata letak mengadopsi prinsip **Milkinside High-Key Futuristic White Dashboard**:
- Permukaan putih taktil berelevasi lembut (*Floating Bento Slabs*).
- Grid modular bernapas dengan *whitespace* proporsional (*Generous Bento-Box Grid*).
- Kontrol berbentuk kapsul melingkar penuh (*Pill-Shaped Capsule Controls*).
- Visualisasi data presisi bergradasi lembut (*Smooth Spline Dataviz*).

---

## 1. Overview

Parallel Vision Workbench memadukan ketegasan riset komputasi paralel akademis dengan keanggunan dasbor eksekutif modern:
- **Clean, Taktil, & Anti-Plain**: Menghindari kesan dokumen putih datar dengan memanfaatkan bayangan difus multi-lapis (*ambient diffused shadows*) di atas kanvas Slate-50 (`#F8FAFC`).
- **Bento-Box Modular Architecture**: Mengorganisasikan parameter eksperimen, telemetri live, matriks komputasi, dan simulator Amdahl ke dalam blok-blok bento mandiri yang bernapas.
- **Hierarki Kognitif Jelas**: Memisahkan secara tegas zona input formulir, visualisasi perbandingan citra, dan pelaporan statistik tanpa sekat garis yang kaku.
- **Tipografi Presisi Tinggi**: Tipografi sans-serif modern dipadukan dengan angka numerik besar bertabular untuk waktu eksekusi presisi tinggi (`perf_counter`) dan selisih piksel absolut $\Delta_{\max} = 0.000000$.

---

## 2. Colors (TETAP & TERKUNCI)

Sistem warna mematuhi rasio kontras WCAG AA (minimal 4.5:1 untuk teks normal, minimal 3:1 untuk teks tebal dan komponen UI).

### 2.1 Palet Utama (Core Palette)
- **Primary / Aksen Utama**: `#1E40AF` (Royal Blue 800). Digunakan untuk navbar monogram, status aktif tab, tombol aksi utama, dan highlight garis grafik serial.
- **Accent / Highlight Data**: `#D97706` (Amber 600). Menandai garis asimtot Amdahl, nilai slider aktif, dan tag header kartu.
- **Canvas / Latar Belakang**: `#F8FAFC` (Slate 50). Memberikan kedalaman dasar yang sejuk, bersih, dan profesional.
- **Surface / Permukaan Kartu**: `#FFFFFF` (Pure White). Digunakan untuk semua kartu bento, panel kontrol, dan kontainer visual.
- **Surface Subtle**: `#E9EEF6` (Muted Blue-Tone). Digunakan untuk latar kapsul segmented control dan selang-seling tabel.
- **Border / Garis Tepi**: `#DBEAFE` (Blue 100). Garis batas ber-tone biru sangat halus (1px solid `rgba(219, 234, 254, 0.7)`).

### 2.2 Warna Teks (Typography Colors)
- **Text Main**: `#0F172A` (Slate 900, Rasio kontras 15.6:1 terhadap putih). Digunakan untuk judul, angka metrik utama, dan label penting.
- **Text Secondary**: `#475569` (Slate 600, Rasio kontras 6.2:1 terhadap putih). Digunakan untuk teks tab inaktif, label parameter, dan subjudul. Memenuhi standar WCAG AA.
- **Text Muted**: `#64748B` (Slate 500). Digunakan untuk caption minor, catatan kaki, dan teks pembantu.

### 2.3 Warna Semantik & Telemetri
- **Success / Status Verifikasi**:
  - Teks/Ikon: `#059669` (Emerald 600) | Latar: `#ECFDF5` | Border: `#A7F3D0`
  - Makna: Verifikasi bit-identik 100% (Δmax = 0.000000), pengujian sukses.
- **Warning / Catatan Khusus**:
  - Teks/Ikon: `#D97706` (Amber 600) | Latar: `#FFFBEB` | Border: `#FDE68A`
  - Makna: Efisiensi komputasi menurun (< 70%), degradasi thread.
- **Danger / Anomali**:
  - Teks/Ikon: `#DC2626` (Red 600) | Latar: `#FEF2F2` | Border: `#FECACA`
  - Makna: Kegagalan proses, selisih piksel terdeteksi.

---

## 3. Typography

Sistem tipografi menggunakan sans-serif sistemik yang bersih dan monospace berpresisi untuk angka metrik.

### 3.1 Font Family
- **Antarmuka Utama (Sans-serif)**: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif`
- **Angka Telemetri & Kode (Monospace)**: `"JetBrains Mono", "Fira Code", Menlo, Monaco, Consolas, monospace` dengan `font-variant-numeric: tabular-nums;`

### 3.2 Skala Tipografi
- **Display / Top Brand**: 1.25rem (20px), Semi-bold (600), line-height 1.2. Varian rail kiri (`.rail-title`): 1.0625rem (17px) agar identitas + badge versi tetap satu blok rapi pada lebar 240px.
- **Heading 1 / Page Title**: 1.5rem (24px), Bold (700), tracking -0.02em.
- **Heading 2 / Section Title**: 1.125rem (18px), Semi-bold (600), text-main.
- **Heading 3 / Card Title**: 1.0rem (16px), Semi-bold (600), text-main.
- **Micro Label / Section Kicker**: 0.6875rem (11px), Semi-bold (600), tracking 0.06em, uppercase, text-muted.
- **Body / Paragraf**: 0.875rem (14px), Regular (400), line-height 1.55.
- **Small / Metadata**: 0.75rem (12px), Regular/Medium (400/500), text-secondary.
- **KPI Metric Value (Angka Kinerja Utama)**: 2.0rem (32px), Bold (700), font monospace tabular.

---

## 4. Layout (MILKINSIDE BENTO-BOX ARCHITECTURE)

Tata letak mengadopsi filosofi Bento-Box Grid asimetris modular dengan pernapasan ruang yang luas.

### 4.1 Sidebar Rail Kiri (Executive Command Rail)
- **Shell dua kolom**: rail tetap `240px` (`--rail-width`) di kiri + area konten `minmax(0, 1fr)`; grid `--rail-width minmax(0, 1fr)`.
- Rail bersifat *sticky* setinggi viewport (`height: 100vh`), latar `#FFFFFF`, batas kanan `1px solid rgba(219, 234, 254, 0.7)`, bayangan melayang difus `box-shadow: var(--shadow-rail)`.
- **Kepala rail**: monogram kapsul berbobot ("PV" Royal Blue) + Nama Aplikasi + badge versi + subjudul institusi.
- **Kaki rail (`.rail-foot`)**: *Telemetry Rows* monospace bertabular — Prosesor, Utas Eksekusi, Memori, Dataset — plus **pill status run global** (radar berdenyut *pulsing live dot*, `data-state` = `ready|running|warning|error`) sebagai satu-satunya permukaan yang mengumumkan status eksekusi panjang.
- Padding internal rail: `1.35rem 1rem`.

### 4.2 Rail Navigation (Vertical Capsule Navigation)
- Navigasi utama berbentuk **daftar kapsul vertikal** di bagian tengah rail (`.rail-nav`, `role="tablist"`), bukan strip horizontal di bawah command bar.
- Empat item modul; setiap item memakai `.tab-btn` (kapsul `border-radius: 14px`) dengan ikon di dalam *icon tile* + label teks.
- **Tab aktif**: latar `#EFF6FF`, teks `#1E40AF`, font-weight 600, **aksen bar kiri 3px** (`inset 3px 0 0 0 #1E40AF`), `box-shadow: var(--shadow-pill)`.
- **Tab inaktif**: latar transparan, warna teks `#475569` (rasio kontras 6.2:1), font-weight 500; hover berlatar `#F8FAFC`.
- Aksesibilitas: `role="tab"` + `aria-selected` + `aria-controls` + roving `tabindex`; navigasi keyboard ArrowUp/Down/Left/Right dan Home/End.
- **Adaptasi lebar <1024px**: rail menyusut menjadi *strip horizontal sticky* di atas area konten; daftar item dapat di-scroll mendatar dengan `scroll-snap-type: x proximity`; baris telemetri disembunyikan (pill status tetap terlihat). Tidak memakai hamburger/drawer off-canvas.

### 4.3 Modular Bento-Box Grid
- **Rasio Pembagian Kolom Dinamis (Tab 1 Live Demo)**:
  - **Kolom Kiri (Control Deck, `minmax(300px, 360px)`)**: Panel kontrol pengaturan sumber citra, filter spasial, dan alokasi worker.
  - **Kolom Kanan (Telemetry & Viewport Deck, `minmax(0, 1fr)`)**: Baris kartu metrik kinerja (KPI Cards) di atas, diikuti viewport matriks citra dan tab perbandingan visual.
  - Pembagian dua kolom baru aktif pada `≥1280px` (`xl:`); di bawahnya kedua deck bertumpuk agar area citra tetap lebar setelah dikurangi rail 240px.
  - Tab 2 (Orkestrator) memakai `minmax(320px, 380px) + minmax(0, 1fr)` sehingga tabel logger 11 kolom mendapat kolom penuh, bukan separuh.
- **Padding Internal Lega (*Breathing Room*)**: Setiap kartu bento memiliki padding internal **24px hingga 28px** (1.5rem–1.75rem) untuk menciptakan kesan mewah dan tidak berdesakan.
- **Integrated Header (Tanpa Garis Potong Abu-abu)**:
  - Dilarang memotong kartu dengan bar abu-abu (`.card-header-bar` konvensional).
  - Header kartu menyatu langsung di dalam body putih: berisi ikon SVG, judul kartu, subjudul penjelasan ringkas, dan tag kategori kapsul melayang di pojok kanan atas.

---

## 5. Elevation & Depth (TACTILE AMBIENT SHADOWS)

Kedalaman visual dibangun menggunakan bayangan difus multi-lapis (*multi-layer ambient soft shadows*), menghasilkan ilusi kartu putih fisik mengambang halus di atas permukaan meja laboratorium.

- **Level 0 (Canvas)**: Background aplikasi `#F8FAFC`.
- **Level 1 (Floating Bento Slabs)**:
  - Background: `#FFFFFF`
  - Border: `1px solid rgba(219, 234, 254, 0.7)` (garis batas ultra-halus)
  - Box Shadow: `0 10px 30px -4px rgba(15, 23, 42, 0.04), 0 2px 8px -2px rgba(15, 23, 42, 0.02)`
  - Hover State: `0 20px 35px -5px rgba(15, 23, 42, 0.06), 0 4px 12px -2px rgba(15, 23, 42, 0.03)`
- **Level 2 (Interactive Capsule Pills & Active Toggles)**:
  - Background: `#FFFFFF`
  - Border: `1px solid rgba(219, 234, 254, 0.8)`
  - Box Shadow: `0 2px 6px rgba(15, 23, 42, 0.06)`
- **Level 3 (Command Navbar & Modal Viewport)**:
  - Box Shadow: `0 4px 20px -2px rgba(15, 23, 42, 0.05)`

---

## 6. Shapes & Radius

Semua sudut komponen diatur membulat halus (*curved elegance*) sesuai estetika Milkinside:
- **Bento Card Slab**: Radius `20px` (`--radius-card`) untuk seluruh kartu utama.
- **Capsule Pills**: Radius penuh `9999px` (`--radius-full`) untuk seluruh tombol segmented, tab, chip status, dan badge verifikasi.
- **Image Viewport Frame**: Radius `16px` (`--radius-lg`) dengan batas halus dan overflow terpotong rapi.
- **Button & Input Fields**: Radius `10px` hingga `9999px`.

---

## 7. Components

### 7.1 Bento Card Container (`.academic-card`)
- Format monolitik putih bersih tanpa sekat header abu-abu.
- Header menyatu dengan struktur:
  ```html
  <div class="card-header-integrated">
    <div class="card-header-left">
      <div class="card-icon-bubble"><svg class="svg-icon">...</svg></div>
      <div>
        <h3 class="card-title">Konfigurasi Parameter Pengujian</h3>
        <p class="card-subtitle">Pilih dataset, filter spasial, dan alokasi prosesor</p>
      </div>
    </div>
    <span class="badge-capsule">Panel Kontrol</span>
  </div>
  ```

### 7.2 KPI Metric Widgets (`.metric-card`)
- Kartu metrik taktil berlatar putih dengan bayangan mikro:
  - Label mikro: `11px`, semi-bold uppercase, `letter-spacing: 0.06em`, warna `#64748B`.
  - Nilai metrik: `32px` (2rem), bold tabular monospace, warna `#0F172A`.
  - Sub-label / Delta Pill: Kapsul kecil di bawah angka (misal: kapsul hijau lembut berlatar `#ECFDF5` bertuliskan `+3.45× Speedup`).

### 7.3 Capsule Segmented Radio (`.segmented`)
- Wadah luar berbentuk kapsul lonjong (`border-radius: 9999px`) berlatar `#EFF6FF` dengan padding 4px.
- Opsi aktif memiliki latar putih murni `#FFFFFF`, teks `#1E40AF`, radius `9999px`, dan bayangan `0 2px 6px rgba(15,23,42,0.06)`.
- Transisi pergeseran mikro 150ms tanpa kedipan.

### 7.4 Verifikasi Bit-Identik Capsule Badge
- Kontainer kapsul elegan berlatar hijau zamrud lembut (`#ECFDF5`), border `1px solid #A7F3D0`, ikon centang ganda, teks hijau `#065F46`, dan pembacaan selisih piksel absolut $\Delta_{\max} = 0.000000$.

### 7.5 Dataviz & Chart.js Styling (Milkinside Spline Area)
- Kurva garis menggunakan spline halus (`tension: 0.4`).
- Area di bawah garis kurva diberi isian gradasi pudar lembut (*vertical linear gradient from color with 0.15 opacity to transparent 0.0 opacity*).
- Garis grid sumbu horizontal/vertikal sangat tipis dan halus (`rgba(226, 232, 240, 0.5)`).
- Titik data (*point hover*) membesar halus dengan pendaran ring putih.

---

## 8. Do's and Don'ts

### DO:
- Pertahankan palet warna Slate-50 dan Pure White yang sudah disetujui tanpa modifikasi hex.
- Terapkan radius 20px pada seluruh kartu utama dan 9999px pada seluruh segmented pills.
- Gunakan bayangan difus ambient berlapis (`box-shadow: var(--shadow-card)`) untuk menghasilkan kedalaman taktil.
- Satukan header kartu ke dalam body putih tanpa garis potong atau bar abu-abu.
- Berikan kurva spline halus dan gradasi pudar pada grafik Chart.js.

### DON'T:
- Jangan mengubah variabel warna di `tokens.css` atau merusak rasio kontras WCAG AA.
- Jangan gunakan border hitam/abu-abu pekat atau bayangan kaku yang membuat kartu terlihat seperti admin panel murahan.
- Jangan memotong kartu dengan strip header horizontal abu-abu (`.card-header-bar` lama).
- Jangan gunakan tombol radio HTML lingkaran biasa; selalu gunakan *capsule pill segmented toggle*.
- Jangan hilangkan cincin fokus aksesibilitas keyboard (`:focus-visible`).
