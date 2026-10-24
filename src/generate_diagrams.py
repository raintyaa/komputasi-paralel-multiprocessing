"""
generate_diagrams.py
====================
Menghasilkan Gambar 1 (Arsitektur Pemrosesan Paralel) dan Gambar 2 (Bagan Alir Penelitian)
dengan standar visual publikasi ilmiah: resolusi tinggi (300 DPI, lebar >= 1600 px),
latar belakang terang/putih, panah alir tajam, dan 100% selaras dengan narasi metodologi.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

PLOTS_DIR = Path("results/plots")
PLOTS_DIR.mkdir(parents=True, exist_ok=True)


def draw_gambar_1():
    """
    Gambar 1: Arsitektur Sistem Pemrosesan Citra Paralel dengan Dekomposisi Horizontal
    dan Manajemen Boundary Halo Padding (k=1).
    """
    fig, ax = plt.subplots(figsize=(10, 13), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 130)
    ax.axis("off")

    # Styling helper
    box_props = dict(boxstyle="round,pad=0.5", facecolor="#F8FAFC", edgecolor="#334155", linewidth=1.5)
    accent_box = dict(boxstyle="round,pad=0.5", facecolor="#EFF6FF", edgecolor="#2563EB", linewidth=1.5)
    worker_box = dict(boxstyle="round,pad=0.4", facecolor="#F0FDF4", edgecolor="#16A34A", linewidth=1.4)
    timer_box = dict(boxstyle="round,pad=0.4", facecolor="#FEF3C7", edgecolor="#D97706", linewidth=1.4)
    term_box = dict(boxstyle="round,pad=0.5", facecolor="#E2E8F0", edgecolor="#1E293B", linewidth=2.0)

    # 1. Mulai
    ax.text(50, 124, "Mulai", ha="center", va="center", fontsize=11, fontweight="bold",
            color="#0F172A", bbox=term_box)

    # Panah 1
    ax.annotate("", xy=(50, 117), xytext=(50, 121),
                arrowprops=dict(arrowstyle="-|>", color="#1E293B", lw=1.5, mutation_scale=12))

    # 2. Citra Masukan
    ax.text(50, 113, "Citra Masukan $I(x, y)$ [Dimensi $H \\times W$, RGB]\n(Larik NumPy C-Contiguous di Memori Utama)",
            ha="center", va="center", fontsize=9.5, fontweight="bold", color="#1E293B", bbox=box_props)

    # Panah 2
    ax.annotate("", xy=(50, 106), xytext=(50, 109),
                arrowprops=dict(arrowstyle="-|>", color="#1E293B", lw=1.5, mutation_scale=12))

    # 3. Start Timer
    ax.text(50, 103, "Mulai Timer Komputasi Murni: $t_{start} = \\mathrm{time.perf\\_counter()}$",
            ha="center", va="center", fontsize=9, fontweight="bold", color="#92400E", bbox=timer_box)

    # Panah 3
    ax.annotate("", xy=(50, 96), xytext=(50, 100),
                arrowprops=dict(arrowstyle="-|>", color="#1E293B", lw=1.5, mutation_scale=12))

    # 4. Dekomposisi Horizontal & Boundary Halo Padding
    ax.text(50, 91, "Dekomposisi Baris Horizontal & Penambahan Boundary Halo ($k=1$)\n"
                    "Pembagian $P$ Sub-matriks dengan Irisan Batas Tepi:\n"
                    "• Sub-blok 1: Baris $0$ s.d. $(H/P) + 1$ (Padding Bawah)\n"
                    "• Sub-blok $i$: Baris $(i-1)\\frac{H}{P} - 1$ s.d. $i\\frac{H}{P} + 1$ (Padding Atas & Bawah)\n"
                    "• Sub-blok $P$: Baris $(P-1)\\frac{H}{P} - 1$ s.d. $H$ (Padding Atas)",
            ha="center", va="center", fontsize=8.5, color="#1E3A8A", bbox=accent_box)

    # Distribusi Panah ke Worker Pool
    y_split = 81
    ax.annotate("", xy=(50, y_split), xytext=(50, 83.5),
                arrowprops=dict(arrowstyle="-", color="#2563EB", lw=1.5))
    ax.plot([18, 82], [y_split, y_split], color="#2563EB", lw=1.5)

    # Workers
    worker_x = [18, 39, 61, 82]
    worker_labels = [
        "Worker 1\n(Konvolusi Sub-blok 1\n+ Halo Bawah)",
        "Worker 2\n(Konvolusi Sub-blok 2\n+ Halo Atas-Bawah)",
        "Worker ...\n(Konvolusi Sub-blok ...\n+ Halo Atas-Bawah)",
        "Worker P\n(Konvolusi Sub-blok P\n+ Halo Atas)"
    ]

    for wx, wlabel in zip(worker_x, worker_labels):
        ax.annotate("", xy=(wx, 73), xytext=(wx, y_split),
                    arrowprops=dict(arrowstyle="-|>", color="#2563EB", lw=1.5, mutation_scale=10))
        ax.text(wx, 67, wlabel, ha="center", va="center", fontsize=7.8, fontweight="bold",
                color="#14532D", bbox=worker_box)
        # Panah ke pemangkasan halo
        ax.annotate("", xy=(wx, 56), xytext=(wx, 61),
                    arrowprops=dict(arrowstyle="-|>", color="#16A34A", lw=1.5, mutation_scale=10))

    # 5. Pemotongan Boundary Halo (Discard Halo)
    ax.text(50, 52, "Pemotongan Baris Batas (Discard Halo Padding $k=1$)\n"
                    "Setiap Worker Menghapus Lapisan Halo Tambahan dari Hasil Konvolusi",
            ha="center", va="center", fontsize=9, fontweight="bold", color="#15803D", bbox=box_props)

    # Penggabungan Panah dari Discard Halo
    for wx in worker_x:
        ax.plot([wx, wx], [56, 56], color="#16A34A", lw=1.5)

    # Panah ke np.vstack
    ax.annotate("", xy=(50, 43), xytext=(50, 48),
                arrowprops=dict(arrowstyle="-|>", color="#1E293B", lw=1.5, mutation_scale=12))

    # 6. Rekonstruksi Matriks (np.vstack)
    ax.text(50, 39, "Rekonstruksi Matriks Citra Utuh:\n$I'(x, y) = \\mathrm{np.vstack}([hasil_1, hasil_2, \\dots, hasil_P])$",
            ha="center", va="center", fontsize=9.5, fontweight="bold", color="#1E293B", bbox=box_props)

    # Panah ke Stop Timer
    ax.annotate("", xy=(50, 31), xytext=(50, 34.5),
                arrowprops=dict(arrowstyle="-|>", color="#1E293B", lw=1.5, mutation_scale=12))

    # 7. Stop Timer
    ax.text(50, 27.5, "Pencatatan Waktu Selesai (Stop Timer):\n$T_{paralel} = \\mathrm{time.perf\\_counter()} - t_{start}$",
            ha="center", va="center", fontsize=9, fontweight="bold", color="#92400E", bbox=timer_box)

    # Panah ke Validasi & Keluaran
    ax.annotate("", xy=(50, 19.5), xytext=(50, 23.5),
                arrowprops=dict(arrowstyle="-|>", color="#1E293B", lw=1.5, mutation_scale=12))

    # 8. Keluaran
    ax.text(50, 15.5, "Citra Hasil Pemrosesan Paralel $I'(x, y)$ [$H \\times W$]\n& Logging Metrik (Speedup, Efisiensi, Overhead, %CPU)",
            ha="center", va="center", fontsize=9, color="#1E293B", bbox=box_props)

    # Panah ke Selesai
    ax.annotate("", xy=(50, 7.5), xytext=(50, 11.5),
                arrowprops=dict(arrowstyle="-|>", color="#1E293B", lw=1.5, mutation_scale=12))

    # 9. Selesai
    ax.text(50, 4.5, "Selesai", ha="center", va="center", fontsize=11, fontweight="bold",
            color="#0F172A", bbox=term_box)

    output_path = PLOTS_DIR / "gambar_1_arsitektur_paralel.png"
    plt.tight_layout()
    fig.savefig(output_path, dpi=300, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    print(f"[+] Berhasil membuat Gambar 1: {output_path.resolve()}")


def draw_gambar_2():
    """
    Gambar 2: Bagan Alir Metodologi Penelitian 6 Tahap
    dengan Verifikasi Keidentikan Bit-Identik dan Resolusi Tinggi.
    """
    fig, ax = plt.subplots(figsize=(10, 14), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 140)
    ax.axis("off")

    # Styling helper
    term_box = dict(boxstyle="round,pad=0.5", facecolor="#E2E8F0", edgecolor="#1E293B", linewidth=2.0)
    stage_box = dict(boxstyle="round,pad=0.5", facecolor="#F8FAFC", edgecolor="#334155", linewidth=1.5)
    decision_box = dict(boxstyle="round4,pad=0.5", facecolor="#FEF3C7", edgecolor="#D97706", linewidth=1.8)
    highlight_box = dict(boxstyle="round,pad=0.5", facecolor="#EFF6FF", edgecolor="#2563EB", linewidth=1.5)

    # 1. Mulai
    ax.text(50, 134, "Mulai", ha="center", va="center", fontsize=11, fontweight="bold",
            color="#0F172A", bbox=term_box)

    # Panah
    ax.annotate("", xy=(50, 126), xytext=(50, 131),
                arrowprops=dict(arrowstyle="-|>", color="#1E293B", lw=1.5, mutation_scale=12))

    # Tahap 1
    ax.text(50, 121, "Tahap 1: Studi Literatur & Formulasi Teori\n"
                    "• Teori Komputasi Paralel & Batasan Global Interpreter Lock (GIL)\n"
                    "• Pengalamatan Memori Larik NumPy & Arsitektur Multiprocessing\n"
                    "• Formulasi Matematis Konvolusi Spasial 2D (Grayscale, Gaussian Blur, Sobel)",
            ha="center", va="center", fontsize=8.5, color="#1E293B", bbox=stage_box)

    ax.annotate("", xy=(50, 112), xytext=(50, 115.5),
                arrowprops=dict(arrowstyle="-|>", color="#1E293B", lw=1.5, mutation_scale=12))

    # Tahap 2
    ax.text(50, 107, "Tahap 2: Perancangan & Pengkodean Algoritma\n"
                    "• Implementasi Baseline Serial Tunggal (NumPy murni)\n"
                    "• Implementasi Paralel (Dekomposisi Horizontal + Boundary Halo Padding)\n"
                    "• Integrasi Pre-warmed Worker Pool (P = 2, 4, 8) & CPUMonitor Background",
            ha="center", va="center", fontsize=8.5, color="#1E293B", bbox=stage_box)

    ax.annotate("", xy=(50, 98), xytext=(50, 101.5),
                arrowprops=dict(arrowstyle="-|>", color="#1E293B", lw=1.5, mutation_scale=12))

    # Tahap 3
    ax.text(50, 93, "Tahap 3: Penyiapan Dataset Citra Uji Master\n"
                    "• Standardisasi 1 Citra Acuan Master Fotografi 4K (4096 × 4096 px)\n"
                    "• Pemotongan Terpusat (Center-Crop) ke 512, 1024, 2048, 4096 px\n"
                    "• Meniadakan Variabilitas Tekstur (Data-Independent Matrix Operations)",
            ha="center", va="center", fontsize=8.5, color="#1E293B", bbox=stage_box)

    ax.annotate("", xy=(50, 84), xytext=(50, 87.5),
                arrowprops=dict(arrowstyle="-|>", color="#1E293B", lw=1.5, mutation_scale=12))

    # Tahap 4
    ax.text(50, 77, "Tahap 4: Eksekusi Eksperimen Terkontrol (810 Run)\n"
                    "• Skenario A: Variasi Resolusi (512–4096 px, P = 4, 30 Repetisi)\n"
                    "• Skenario B: Skalabilitas Worker (P = 1, 2, 4, 8 @ 2048 px, 30 Repetisi)\n"
                    "• Skenario C: Kompleksitas Komputasi (P = 4 @ 2048 px, 30 Repetisi)\n"
                    "• Pengukuran Interleaved Serial-Paralel Segar & Cool-down Buffer CPU",
            ha="center", va="center", fontsize=8.5, color="#1E3A8A", bbox=highlight_box)

    ax.annotate("", xy=(50, 67), xytext=(50, 70),
                arrowprops=dict(arrowstyle="-|>", color="#1E293B", lw=1.5, mutation_scale=12))

    # Decision: Verifikasi Bit-Identik
    ax.text(50, 61, "Verifikasi Bit-Identik\nSerial vs Paralel\n($\\Delta_{\\max} = 0.000000$)?",
            ha="center", va="center", fontsize=8.5, fontweight="bold", color="#92400E", bbox=decision_box)

    # Percabangan Tidak
    ax.plot([72, 88, 88], [61, 61, 107], color="#DC2626", lw=1.5)
    ax.annotate("", xy=(73, 107), xytext=(88, 107),
                arrowprops=dict(arrowstyle="-|>", color="#DC2626", lw=1.5, mutation_scale=12))
    ax.text(80, 62.5, "Tidak (Gagal)", ha="center", va="bottom", fontsize=8, fontweight="bold", color="#DC2626")
    ax.text(89, 84, "Koreksi Padding Halo\n& Sinkronisasi Worker", ha="left", va="center", fontsize=7.5, color="#DC2626")

    # Percabangan Ya
    ax.annotate("", xy=(50, 50), xytext=(50, 55),
                arrowprops=dict(arrowstyle="-|>", color="#16A34A", lw=1.5, mutation_scale=12))
    ax.text(51.5, 52.5, "Ya (100% Identik)", ha="left", va="center", fontsize=8, fontweight="bold", color="#16A34A")

    # Tahap 5
    ax.text(50, 44, "Tahap 5: Pencatatan & Kalkulasi Parameter Kinerja\n"
                    "• Durasi Komputasi Murni ($T_{serial}$, $T_{paralel}$ via time.perf_counter)\n"
                    "• Kalkulasi Speedup ($S = T_s / T_p$), Efisiensi ($E = S / P \\times 100\\%$)\n"
                    "• Overhead Paralel ($T_{overhead} = T_p - T_s/P$) & Pemanfaatan CPU (psutil)",
            ha="center", va="center", fontsize=8.5, color="#1E293B", bbox=stage_box)

    ax.annotate("", xy=(50, 35), xytext=(50, 38.5),
                arrowprops=dict(arrowstyle="-|>", color="#1E293B", lw=1.5, mutation_scale=12))

    # Tahap 6
    ax.text(50, 26, "Tahap 6: Analisis Skalabilitas & Penarikan Kesimpulan\n"
                    "• Evaluasi Kurva Percepatan Empiris terhadap Batas Hukum Amdahl\n"
                    "• Estimasi Fraksi Paralel ($f = 0.69 - 0.79$) & Diagnostik Karp–Flatt\n"
                    "• Analisis Korelasi Beban Filter vs Overhead & Utilisasi CPU\n"
                    "• Evaluasi Hipotesis Cache Locality & Perumusan Rekomendasi",
            ha="center", va="center", fontsize=8.5, color="#1E293B", bbox=stage_box)

    ax.annotate("", xy=(50, 15), xytext=(50, 18.5),
                arrowprops=dict(arrowstyle="-|>", color="#1E293B", lw=1.5, mutation_scale=12))

    # Output Laporan
    ax.text(50, 11, "Penyusunan Hasil Pembahasan & Laporan Tugas Akhir",
            ha="center", va="center", fontsize=9, fontweight="bold", color="#1E293B", bbox=stage_box)

    ax.annotate("", xy=(50, 5), xytext=(50, 8),
                arrowprops=dict(arrowstyle="-|>", color="#1E293B", lw=1.5, mutation_scale=12))

    # Selesai
    ax.text(50, 2.5, "Selesai", ha="center", va="center", fontsize=11, fontweight="bold",
            color="#0F172A", bbox=term_box)

    output_path = PLOTS_DIR / "gambar_2_bagan_alir_penelitian.png"
    plt.tight_layout()
    fig.savefig(output_path, dpi=300, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    print(f"[+] Berhasil membuat Gambar 2: {output_path.resolve()}")


if __name__ == "__main__":
    draw_gambar_1()
    draw_gambar_2()
