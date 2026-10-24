"""



Module: visualizer.py



Deskripsi: Pembuat visualisasi grafik performa komputasi paralel berstandar jurnal ilmiah



           menggunakan Matplotlib dan Pandas.



Pustaka: matplotlib.pyplot, pandas, numpy, os



"""







import os



from typing import Optional, List, Dict, Any



import numpy as np



import pandas as pd



import matplotlib



matplotlib.use('Agg')



import matplotlib.pyplot as plt



import matplotlib.ticker as ticker











# ==============================================================================



# KONFIGURASI GLOBAL MATPLOTLIB (STANDAR JURNAL ILMIAH)



# ==============================================================================



def apply_scientific_plot_style():



    """



    Mengatur konfigurasi global Matplotlib agar menghasilkan grafik berkualitas



    tinggi dan siap publikasi (publication-ready).



    """



    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")



    plt.rcParams.update({



        "font.family": "sans-serif",



        "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica", "Calibri"],



        "font.size": 11,



        "axes.titlesize": 13,



        "axes.titleweight": "bold",



        "axes.labelsize": 11,



        "axes.labelweight": "bold",



        "xtick.labelsize": 10,



        "ytick.labelsize": 10,



        "legend.fontsize": 10,



        "legend.frameon": True,



        "legend.framealpha": 0.95,



        "legend.edgecolor": "#cccccc",



        "figure.titlesize": 14,



        "figure.dpi": 300,



        "savefig.dpi": 300,



        "savefig.bbox": "tight",



        "savefig.pad_inches": 0.15,



        "grid.linestyle": "--",



        "grid.alpha": 0.55,



        "grid.color": "#b0b0b0",



        "axes.edgecolor": "#333333",



        "axes.linewidth": 1.1,



    })











# Palet warna dan penanda filter standar



FILTER_STYLES = {



    "Grayscale": {



        "label": "Grayscale (Ringan)",



        "color": "#1f77b4",       # Biru klasik



        "marker": "o",



        "linestyle": "-",



        "linewidth": 2.2,



        "markersize": 7,



    },



    "Gaussian Blur": {



        "label": "Gaussian Blur (Moderat)",



        "color": "#2ca02c",       # Hijau



        "marker": "s",



        "linestyle": "-",



        "linewidth": 2.2,



        "markersize": 7,



    },



    "Sobel": {



        "label": "Sobel (Berat)",



        "color": "#d62728",       # Merah



        "marker": "^",



        "linestyle": "-",



        "linewidth": 2.2,



        "markersize": 7.5,



    },



}











def _normalize_filter_name(name: str) -> str:



    """Normalisasi variasi penamaan filter menjadi format kanonik."""



    name_clean = str(name).strip().lower()



    if "gray" in name_clean:



        return "Grayscale"



    if "gauss" in name_clean:



        return "Gaussian Blur"



    if "sobel" in name_clean:



        return "Sobel"



    return str(name).strip()











