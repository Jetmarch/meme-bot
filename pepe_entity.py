import threading
from logger import Log, LogType
import random

class Pepe:
    bot_id = 0
    bot_name = ""
    chat_id = 1

    current_level = 1
    current_exp = 0
    next_level_exp = 0

    # Каждый час
    time_to_idle = 60 * 60

    def __init__(self) -> None:
        self.happiness = Stat(10)
        self.health = Stat(10)
        self.next_level_exp = max(int((self.current_exp * self.current_exp) * 0.65), 65)
        self.is_alive = True
        self._set_timer()
    
    def set_msg_func(self, msg_func):
        # FIX_ME: Пересмотреть возможность взаимодействия с vk_api
        self.msg_func = msg_func
    
    def _generate_name(self):
        '''
            Присваивает случайное имя из списка
        '''
        self.bot_name = '' #TODO: Класс, хранящий в себе все реплики, названия и имена

    def on_idle(self) -> str:
        ''' 
            Событие-реакция бота на отсутствие сообщений в течение определённого времени в беседе.
            Снижает уровень здоровья и оповещает об этом всех участников беседы
        '''

        if not self.is_alive:
            return
        self._restart_timer()
        self.health.change(-1)

        Log.log(LogType.DEBUG, 'Текущее здоровье: ', self.health.current)

        if self.health.current > (int(self.health.max / 2)):
            return self.msg_func(self.chat_id, 'Пепе скучает')

        if self.health.current <= (int(self.health.max / 2)) and self.health.current > 0:
            return self.msg_func(self.chat_id, 'Пепе помирает со скуки')

        if self.health.current <= 0:
            return self.msg_func(self.chat_id, self.die())
       

    def on_pat(self, event) -> str:
        ''' 
            Событие-реакция бота на поглаживание через команду в беседе
            Обновляет таймер
        '''
        #print('Пепе довольно нежится от поглаживаний')
        self._restart_timer()
        self.msg_func(event.chat_id, 'Пепе довольно нежится от поглаживаний')

    '''
        TODO: Отдельная реакция на следующий список разных сообщений
        1. Простое текстовое сообщение
        2. Простое сообщение с картинкой
        3. Пересланное текстовое сообщение из ленты
        4. Пересланное сообщение с картинкой из ленты
        5. Пересланное сообщение с несколькими картинками из ленты
        6. Пересланное сообщение с видео из ленты

    '''
    def on_message(self, event) -> str:
        ''' 
            Событие-реакция бота на новое сообщение в беседе.
            Обновляет таймер, лечит Пепе (TODO: продумать механику лечения)
            Так же даёт ему немного опыта в зависимости от типа сообщения
        '''

        self.health.change(1)
        self._restart_timer()
        self.current_exp += 1
        Log.log(LogType.DEBUG, "Активность! Пепе доволен")

        
        if self.current_exp >= self.next_level_exp:
            self.on_level_up(event)
        
        # С небольшим шансом бот будет как-то комментировать активность в беседе
        if random.randint(0, 9) == 1:
            return self.msg_func(self.chat_id, 'Пепе довольно облизывается, видя активность в беседе')
        else:
            return ''

    def on_level_up(self, event) -> None:
        ''' 
            Событие-реакция бота на поднятие уровня.
            Обновляет здоровье до максимального
            и устанавливает другой статус Пепе.
            Так же устанавливает следующие границы для повышения уровня
        '''
        #Вычисление количества опыта для следующего уровня происходят по формуле (x * x) * 0.65
        pass
    
    def get_bot_info(self, event) -> str:
        '''
            Возвращает информацию о Пепе:
            * Текущий уровень, количество текущего опыта / количество опыта до следующего уровня
            * Текущий уровень здоровья / максимальный уровень здоровья
            * Картинку его статуса (яйцо, маленький Пепе, Пепе-подросток, Пепе-взрослый, Пепе-мудрец)
            * TODO: Продумать несколько промежуточных статусов
        '''
        return self.msg_func(event.chat_id, 
                  f'Имя: {self.bot_name}\n' \
                + f'Текущее здоровье: {self.health.current}/{self.health.max} \n' \
                + f'Текущий уровень: {self.current_level} \n' \
                + f'Текущий опыт: {self.current_exp}/{self.next_level_exp}')

    def die(self) -> str:
        ''' 
            Событие-реакция бота на снижение здоровья до нуля.
            Останавливает таймер и отключает бота
        '''
        Log.log(LogType.WARNING, f'Пепе из беседы {self.chat_id} умер!')
        self.is_alive = False
        self._stop_timer()
        return self.msg_func(self.chat_id, 'Пепе издаёт последний вздох, прежде чем отправиться к праотцам')
    
    def _set_timer(self) -> None:
        self.idle_timer = threading.Timer(self.time_to_idle, self.on_idle)
        self.idle_timer.start()
    
    def _stop_timer(self) -> None:
        if self.idle_timer.is_alive:
            self.idle_timer.cancel()

    def _restart_timer(self) -> None:
        self._stop_timer()
        
        self.idle_timer = threading.Timer(self.time_to_idle, self.on_idle)
        self.idle_timer.start()

    def revive(self) -> None:
        '''
             Возрождение бота. Восстанавливает значение здоровья до максимального,
             но обнуляет весь набранный опыт и уровни
        '''
        self.is_alive = True
        self.health.restore()
        self.current_exp = 0
        self.current_level = 0
        self.next_level_exp = 65
        

class Stat:
    def __init__(self, max_amount, current_amount = 0) -> None:
        self.max = max_amount
        if current_amount == 0:
            self.current = max_amount
        else:
            self.current = current_amount

    def change(self, value) -> None:
        if self.current == self.max and value > 0:
            return
        
        self.current += value

    def restore(self) -> None:
        self.current = self.max