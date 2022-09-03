from PIL import Image, ImageDraw, ImageFont

class ImageCreator:

    @staticmethod
    def create_image_with_text(text, x, y, font_size = 24, img_size = (512, 300), background_color = (188, 163, 113), font_color = (255, 255, 255)) -> str:
        img_name = 'temp/img.png'
        img = Image.new("RGB", img_size, color=background_color)
        draw = ImageDraw.Draw(img)

        font = ImageFont.truetype("fonts/Rubik/Rubik-Medium.ttf", size=font_size)
        draw.text((x, y), text=text, font=font, fill=font_color)
        img.save(img_name)
        return img_name
    
    @staticmethod
    def add_img_to_image(image_to_paste, background_img, x, y) -> str:
        img_name = 'temp/result.png'
        paste_image = Image.open(image_to_paste, 'r')
        background = Image.open(background_img, 'r')
        paste_image = paste_image.convert("RGBA")
        background = background.convert("RGBA")
        
        background.paste(paste_image, (x, y), paste_image)
        background.save(img_name)
        return img_name