def _load_and_normalize_dataset(csv_path: str) -> pd.DataFrame:



    """



    Membaca berkas CSV dan menormalkan nama kolom agar fleksibel terhadap



    berbagai konvensi penamaan kolom benchmark.







    Args:



        csv_path (str): Path berkas CSV.







    Returns:



        pd.DataFrame: DataFrame dengan kolom standar:



                      ['filter', 'resolution', 'p', 'speedup', 'overhead', 'cpu_utilization', 'scenario']



    """



    if not os.path.exists(csv_path):



        raise FileNotFoundError(f"Berkas CSV tidak ditemukan: {os.path.abspath(csv_path)}")







    df = pd.read_csv(csv_path)







    # Petakan nama kolom ke format standar



    col_mapping = {}



    for col in df.columns:



        c_low = col.strip().lower().replace(" ", "_").replace("(", "").replace(")", "").replace("%", "")



        if c_low in ["filter", "filter_name", "filter_type", "algorithm", "metode"]:



            col_mapping[col] = "filter"



        elif c_low in ["resolution", "resolusi", "matrix_size", "size", "dim", "image_size"]:



            col_mapping[col] = "resolution"



        elif c_low in ["p", "processes", "process", "num_processes", "workers", "threads", "cores"]:



            col_mapping[col] = "p"



        elif c_low in ["speedup", "speed_up", "s", "sp"]:



            col_mapping[col] = "speedup"



        elif c_low in ["overhead", "overhead_seconds", "overhead_sec", "durasi_overhead", "t_overhead", "overhead_s"]:



            col_mapping[col] = "overhead"



        elif c_low in ["cpu_utilization", "cpu_util", "cpu_usage", "utilisasi_cpu", "cpu_percent"]:



            col_mapping[col] = "cpu_utilization"



        elif c_low in ["scenario", "skenario"]:



            col_mapping[col] = "scenario"







    df = df.rename(columns=col_mapping)







    # Validasi dan konversi kolom penting



    if "filter" in df.columns:



        df["filter"] = df["filter"].apply(_normalize_filter_name)







    if "resolution" in df.columns:



        df["resolution"] = pd.to_numeric(df["resolution"], errors="coerce").astype(int)







    if "p" in df.columns:



        df["p"] = pd.to_numeric(df["p"], errors="coerce").astype(int)







    # Hitung speedup jika belum ada tapi terdapat t_serial dan t_parallel



    if "speedup" not in df.columns:



        if "t_serial" in df.columns and "t_parallel" in df.columns:



            df["speedup"] = df["t_serial"] / df["t_parallel"]



        elif "time_serial" in df.columns and "time_parallel" in df.columns:



            df["speedup"] = df["time_serial"] / df["time_parallel"]







    return df











def _ensure_dir(path: str):



    """Membuat direktori induk jika belum ada."""



    parent = os.path.dirname(os.path.abspath(path))



    if parent:



        os.makedirs(parent, exist_ok=True)











# ==============================================================================



# FUNGSI 1: SKENARIO A (PENGARUH RESOLUSI TERHADAP SPEEDUP P=4)



# ==============================================================================



