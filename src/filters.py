
import numpy as np


def apply_grayscale(image: np.ndarray) -> np.ndarray:
    """
    Mengonversi citra RGB menjadi grayscale menggunakan bobot luminansi
    standar ITU-R BT.601.

    Rumus:
        Gray = 0.299 * R + 0.587 * G + 0.114 * B

    Args:
        image: Array RGB berdimensi (H, W, 3), bertipe uint8.

    Returns:
        Array grayscale berdimensi (H, W), bertipe uint8.
    """
    image_float = image.astype(np.float64)

    gray = (
        0.299 * image_float[:, :, 0]
        + 0.587 * image_float[:, :, 1]
        + 0.114 * image_float[:, :, 2]
    )

    return np.clip(gray, 0, 255).astype(np.uint8)


def apply_gaussian_blur(image: np.ndarray) -> np.ndarray:
    """
    Menerapkan Gaussian Blur dengan kernel 3x3.

    Kernel:
        [[1, 2, 1],
         [2, 4, 2],
         [1, 2, 1]] / 16

    Padding menggunakan edge replication agar ukuran citra tetap sama.

    Args:
        image: Array grayscale (H, W) atau RGB (H, W, 3),
               bertipe uint8.

    Returns:
        Array hasil blur dengan dimensi dan dtype yang sama seperti input.
    """
    if image.ndim == 2:
        pad_width = ((1, 1), (1, 1))
    elif image.ndim == 3 and image.shape[2] == 3:
        pad_width = ((1, 1), (1, 1), (0, 0))
    else:
        raise ValueError(
            "Input harus berupa citra grayscale (H, W) "
            "atau RGB (H, W, 3)."
        )

    image_float = image.astype(np.float64)

    kernel = np.array(
        [
            [1, 2, 1],
            [2, 4, 2],
            [1, 2, 1],
        ],
        dtype=np.float64,
    ) / 16.0

    padded = np.pad(image_float, pad_width, mode="edge")
    height, width = image.shape[:2]

    result = np.zeros_like(image_float, dtype=np.float64)

    for i in range(3):
        for j in range(3):
            if image.ndim == 2:
                region = padded[
                    i:i + height,
                    j:j + width,
                ]
            else:
                region = padded[
                    i:i + height,
                    j:j + width,
                    :,
                ]

            result += kernel[i, j] * region

    return np.clip(result, 0, 255).astype(np.uint8)


def apply_sobel(image: np.ndarray) -> np.ndarray:
    """
    Mendeteksi tepi citra menggunakan operator Sobel 3x3.

    Citra RGB dikonversi menjadi grayscale terlebih dahulu.
    Magnitudo gradien dihitung menggunakan:

        G = sqrt(Gx**2 + Gy**2)

    Hasil akhirnya di-clip ke rentang 0-255.

    Args:
        image: Array grayscale (H, W) atau RGB (H, W, 3),
               bertipe uint8.

    Returns:
        Array citra tepi 2D berdimensi (H, W), bertipe uint8.
    """
    if image.ndim == 3 and image.shape[2] == 3:
        gray = apply_grayscale(image)
    elif image.ndim == 2:
        gray = image
    else:
        raise ValueError(
            "Input harus berupa citra grayscale (H, W) "
            "atau RGB (H, W, 3)."
        )

    gray_float = gray.astype(np.float64)
    height, width = gray.shape

    kernel_x = np.array(
        [
            [-1, 0, 1],
            [-2, 0, 2],
            [-1, 0, 1],
        ],
        dtype=np.float64,
    )

    kernel_y = np.array(
        [
            [-1, -2, -1],
            [0, 0, 0],
            [1, 2, 1],
        ],
        dtype=np.float64,
    )

    padded = np.pad(gray_float, 1, mode="edge")

    gx = np.zeros((height, width), dtype=np.float64)
    gy = np.zeros((height, width), dtype=np.float64)

    for i in range(3):
        for j in range(3):
            region = padded[
                i:i + height,
                j:j + width,
            ]

            gx += kernel_x[i, j] * region
            gy += kernel_y[i, j] * region

    magnitude = np.sqrt(gx**2 + gy**2)

    return np.clip(magnitude, 0, 255).astype(np.uint8)
