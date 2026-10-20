import os
import unittest
import cv2
from src.image_generator import prepare_reference_multires_images


class TestCenterCrop(unittest.TestCase):
    def test_prepare_reference_multires_images(self):
        master_path = os.path.join("data", "dataset_30", "4096", "img_01.png")
        if not os.path.exists(master_path):
            self.skipTest(f"Master dataset {master_path} tidak tersedia")

        output_dir = os.path.join("data", "input")
        res_dict = prepare_reference_multires_images(master_path=master_path, output_dir=output_dir)

        expected_resolutions = [512, 1024, 2048, 4096]
        for res in expected_resolutions:
            self.assertIn(res, res_dict, f"Resolusi {res} tidak ada dalam dictionary hasil")
            file_path = res_dict[res]
            self.assertTrue(os.path.exists(file_path), f"File {file_path} tidak ditemukan")

            img = cv2.imread(file_path)
            self.assertIsNotNone(img, f"Gagal membaca gambar {file_path}")
            self.assertEqual(img.shape, (res, res, 3), f"Dimensi citra {res} salah: {img.shape}")


if __name__ == "__main__":
    unittest.main()
