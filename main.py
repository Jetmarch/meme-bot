from ImageReader import ImageReader
from ImageLoader import ImageLoader


image_url = ''


imageReader = ImageReader()

#Если возвращаемое значение 0, то сообщение с мемом должно быть отправлено в группу с английскими мемами
print(len(imageReader.read(ImageLoader.load_from_url(image_url))))