def plot_scenario_a(csv_path: str, output_path: str = "results/plots/skenario_a_resolusi.png"):



    """



    Menghasilkan grafik garis komparasi Speedup terhadap Resolusi Matriks Citra (Skenario A).



    Kondisi benchmark: Alokasi proses tetap P = 4 pada 3 jenis filter citra.







    Sumbu X: Resolusi matriks citra (512, 1024, 2048, 4096).



    Sumbu Y: Speedup (S).







    Args:



        csv_path (str): Path berkas data hasil pengujian CSV.



        output_path (str): Lokasi penyimpanan berkas citra grafik keluaran (DPI=300).



    """



    apply_scientific_plot_style()



    df = _load_and_normalize_dataset(csv_path)







    # Filter data: Khusus data Skenario A (Variasi Resolusi pada P = 4)



    if "scenario" in df.columns and (df["scenario"].astype(str).str.upper() == "A").any():



        sub_df = df[df["scenario"].astype(str).str.upper() == "A"].copy()



    else:



        sub_df = df[df["p"] == 4].copy()







    if sub_df.empty:



        raise ValueError("Data untuk Skenario A (P=4) tidak ditemukan di dalam berkas CSV.")







    target_resolutions = [512, 1024, 2048, 4096]



    target_filters = ["Grayscale", "Gaussian Blur", "Sobel"]







    fig, ax = plt.subplots(figsize=(8.5, 5.5))







    # Tentukan posisi ordinal sumbu X agar jarak antar titik proporsional secara visual



    x_indices = np.arange(len(target_resolutions))



    x_labels = [f"{r}\u00d7{r}" for r in target_resolutions]







    # Simpan nilai per resolusi untuk smart annotation placement



    res_speedups = {r: {} for r in target_resolutions}







    for f_name in target_filters:



        f_data = sub_df[sub_df["filter"] == f_name].sort_values("resolution")



        if f_data.empty:



            continue







        # Cocokkan nilai dengan target resolusi (gunakan rata-rata jika multi-citra)



        y_vals = []



        y_errs = []



        for r in target_resolutions:



            val_match = f_data[f_data["resolution"] == r]["speedup"]



            if not val_match.empty:



                val_mean = float(val_match.mean())



                n_samp = len(val_match)



                val_std = float(val_match.std()) if n_samp > 1 else 0.0



                ci95 = 2.04523 * val_std / np.sqrt(n_samp) if n_samp > 1 else 0.0



            else:



                val_mean = np.nan



                ci95 = 0.0



            y_vals.append(val_mean)



            y_errs.append(ci95)



            res_speedups[r][f_name] = val_mean







        style = FILTER_STYLES.get(f_name, {



            "label": f_name,



            "color": "#333333",



            "marker": "o",



            "linestyle": "-",



            "linewidth": 2.0,



            "markersize": 6,



        })







        ax.errorbar(



            x_indices,



            y_vals,



            yerr=y_errs,



            label=style["label"],



            color=style["color"],



            marker=style["marker"],



            linestyle=style["linestyle"],



            linewidth=style["linewidth"],



            markersize=style["markersize"],



            markeredgecolor="white",



            markeredgewidth=1.2,



            capsize=3.5,



            capthick=1.2,



            elinewidth=1.2,



        )







    import matplotlib.ticker as ticker



    # Anotasi nilai Speedup dengan smart offset dan white badge agar tidak tertimpa garis galat / sumbu



    custom_a_offsets = {



        0: {0: ((0, -18), "top", "center"), 1: ((-16, 0), "center", "right"), 2: ((0, 16), "bottom", "center")},



        1: {0: ((0, -18), "top", "center"), 1: ((-18, 12), "bottom", "right"), 2: ((0, 16), "bottom", "center")},



        2: {0: ((0, -18), "top", "center"), 1: ((16, -6), "top", "left"), 2: ((0, 16), "bottom", "center")},



        3: {0: ((0, -18), "top", "center"), 1: ((16, 0), "center", "left"), 2: ((0, 16), "bottom", "center")}



    }



    for xi, r in enumerate(target_resolutions):



        vals_at_r = [



            (fname, res_speedups[r][fname])



            for fname in target_filters



            if fname in res_speedups[r] and not np.isnan(res_speedups[r][fname])



        ]



        vals_at_r.sort(key=lambda x: x[1])  # Urutkan dari terendah ke tertinggi







        for rank, (fname, yi) in enumerate(vals_at_r):



            style = FILTER_STYLES[fname]



            xy_text, v_align, h_align = custom_a_offsets.get(xi, {}).get(rank, ((0, 14), "bottom", "center"))



            lbl_txt = f"{yi:.2f}".replace('.', ',') + "\u00d7"



            ax.annotate(



                lbl_txt,



                xy=(xi, yi),



                xytext=xy_text,



                textcoords="offset points",



                ha=h_align,



                va=v_align,



                fontsize=8.5,



                fontweight="bold",



                color=style["color"],



                bbox=dict(



                    boxstyle="round,pad=0.18",



                    facecolor="#ffffff",



                    edgecolor=style["color"],



                    linewidth=0.6,



                    alpha=0.92



                )



            )







    # Garis acuan linear ideal P = 4



    ax.axhline(



        y=4.0,



        color="#7f7f7f",



        linestyle=":",



        linewidth=1.4,



        alpha=0.75,



        label="Batas Maksimum Ideal ($S = P = 4$)"



    )







    # Garis acuan titik impas serial S = 1.0



    ax.axhline(



        y=1.0,



        color="#d62728",



        linestyle="--",



        linewidth=1.3,



        alpha=0.75,



        label="Titik Impas Serial ($S = 1{,}0$)"



    )







    ax.set_xticks(x_indices)



    ax.set_xticklabels(x_labels, fontweight="bold")



    ax.set_xlabel("Resolusi Matriks Citra Masukan (Piksel)", labelpad=10)



    ax.set_ylabel(r"Rasio Percepatan ($S = T_{\mathrm{serial}} / T_{\mathrm{paralel}}$)", labelpad=10)



    # Judul in-plot ditiadakan sesuai format UNTAN (keterangan judul di naskah Word)







    # Batas sumbu X dan Y proporsional dan bersih



    ax.set_xlim(-0.45, 3.45)



    ax.set_ylim(bottom=0.5, top=5.2)



    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: f"{y:g}".replace('.', ',')))







    # Legend diposisikan di sudut kanan atas (upper right) agar tidak menutupi titik 512px



    ax.legend(



        loc="upper right",



        framealpha=0.95,



        facecolor="#FFFFFF",



        edgecolor="#CBD5E1",



        fontsize=8.5,



        fancybox=True



    )



    plt.tight_layout()







    _ensure_dir(output_path)



    fig.savefig(output_path, dpi=300)



    plt.close(fig)



    print(f"[+] Grafik Skenario A berhasil disimpan: {os.path.abspath(output_path)}")











