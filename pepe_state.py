import datetime
from enum import Enum
import random
import threading
from logger import Log, LogType
from pepe_progress import PepeProgress

class BaseState:
    def __init__(self, pepe) -> None:
        self.pepe = pepe

    def on_message(self, event):
        pass
    
    def on_pat(self, event):
        pass
    
    def get_bot_info(self, event):
        '''
            Возвращает информацию о Пепе:
            * Текущий уровень, количество текущего опыта / количество опыта до следующего уровня
            * Текущий уровень здоровья / максимальный уровень здоровья
            * Картинку его статуса (яйцо, маленький Пепе, Пепе-подросток, Пепе-взрослый, Пепе-мудрец)
            * TODO: Продумать несколько промежуточных статусов
        '''
        return self.pepe.msg_func(event.chat_id, 
                  f'Имя: {self.pepe.bot_name}\n' \
                + f'Текущее здоровье: {self.pepe.health.current}/{self.pepe.health.max} \n' \
                + f'Текущий уровень: {self.pepe.current_level} \n' \
                + f'Текущий опыт: {self.pepe.current_exp}/{self.pepe.next_level_exp}\n' \
                + f'Текущее развитие: {self.pepe._get_str_state()}\n'\
                + f'Текущее состояние: {self.pepe.current_state.__str__()}\n'
                )

    def on_idle(self):
        pass

    def __str__(self) -> str:
        "База"

class IdleState(BaseState):

    # Пепега будет уведомлять о скуке каждый час
    time_to_idle = 60 * 60

    # Пепе будет укладываться спать в 11 вечера и просыпаться в 8 утра
    # Во время сна не будет происходить снижение здоровья за бездействие
    is_sleeping = False
    go_to_sleep_time = 23
    wake_up_time = 7

    def __init__(self, pepe) -> None:
        super().__init__(pepe)
        self._set_idle_timer()

    def on_message(self, event):
        '''
            TODO: Отдельная реакция на следующий список разных сообщений
            1. Простое текстовое сообщение
            2. Простое сообщение с картинкой
            3. Пересланное текстовое сообщение из ленты
            4. Пересланное сообщение с картинкой из ленты
            5. Пересланное сообщение с несколькими картинками из ленты
            6. Пересланное сообщение с видео из ленты

        '''
        super().on_message(event)
        self.pepe.health.change(1)
        self._restart_timer()
        self.pepe.current_exp += 1
        Log.log(LogType.DEBUG, "Активность! Пепе доволен")

        
        if self.pepe.current_exp >= self.pepe.next_level_exp:
            self.pepe.on_level_up(event)
        
        # С небольшим шансом бот будет как-то комментировать активность в беседе
        if random.randint(0, 9) == 1:
            return self.pepe.msg_func(self.pepe.chat_id, f'{self.pepe.bot_name} довольно облизывается, видя активность в беседе')
        else:
            return ''

    def on_pat(self, event) -> None:
        ''' 
            Событие-реакция бота на поглаживание через команду в беседе
            Обновляет таймер
        '''
        self._restart_timer()
        self.pepe.msg_func(event.pepe.chat_id, f'{self.pepe.bot_name} довольно нежится от поглаживаний')

    def get_bot_info(self, event):
        super().get_bot_info()

    def on_idle(self):
        super().on_idle()
        ''' 
            Событие-реакция бота на отсутствие сообщений в течение определённого времени в беседе.
            Снижает уровень здоровья и оповещает об этом всех участников беседы
        '''
        now = datetime.now()
        if now.hour >= self.go_to_sleep_time or now.hour <= self.wake_up_time:
            self.go_to_sleep()
            return
        
        self._restart_timer()
        self.pepe.health.change(-1)

        Log.log(LogType.DEBUG, f'{self.pepe.bot_name} из беседы {self.pepe.chat_id} скучает.')

        if self.pepe.health.current > (int(self.pepe.health.max / 2)):
            return self.pepe.msg_func(self.pepe.chat_id, f'{self.pepe.bot_name} скучает')

        if self.pepe.health.current <= (int(self.pepe.health.max / 2)) and self.pepe.health.current > 0:
            return self.pepe.msg_func(self.pepe.chat_id, f'{self.pepe.bot_name} помирает со скуки')

        if self.pepe.health.current <= 0:
            self._stop_timer()
            return self.pepe.msg_func(self.pepe.chat_id, self.die())

    def go_to_sleep(self, event = None) -> None:
        '''
            Работает только из состояния PepeState.Idle
            Отправляет Пепе спать. Срабатывает по таймеру, но так же может быть вызвана командой.
            Если вызывается командой, то есть шанс, что Пепе обидится и не послушается команды
        '''
        if event is None:
            self.pepe.msg_func(self.pepe.chat_id, f"{self.pepe.bot_name} укладывается спать")
            self.pepe.current_state = SleepState(self.pepe)
            #TODO: Переделать пробуждение бота не по времени, а ЧЕРЕЗ некоторое время после того, как он уснул
            #self._start_func_at_hour(self.wake_up, self.wake_up_time)
        else:
            self.pepe.msg_func(self.pepe.chat_id, f"{self.pepe.bot_name} обидчиво смотрит в сторону того, кто заставляет его лечь спать")

    def die(self) -> None:
        ''' 
            Событие-реакция бота на снижение здоровья до нуля.
            Останавливает таймер и отключает бота
        '''
        Log.log(LogType.WARNING, f'Пепе из беседы {self.pepe.chat_id} умер!')
        self.pepe.current_state = DeadState(self.pepe)
        self.pepe.msg_func(self.pepe.chat_id, f'{self.pepe.bot_name} издаёт последний вздох, прежде чем отправиться к праотцам')

    def _set_idle_timer(self) -> None:
        self.idle_timer = threading.Timer(self.time_to_idle, self.on_idle)
        self.idle_timer.start()
    
    def _restart_timer(self) -> None:
        self._stop_timer()
        
        self.idle_timer = threading.Timer(self.time_to_idle, self.on_idle)
        self.idle_timer.start()
    
    def _stop_timer(self) -> None:
        if self.idle_timer.is_alive:
            self.idle_timer.cancel()
    
    def __str__(self) -> str:
        return "Бодрствует"

