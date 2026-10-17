"""
Skrip Otomatisasi Pengunduhan dan Pemrosesan Multiresolusi Dataset
Sumber: Hugging Face (zhang0jhon/Aesthetic-4K)
Tujuan: Mengunduh 30 citra 4K/6K fotografi nyata, melakukan center-crop persegi (1:1),
        dan mengekspor ke 4 tingkatan resolusi standar (512, 1024, 2048, 4096)
        menghasilkan total 120 berkas citra uji deterministik.
"""

import os
import sys
import json
import urllib.request
import cv2
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(BASE_DIR, "data", "dataset_30")

RESOLUTIONS = [512, 1024, 2048, 4096]
NUM_IMAGES_TARGET = 30
API_URL = "https://huggingface.co/api/datasets/zhang0jhon/Aesthetic-4K/tree/main/train/images/0000"
RAW_BASE_URL = "https://huggingface.co/datasets/zhang0jhon/Aesthetic-4K/resolve/main"

def prepare_directories():
    for res in RESOLUTIONS:
        folder = os.path.join(DATASET_DIR, str(res))
        os.makedirs(folder, exist_ok=True)

def fetch_image_list():
    print("[*] Menghubungi Hugging Face API untuk mengambil katalog gambar...")
    req = urllib.request.Request(API_URL, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        items = json.loads(resp.read().decode())
    
    # Filter item gambar dengan ukuran minimal 2.5 MB (menjamin foto resolusi tinggi 4K/6K)
    high_res_items = [
        item for item in items 
        if item.get("type") == "file" and item.get("path", "").endswith(".jpg") and item.get("size", 0) >= 2500000
    ]
    print(f"[+] Ditemukan {len(high_res_items)} foto beresolusi tinggi (>= 2.5 MB).")
    return high_res_items[:NUM_IMAGES_TARGET]

def process_and_save_multires(img_bgr: np.ndarray, index: int):
    h, w = img_bgr.shape[:2]
    min_dim = min(h, w)
    
    # Center-crop ke rasio persegi 1:1
    y1 = (h - min_dim) // 2
    y2 = y1 + min_dim
    x1 = (w - min_dim) // 2
    x2 = x1 + min_dim
    cropped = img_bgr[y1:y2, x1:x2]
    
    # Simpan ke 4 tingkatan resolusi
    for res in RESOLUTIONS:
        if min_dim == res:
            resized = cropped
        elif min_dim > res:
            resized = cv2.resize(cropped, (res, res), interpolation=cv2.INTER_AREA)
        else:
            resized = cv2.resize(cropped, (res, res), interpolation=cv2.INTER_LANCZOS4)
            
        out_filename = f"img_{index:02d}.png"
        out_path = os.path.join(DATASET_DIR, str(res), out_filename)
        
        # Simpan dalam format PNG tanpa kompresi berat untuk kecepatan dan ketajaman
        cv2.imwrite(out_path, resized, [cv2.IMWRITE_PNG_COMPRESSION, 1])

def main():
    prepare_directories()
    selected_items = fetch_image_list()
    
    if len(selected_items) < NUM_IMAGES_TARGET:
        print(f"[!] Peringatan: Hanya menemukan {len(selected_items)} gambar.")
        
    print(f"\n[*] Memulai pengunduhan dan pembuatan 120 berkas citra multiresolusi ({NUM_IMAGES_TARGET} citra x 4 resolusi)...")
    
    success_count = 0
    for idx, item in enumerate(selected_items, start=1):
        rel_path = item["path"]
        download_url = f"{RAW_BASE_URL}/{rel_path}"
        file_size_mb = item["size"] / (1024 ** 2)
        
        print(f"[{idx:02d}/{NUM_IMAGES_TARGET}] Mengunduh {os.path.basename(rel_path)} ({file_size_mb:.2f} MB)...", end=" ", flush=True)
        
        try:
            req = urllib.request.Request(download_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=45) as resp:
                raw_bytes = resp.read()
                
            img_array = np.frombuffer(raw_bytes, dtype=np.uint8)
            img_bgr = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            
            if img_bgr is None:
                print("GAGAL (imdecode)")
                continue
                
            orig_h, orig_w = img_bgr.shape[:2]
            process_and_save_multires(img_bgr, idx)
            print(f"SUKSES! (Dimensi Asli: {orig_w}x{orig_h} -> 512, 1024, 2048, 4096)")
            success_count += 1
            
        except Exception as e:
            print(f"ERROR ({str(e)})")
            
    print("\n" + "=" * 70)
    print(f"[+] Selesai! Berhasil memproses {success_count} citra ke dalam 4 folder resolusi.")
    print(f"[+] Total berkas baru di {DATASET_DIR}: {success_count * len(RESOLUTIONS)} berkas PNG.")
    print("=" * 70)

if __name__ == "__main__":
    main()
