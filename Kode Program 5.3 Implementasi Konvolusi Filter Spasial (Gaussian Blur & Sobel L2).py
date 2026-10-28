# --- Realisasi Konvolusi Gaussian Blur 3x3 ---
padded = np.pad(image.astype(np.float64), ((1,1), (1,1), (0,0)), mode="edge")
kernel_gauss = np.array([[1, 2, 1], [2, 4, 2], [1, 2, 1]], dtype=np.float64) / 16.0
blur_result = np.zeros_like(image, dtype=np.float64)

for i in range(3):
    for j in range(3):
        blur_result += kernel_gauss[i, j] * padded[i:i + H, j:j + W]
output_blur = np.clip(blur_result, 0, 255).astype(np.uint8)

# --- Realisasi Magnitudo Gradien Sobel L2 ---
# (Setelah konvolusi kernel gx dan gy pada citra derajat keabuan)
magnitude = np.sqrt(gx**2 + gy**2)
output_sobel = np.clip(magnitude, 0, 255).astype(np.uint8)