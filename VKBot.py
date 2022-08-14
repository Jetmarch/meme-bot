import time
import vk_api
from ImageLoader import ImageLoader
from ImageReader import ImageReader
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import detectlanguage

class VkBot:
    token = ''
    english_conf_id = 0
    russian_conf_id = 0
    bot_admin_id = 365491689

    def __init__(self) -> None:
        f = open('token.txt', 'r', encoding="utf-8")
        self.token = f.readline()
        f.close()
        f = open('lang_detect_key.txt', 'r', encoding="utf-8")
        detectlanguage.configuration.api_key = f.readline()
        f.close()
        self.vk = vk_api.VkApi(token=self.token)
        self.longpoll = VkBotLongPoll(self.vk, '215306309')
        self.imageReader = ImageReader()
        print('Bot launched')

    def write_msg(self, chat_id, message):
        random_id = int(round(time.time() * 1000))
        self.vk.method('messages.send', {'chat_id': chat_id, 'message': message, 'random_id':random_id})
        print(message)

    def listen_longpoll(self):
        for event in self.longpoll.listen():
            try:
                #print('event from: ' + str(event.chat_id))
                if event.type == VkBotEventType.MESSAGE_NEW:
                    if event.from_chat:

                        
                        '''
                        if event.message.text == '!rus' and event.message.from_id == self.bot_admin_id:
                            self.english_conf_id = event.chat_id
                            self.write_msg(event.chat_id, 'Запомнил')
                        if event.message.text == '!eng' and event.message.from_id == self.bot_admin_id:
                            self.russian_conf_id = event.chat_id
                            self.write_msg(event.chat_id, 'Запомнил')

                        #print(str(event))
                        #Загрузка самой большой картинки из вложения в сообщении
                        if len(event.message.attachments) != 0:
                            for size in event.message.attachments[0]['wall']['attachments'][0]['photo']['sizes']:
                                if(size['type'] == 'r'):
                                    ImageLoader.load_from_url(size['url'])
                            text = self.imageReader.read('temp.jpg')
                            print(text)
                            try:
                                lang = detectlanguage.simple_detect(text)
                            
                                print(lang)
                                self.write_msg(event.chat_id, 'Что я прочитал: ' + text + '\n' 
                                    + ' Какой язык я определил: ' + lang)
                            except Exception as e:
                                self.write_msg(event.chat_id, 'Не нашёл на пикче слов')
                                print(str(e))
                        '''
            except Exception as e:
                self.write_msg(event.chat_id, 'Сломалься.')
                print(str(e))