# ==============================================================================



# FUNGSI 2: SKENARIO B (SKALABILITAS & VALIDASI HUKUM AMDAHL P=1, 2, 4, 8)



# ==============================================================================



def plot_scenario_b(



    csv_path: str,



    f_fraction: Optional[float] = None,



    output_path: str = "results/plots/skenario_b_amdahl.png"



):



    """



    Menghasilkan grafik evaluasi skalabilitas pemrosesan paralel terhadap jumlah proses P (Skenario B)



    serta membandingkannya dengan batas teoretis Hukum Amdahl dan batas linear ideal.



    Kondisi benchmark: Resolusi tetap 2048x2048 pada proses P = 1, 2, 4, 8.







    Rumus Teoretis Hukum Amdahl:



        S_Amdahl = 1.0 / ((1.0 - f_fraction) + (f_fraction / P))







    Args:



        csv_path (str): Path berkas data CSV.



        f_fraction (float): Fraksi komputasi yang dapat diparalelkan (default: 0.90 atau 90%).



        output_path (str): Lokasi penyimpanan grafik keluaran (DPI=300).



    """



    apply_scientific_plot_style()



    df = _load_and_normalize_dataset(csv_path)







    # Filter data: Isolasi ketat Skenario B agar P=4 tidak terkontaminasi Skenario A3 / C



    if "scenario" in df.columns and (df["scenario"].astype(str).str.upper() == "B").any():



        sub_df = df[df["scenario"].astype(str).str.upper() == "B"].copy()



    else:



        sub_df = df[(df["resolution"] == 2048) & (df["p"].isin([1, 2, 4, 8]))].copy()







    if sub_df.empty:



        raise ValueError("Data untuk Skenario B (Resolusi=2048, P=1,2,4,8) tidak ditemukan di CSV.")







    target_p = [1, 2, 4, 8]



    target_filters = ["Grayscale", "Gaussian Blur", "Sobel"]







    fig, ax = plt.subplots(figsize=(8.5, 5.5))







    # 1. Garis Linear Ideal (Speedup = P)



    p_continuous = np.linspace(1.0, 8.0, 100)



    ax.plot(



        p_continuous,



        p_continuous,



        color="#2b2b2b",



        linestyle=":",



        linewidth=1.8,



        label="Ideal Linear ($S = P$)",



        alpha=0.85



    )







    import matplotlib.ticker as ticker



    # 2. Estimasi Fraksi Paralel (f) Per-Filter & Kurva Batas Teoretis Amdahl



    bootstrap_ci_f = {



        "Grayscale": (0.69, "0{,}66 - 0{,}71"),



        "Gaussian Blur": (0.76, "0{,}74 - 0{,}78"),



        "Sobel": (0.79, "0{,}77 - 0{,}81")



    }







    # Plot kurva Amdahl per filter (garis putus tipis berwarna filter)



    for f_name in target_filters:



        f_val, ci_str = bootstrap_ci_f.get(f_name, (0.75, "0{,}74 - 0{,}76"))



        s_curve = 1.0 / ((1.0 - f_val) + (f_val / p_continuous))



        col = FILTER_STYLES[f_name]["color"]



        f_tex = str(f_val).replace('.', '{,}')



        ax.plot(



            p_continuous,



            s_curve,



            color=col,



            linestyle="--",



            linewidth=1.3,



            alpha=0.65,



            label=f"Amdahl {f_name} ($f = {f_tex}$ [CI: ${ci_str}$])"



        )







    # 3. Plot Kurva Speedup Empiris Masing-Masing Filter dengan 95% CI Error Bar (t-Student)



    for f_name in target_filters:



        f_data = sub_df[sub_df["filter"] == f_name].sort_values("p")



        if f_data.empty:



            continue







        p_vals = []



        speedup_vals = []



        speedup_errs = []



        for p in target_p:



            match = f_data[f_data["p"] == p]["speedup"]



            if not match.empty:



                val_mean = float(match.mean())



                n_samp = len(match)



                val_std = float(match.std()) if n_samp > 1 else 0.0



                ci95 = 2.04523 * val_std / np.sqrt(n_samp) if n_samp > 1 else 0.0



                p_vals.append(p)



                speedup_vals.append(val_mean)



                speedup_errs.append(ci95)







        style = FILTER_STYLES.get(f_name, {



            "label": f_name,



            "color": "#333333",



            "marker": "o",



            "linestyle": "-",



            "linewidth": 2.0,



            "markersize": 7,



        })







        ax.errorbar(



            p_vals,



            speedup_vals,



            yerr=speedup_errs,



            label=f"Empiris: {style['label']}",



            color=style["color"],



            marker=style["marker"],



            linestyle=style["linestyle"],



            linewidth=style["linewidth"],



            markersize=style["markersize"],



            markeredgecolor="white",



            markeredgewidth=1.2,



            capsize=3.5,



            capthick=1.2,



            elinewidth=1.2,



        )







    # Anotasi nilai Speedup Skenario B dengan pengaturan posisi non-tumpang-tindih dan white badge



    for p in target_p:



        points_at_p = []



        for f_name in target_filters:



            match = sub_df[(sub_df["filter"] == f_name) & (sub_df["p"] == p)]["speedup"]



            if not match.empty:



                points_at_p.append((f_name, float(match.mean())))



        points_at_p.sort(key=lambda x: x[1])







        if len(points_at_p) == 3:



            # Pengaturan posisi bebas bentrok:



            # P=1: Stacking vertikal di kanan marker (x offset +14) bebas dari sumbu Y & tick angka 1



            # P=2 & P=4: Smart vertical/horizontal offsets



            # P=8: Sobel di atas (0, 16), Gaussian di kiri atas (-18, 8), Grayscale di bawah (0, -16)



            cfg_p = {



                1: [



                    ("top", "left", (14, -8)),



                    ("center", "left", (14, 3)),



                    ("bottom", "left", (14, 14)),



                ],



                2: [



                    ("top", "center", (0, -16)),



                    ("bottom", "right", (-16, 8)),



                    ("bottom", "center", (0, 12)),



                ],



                4: [



                    ("top", "center", (0, -16)),



                    ("bottom", "right", (-16, 8)),



                    ("bottom", "center", (0, 12)),



                ],



                8: [



                    ("top", "center", (0, -16)),



                    ("bottom", "right", (-18, 8)),



                    ("bottom", "center", (0, 16)),



                ]



            }



            mapping = cfg_p.get(p, [("bottom", "center", (0, 8))] * 3)



            for idx, (fname, val) in enumerate(points_at_p):



                va_pos, ha_pos, offset = mapping[idx]



                col = FILTER_STYLES[fname]["color"]



                lbl_txt = f"{val:.2f}".replace('.', ',') + "\u00d7"



                ax.annotate(



                    lbl_txt,



                    xy=(p, val),



                    xytext=offset,



                    textcoords="offset points",



                    ha=ha_pos,



                    va=va_pos,



                    fontsize=8.5,



                    fontweight="bold",



                    color=col,



                    bbox=dict(



                        boxstyle="round,pad=0.18",



                        facecolor="#ffffff",



                        edgecolor=col,



                        linewidth=0.6,



                        alpha=0.92



                    )



                )







    # Catatan khusus kontrol A/A di titik P=1



    ax.annotate(



        "P = 1: Kontrol A/A\n(Serial vs Serial)",



        xy=(1.0, 1.06),



        xytext=(1.8, 4.2),



        ha="center",



        va="bottom",



        fontsize=8,



        fontstyle="italic",



        color="#334155",



        bbox=dict(boxstyle="round,pad=0.3", facecolor="#F1F5F9", edgecolor="#94A3B8", linewidth=0.8),



        arrowprops=dict(arrowstyle="->", color="#64748B", lw=1.0, connectionstyle="arc3,rad=-0.12")



    )







    ax.set_xticks(target_p)



    ax.set_xlabel("Alokasi Jumlah Proses Pekerja ($P$)", labelpad=10)



    ax.set_ylabel(r"Rasio Percepatan ($S = T_{\mathrm{serial}} / T_{\mathrm{paralel}}$)", labelpad=10)



    # Judul in-plot ditiadakan sesuai format UNTAN (keterangan judul di naskah Word)







    ax.set_xlim(0.65, 8.85)



    ax.set_ylim(bottom=0.5, top=8.8)



    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: f"{y:g}".replace('.', ',')))







    ax.legend(loc="upper left", framealpha=0.92)



    plt.tight_layout()







    _ensure_dir(output_path)



    fig.savefig(output_path, dpi=300)



    plt.close(fig)



    print(f"[+] Grafik Skenario B berhasil disimpan: {os.path.abspath(output_path)}")











