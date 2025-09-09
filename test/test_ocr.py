import cv2
from src.ocr.ocr import OCR

image = cv2.imread("test/Screenshot from 2025-09-09 02-13-29.png")
test_string = OCR.read_text(image=image)

print(test_string)