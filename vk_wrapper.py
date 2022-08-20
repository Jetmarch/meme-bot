import json
import time, vk_api, requests
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from db_wrapper import DBWrap
from logger import Log, LogType

class vk_wrapper:
    token = ''
    english_conf_id = 0
    russian_conf_id = 0
    bot_admin_id = 365491689
    bot_group_id = '215306309'
    bot_prefix = '!'

    pepe_list = []

    def __init__(self) -> None:
        self._launch_bot()
    
    def _launch_bot(self):
        f = open('token.txt', 'r', encoding="utf-8")
        self.token = f.readline()
        f.close()
        #f = open('lang_detect_key.txt', 'r', encoding="utf-8")
        #detectlanguage.configuration.api_key = f.readline()
        #f.close()
        self.vk = vk_api.VkApi(token=self.token)
        self.longpoll = VkBotLongPoll(self.vk, self.bot_group_id, 5)

        self.db_wrap = DBWrap()
        self.pepe_list = self.db_wrap.get_all_pepe()

        for pepe in self.pepe_list:
            pepe.set_msg_func(self.write_msg)

        Log.log(LogType.OK, "Бот запущен")

    def write_msg(self, chat_id, message, event = None):
        if message == '' or message is None:
            return

        random_id = int(round(time.time() * 1000))

        if event is not None:
            query_json = json.dumps({"peer_id": event.message.peer_id,"conversation_message_ids":[event.message.conversation_message_id],"is_reply":True})
            self.vk.method('messages.send', {'chat_id': chat_id, 'message': message, 'random_id':random_id,
            'forward': [query_json]})
        else:
            self.vk.method('messages.send', {'chat_id': chat_id, 'message': message, 'random_id':random_id})

        Log.log(LogType.INFO, "Ответ '", message, "' в чат ", chat_id)
        

    def _get_pepe_by_chat_id(self, chat_id):
        for pepe in self.pepe_list:
            if pepe.chat_id == chat_id:
                return pepe
        return None

    #TODO: Рассылка описания изменений по беседам, либо команда !хотфикс
    def listen_longpoll(self):
        while True:
            try:
                for event in self.longpoll.listen():
                    try:
                        if event.type == VkBotEventType.MESSAGE_NEW:
                            if event.from_chat:
                                pepe = self._get_pepe_by_chat_id(event.chat_id)
                            
                                if pepe is not None:
                                    Log.log(LogType.DEBUG, 'Пепе для беседы ', event.chat_id, ' ', pepe.bot_name, ' id: ', pepe.bot_id)                     
                                    pepe.on_message(event)
                                    self.db_wrap.update_pepe(pepe)
                                    
                                #if event.message.text.lower().strip(' ') == self.bot_prefix + 'завести':
                                #    self.write_msg(event.chat_id, 'Пока нет возможности завести Пепе, но такая возможность скоро будет доступна')
                    except Exception as e:
                        self.write_msg(event.chat_id, 'Что-то пошло не так...')
                        Log.log(LogType.CRITICAL, "Ошибка в основном цикле обработки событий - ", str(e))

            except requests.exceptions.RequestException:
                    Log.log(LogType.CRITICAL, "Ошибка сети. Переподключение...")
                    time.sleep(5)

