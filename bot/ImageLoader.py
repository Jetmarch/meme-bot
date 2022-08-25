import string
import requests


class ImageLoader:
    def load_from_url(url, filename = 'temp.jpg') -> string:
        img_data = requests.get(url).content
        with open(filename, 'wb') as handler:
            handler.write(img_data)
        return filename