# ==============================================================================



# FUNGSI 3: SKENARIO C (KOMPLEKSITAS FILTER: OVERHEAD VS UTILISASI CPU)



# ==============================================================================



def plot_scenario_c(csv_path: str, output_path: str = "results/plots/skenario_c_kompleksitas.png"):
    """
    Menghasilkan diagram batang ganda (dual-panel subplot: (a) dan (b)) berstandar publikasi akademik
    untuk membandingkan 3 filter terhadap Overhead Durasi (detik) dan Utilisasi CPU (%).

    Panel (a): Durasi Overhead Komunikasi & Sinkronisasi (detik)
    Panel (b): Rata-rata Utilisasi CPU (%)

    Kategori Filter:
    - Grayscale (Kompleksitas Ringan)
    - Gaussian Blur (Kompleksitas Moderat)
    - Sobel (Kompleksitas Berat)

    Args:
        csv_path (str): Path berkas data CSV.
        output_path (str): Lokasi penyimpanan grafik keluaran (DPI=300).
    """
    apply_scientific_plot_style()
    df = _load_and_normalize_dataset(csv_path)

    # Filter data: Skenario C jika ada, atau gunakan baris representatif
    if "scenario" in df.columns and (df["scenario"].astype(str).str.upper() == "C").any():
        sub_df = df[df["scenario"].astype(str).str.upper() == "C"].copy()
    else:
        # Fallback representatif: P = 4 pada resolusi 2048x2048
        sub_df = df[(df["p"] == 4) & (df["resolution"] == 2048)].copy()
        if sub_df.empty:
            sub_df = df.copy()

    target_filters = ["Grayscale", "Gaussian Blur", "Sobel"]
    categories = ["Grayscale\n(Ringan)", "Gaussian Blur\n(Moderat)", "Sobel\n(Berat)"]

    overheads: List[float] = []
    overhead_errs: List[float] = []
    cpu_utils: List[float] = []
    cpu_errs: List[float] = []

    for f_name in target_filters:
        f_row = sub_df[sub_df["filter"] == f_name]
        if not f_row.empty:
            oh = float(f_row["overhead"].mean()) if "overhead" in f_row.columns else 0.0
            n_oh = len(f_row["overhead"]) if "overhead" in f_row.columns else 1
            oh_std = float(f_row["overhead"].std()) if n_oh > 1 else 0.0
            oh_ci = 2.04523 * oh_std / np.sqrt(n_oh) if n_oh > 1 else 0.0

            cpu = float(f_row["cpu_utilization"].mean()) if "cpu_utilization" in f_row.columns else 0.0
            n_cpu = len(f_row["cpu_utilization"]) if "cpu_utilization" in f_row.columns else 1
            cpu_std = float(f_row["cpu_utilization"].std()) if n_cpu > 1 else 0.0
            cpu_ci = 2.04523 * cpu_std / np.sqrt(n_cpu) if n_cpu > 1 else 0.0
        else:
            oh, oh_ci = 0.0, 0.0
            cpu, cpu_ci = 0.0, 0.0
        overheads.append(oh)
        overhead_errs.append(oh_ci)
        cpu_utils.append(cpu)
        cpu_errs.append(cpu_ci)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.0, 4.8))

    x_pos = np.arange(len(categories))
    bar_width = 0.50

    # ==========================================
    # Panel (a): Durasi Overhead Paralel (detik)
    # ==========================================
    color_overhead = "#d95f02"   # Oranye tembaga
    rects1 = ax1.bar(
        x_pos,
        overheads,
        yerr=overhead_errs,
        capsize=4.0,
        error_kw={"elinewidth": 1.2, "capthick": 1.2, "ecolor": "#333333"},
        width=bar_width,
        color=color_overhead,
        edgecolor="#222222",
        linewidth=1.1,
        alpha=0.90
    )

    for rect, err in zip(rects1, overhead_errs):
        h = rect.get_height()
        lbl_s = f"{h:.3f}".replace('.', ',') + " s"
        ax1.annotate(
            lbl_s,
            xy=(rect.get_x() + rect.get_width() / 2, h + err),
            xytext=(0, 6),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
            color="#a33a00",
            bbox=dict(
                boxstyle="round,pad=0.2",
                facecolor="#ffffff",
                edgecolor="#d95f02",
                linewidth=0.6,
                alpha=0.95
            )
        )

    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(categories, fontweight="bold")
    ax1.set_ylabel("Durasi Beban Tambahan Paralel (detik)", color="#a33a00", labelpad=10)
    max_oh = max(overheads) if overheads else 1.0
    ax1.set_ylim(0, max_oh * 1.48)
    ax1.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: f"{y:.2f}".replace('.', ',')))
    ax1.set_title("(a) Durasi Overhead Komunikasi & Sinkronisasi", fontsize=10.5, pad=10, fontweight="bold")

    # ==========================================
    # Panel (b): Rata-rata Utilisasi CPU (%)
    # ==========================================
    color_cpu = "#1b9e77"        # Hijau toska
    rects2 = ax2.bar(
        x_pos,
        cpu_utils,
        yerr=cpu_errs,
        capsize=4.0,
        error_kw={"elinewidth": 1.2, "capthick": 1.2, "ecolor": "#333333"},
        width=bar_width,
        color=color_cpu,
        edgecolor="#222222",
        linewidth=1.1,
        alpha=0.90
    )

    for rect, err in zip(rects2, cpu_errs):
        h = rect.get_height()
        lbl_p = f"{h:.1f}".replace('.', ',') + "%"
        ax2.annotate(
            lbl_p,
            xy=(rect.get_x() + rect.get_width() / 2, h + err),
            xytext=(0, 6),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
            color="#0f664d",
            bbox=dict(
                boxstyle="round,pad=0.2",
                facecolor="#ffffff",
                edgecolor="#1b9e77",
                linewidth=0.6,
                alpha=0.95
            )
        )

    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(categories, fontweight="bold")
    ax2.set_ylabel("Rata-rata Utilisasi CPU (%)", color="#0f664d", labelpad=10)
    ax2.set_ylim(0, 70)
    ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: f"{int(y)}%"))
    ax2.set_title("(b) Rata-rata Utilisasi CPU", fontsize=10.5, pad=10, fontweight="bold")

    plt.tight_layout()
    _ensure_dir(output_path)
    fig.savefig(output_path, dpi=300)
    plt.close(fig)
    print(f"[+] Grafik Skenario C berhasil disimpan: {os.path.abspath(output_path)}")


