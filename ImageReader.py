import string
import cv2
import numpy as np
import easyocr
import matplotlib.pyplot as plt
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter


class ImageReader:
    used_lang = 'eng+rus'
    def __init__(self) -> None:
        pytesseract.pytesseract.tesseract_cmd = 'D:\\Tesseract\\tesseract.exe'

    def read(self, path_to_image, lang='rus') -> string:
        #image = cv2.imread(path_to_image, 0)
        #image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        #text = pytesseract.image_to_string(image, lang=self.used_lang)
        text = self.recognize_text(path_to_image)
        return text

    def recognize_text(self, img_path):
        reader = easyocr.Reader(['en', 'ru'])
        return reader.readtext(img_path)