class DeadState(BaseState):

    def __init__(self, pepe) -> None:
        super().__init__(pepe)

    def on_message(self, event):
        '''
            Реагирует только на команды "статы" и "воскресить"
        '''
        super().on_message(event)

        if event.message.text.lower().strip(' ') == self.pepe.bot_prefix + 'статы':
            self.get_bot_info(event)
        if event.message.text.lower().strip(' ') == self.pepe.bot_prefix + 'воскресить':
            self.revive()

    def on_pat(self, event):
        pass
    
    def get_bot_info(self, event):
        super().get_bot_info()

    def on_idle(self):
        super().on_idle()

    def revive(self) -> None:
        '''
             Возрождение бота. Восстанавливает значение здоровья до максимального,
             но обнуляет весь набранный опыт и уровни
        '''
        self.pepe.health.restore()
        self.pepe.current_exp = 0
        self.pepe.current_level = 0
        self.pepe.next_level_exp = 65
        self.pepe.progress = PepeProgress.Egg
        self.pepe.current_state = IdleState(self.pepe)
        #TODO: сообщение о воскрешении
        self.pepe.msg_func(self.pepe.chat_id, f'Круг жизни возвращается и {self.pepe.bot_name} вновь появляется на свет')
    
    def __str__(self) -> str:
        return "Мёртв"
    

class SleepState(BaseState):

    def __init__(self, pepe) -> None:
        super().__init__(pepe)
        self.current_messages_count = 0
        self.count_message_to_awake = 10

    def on_message(self, event):
        '''
            Бот проснётся, если количество сообщений превысит внутренний счётчик
            Если его разбудили ночью и какое-то время после никто ничего не писал в беседу, то он засыпает сам
        '''
        self.current_messages_count += 1

        if self.current_messages_count >= self.count_message_to_awake:
            self.wake_up()
        

    def on_pat(self, event):
        '''
            Сбрасывает счётчик сообщений, которые должны его разбудить
        '''
        self.current_messages_count = 0
        self.pepe.msg_func(self.pepe.chat_id, f'{self.pepe.bot_name} довольно бурчит в подушку и крепко засыпает')
        

    def wake_up(self, event = None) -> None:
        '''
            Работает только из состояния PepeState.Sleep
            Будит Пепе. Срабатывает по таймеру, но так же может быть вызвана командой. 
            При вызове командой ночью (с 12 ночи до 7 утра) Пепе будет ворчать, но не встанет с постели
        '''
        if event is None:
            self.pepe.msg_func(self.pepe.chat_id, f"{self.pepe.bot_name}, потягиваясь, просыпается. Доброе утро!")
            self.pepe.current_state = IdleState(self.pepe)
            #self._start_func_at_hour(self.go_to_sleep, self.go_to_sleep_time)
        else:
            self.pepe.msg_func(self.pepe.chat_id, f"{self.pepe.bot_name} недовольно ворчит, переворачиваясь на другой бок")

    def get_bot_info(self, event):
        super().get_bot_info()

    def on_idle(self):
        super().on_idle()
    
    def __str__(self) -> str:
        return "Спит"