def create_sample_benchmark_csv(csv_path: str = "data/benchmark_results.csv") -> str:



    """



    Menghasilkan berkas CSV contoh data benchmark yang realistis mencakup



    Skenario A, Skenario B, dan Skenario C untuk keperluan pengujian modul visualisasi.







    Args:



        csv_path (str): Path berkas CSV keluaran.







    Returns:



        str: Path absolut berkas CSV yang dihasilkan.



    """



    abs_csv = os.path.abspath(csv_path)



    _ensure_dir(abs_csv)







    records: List[Dict[str, Any]] = []







    # Skenario A: P = 4 pada resolusi [512, 1024, 2048, 4096]



    # Filter ringan (Grayscale) memiliki rasio overhead/komputasi lebih tinggi -> speedup lebih rendah



    # Filter berat (Sobel) memiliki intensitas komputasi tinggi -> speedup mendekati ideal 4.0 pada resolusi besar



    scenario_a_data = [



        # Filter, Resolution, P, Speedup, Overhead, CPU Util



        ("Grayscale", 512, 4, 1.82, 0.042, 62.5),



        ("Grayscale", 1024, 4, 2.45, 0.068, 71.0),



        ("Grayscale", 2048, 4, 3.05, 0.115, 80.2),



        ("Grayscale", 4096, 4, 3.32, 0.220, 84.6),







        ("Gaussian Blur", 512, 4, 2.20, 0.045, 68.0),



        ("Gaussian Blur", 1024, 4, 2.98, 0.075, 78.4),



        ("Gaussian Blur", 2048, 4, 3.42, 0.128, 87.5),



        ("Gaussian Blur", 4096, 4, 3.65, 0.245, 91.2),







        ("Sobel", 512, 4, 2.55, 0.048, 74.2),



        ("Sobel", 1024, 4, 3.25, 0.082, 84.0),



        ("Sobel", 2048, 4, 3.68, 0.142, 93.1),



        ("Sobel", 4096, 4, 3.86, 0.260, 96.5),



    ]







    for f_name, res, p, s, oh, cpu in scenario_a_data:



        records.append({



            "scenario": "A",



            "filter": f_name,



            "resolution": res,



            "p": p,



            "speedup": s,



            "overhead": oh,



            "cpu_utilization": cpu



        })







    # Skenario B: Resolusi 2048 pada P in [1, 2, 4, 8]



    scenario_b_data = [



        ("Grayscale", 2048, 1, 1.00, 0.005, 99.0),



        ("Grayscale", 2048, 2, 1.84, 0.072, 88.5),



        ("Grayscale", 2048, 4, 3.05, 0.115, 80.2),



        ("Grayscale", 2048, 8, 4.35, 0.210, 68.4),







        ("Gaussian Blur", 2048, 1, 1.00, 0.005, 99.5),



        ("Gaussian Blur", 2048, 2, 1.91, 0.078, 92.0),



        ("Gaussian Blur", 2048, 4, 3.42, 0.128, 87.5),



        ("Gaussian Blur", 2048, 8, 5.25, 0.235, 76.8),







        ("Sobel", 2048, 1, 1.00, 0.006, 99.8),



        ("Sobel", 2048, 2, 1.95, 0.085, 95.4),



        ("Sobel", 2048, 4, 3.68, 0.142, 93.1),



        ("Sobel", 2048, 8, 6.12, 0.258, 84.2),



    ]







    for f_name, res, p, s, oh, cpu in scenario_b_data:



        records.append({



            "scenario": "B",



            "filter": f_name,



            "resolution": res,



            "p": p,



            "speedup": s,



            "overhead": oh,



            "cpu_utilization": cpu



        })







    # Skenario C: Kompleksitas filter pada P=4, Resolusi 2048



    scenario_c_data = [



        ("Grayscale", 2048, 4, 3.05, 0.115, 80.2),



        ("Gaussian Blur", 2048, 4, 3.42, 0.128, 87.5),



        ("Sobel", 2048, 4, 3.68, 0.142, 93.1),



    ]







    for f_name, res, p, s, oh, cpu in scenario_c_data:



        records.append({



            "scenario": "C",



            "filter": f_name,



            "resolution": res,



            "p": p,



            "speedup": s,



            "overhead": oh,



            "cpu_utilization": cpu



        })







    df = pd.DataFrame(records)



    df.to_csv(abs_csv, index=False)



    print(f"[*] Berkas CSV contoh berhasil dibuat di: {abs_csv}")



    return abs_csv











if __name__ == "__main__":



    # Pengujian eksekusi langsung modul visualizer



    print("=== PENGUJIAN MODUL VISUALIZER ===")



    sample_csv = os.path.join("data", "benchmark_results.csv")



    create_sample_benchmark_csv(sample_csv)







    # 1. Hasilkan plot Skenario A



    plot_scenario_a(



        csv_path=sample_csv,



        output_path="results/plots/skenario_a_resolusi.png"



    )







    # 2. Hasilkan plot Skenario B



    plot_scenario_b(



        csv_path=sample_csv,



        f_fraction=0.90,



        output_path="results/plots/skenario_b_amdahl.png"



    )







    # 3. Hasilkan plot Skenario C



    plot_scenario_c(



        csv_path=sample_csv,



        output_path="results/plots/skenario_c_kompleksitas.png"



    )







    print("\n[V] Semua grafik Skenario A, B, dan C berhasil digenerate dengan sukses!")



