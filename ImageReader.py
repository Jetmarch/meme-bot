import string
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter

class ImageReader:
    def __init__(self) -> None:
        pytesseract.pytesseract.tesseract_cmd = 'D:\\Tesseract\\tesseract.exe'

    def read(self, path_to_image, lang='rus') -> string:
        im = Image.open(path_to_image)
        im = im.filter(ImageFilter.MedianFilter())
        enhancer = ImageEnhance.Contrast(im)
        im = enhancer.enhance(2)
        im = im.convert('1')
        im.save('temp2.jpg')
        text = pytesseract.image_to_string(Image.open('temp2.jpg'), lang=lang)
        return text