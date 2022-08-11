import time
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor


def write_msg(chat_id, message):
    random_id = int(round(time.time() * 1000))
    vk.method('messages.send', {'chat_id': chat_id, 'message': message, 'random_id':random_id})


f = open('token.txt', 'r', encoding="utf-8")
token = f.readline()

f.close()

vk = vk_api.VkApi(token=token)
longpoll = VkBotLongPoll(vk, '215306309')

print('Launched')

'''
TODO: Добавить команду, дающую возможность запомнить айди беседы 
        для дальнейшего распределения сообщений
      Пока что планируется распределение только по языку картинки (английский и русский)

'''
for event in longpoll.listen():
    print('event from: ' + str(event.chat_id))
    
    if event.type == VkBotEventType.MESSAGE_NEW:
        if event.from_chat:
            print('event from chat: ' + event.message.text)
            
            if event.message.text == 'Boi?':
                write_msg(event.chat_id, 'Oh yeah. Im fkin alive')
            else:
                write_msg(event.chat_id, 'I sleep.')