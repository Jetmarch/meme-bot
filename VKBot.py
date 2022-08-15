import time
import vk_api
from ImageLoader import ImageLoader
from ImageReader import ImageReader
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from logger import Log, LogType
from pepe_entity import Pepe
#import detectlanguage

class VkBot:
    token = ''
    english_conf_id = 0
    russian_conf_id = 0
    bot_admin_id = 365491689
    bot_group_id = '215306309'
    bot_prefix = '!'

    def __init__(self) -> None:
        f = open('token.txt', 'r', encoding="utf-8")
        self.token = f.readline()
        f.close()
        #f = open('lang_detect_key.txt', 'r', encoding="utf-8")
        #detectlanguage.configuration.api_key = f.readline()
        #f.close()
        self.vk = vk_api.VkApi(token=self.token)
        self.longpoll = VkBotLongPoll(self.vk, self.bot_group_id)
        #self.imageReader = ImageReader()
        self.pepe_bot = Pepe(self.write_msg)
        Log.log(LogType.OK, "Бот запущен")

    def write_msg(self, chat_id, message):
        if message == '' or message is None:
            return
        
        random_id = int(round(time.time() * 1000))
        self.vk.method('messages.send', {'chat_id': chat_id, 'message': message, 'random_id':random_id})
        Log.log(LogType.INFO, "Ответ '", message, "' в чат ", chat_id)

    def listen_longpoll(self):
        for event in self.longpoll.listen():
            try:
                if event.type == VkBotEventType.MESSAGE_NEW:
                    if event.from_chat:
                        #Сделано для теста. TODO: переделать в лист ботов и хранить данные о каждом в базе данных
                        self.pepe_bot.chat_id = event.chat_id
                        #Log.log(LogType.INFO, "Сообщение '", event.message.text, "' из беседы: ", event.chat_id)
                        if event.message.text == self.bot_prefix + 'Погладил Пепе':
                            self.pepe_bot.on_pat(event)
                        elif event.message.text == self.bot_prefix + 'Пепе статы':
                            self.pepe_bot.get_bot_info(event)
                        else:
                            self.pepe_bot.on_message(event)

            except Exception as e:
                self.write_msg(event.chat_id, 'Что-то пошло не так...')
                Log.log(LogType.CRITICAL, "Ошибка в основном цикле - ", str(e))

