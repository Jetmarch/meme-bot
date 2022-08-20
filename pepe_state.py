from datetime import datetime
import random, threading
from logger import Log, LogType
from pepe_progress import PepeProgress

class BaseState:
    def __init__(self, pepe) -> None:
        self.pepe = pepe

    def on_message(self, event):
        if event.message.text.lower().strip(' ') == self.pepe.bot_prefix + 'погладил':
            self.on_pat(event)
        elif event.message.text.lower().strip(' ') == self.pepe.bot_prefix + 'статы':
            self.get_bot_info(event)
        elif event.message.text.lower().strip(' ') == self.pepe.bot_prefix + 'ап': #дебаг
            self.pepe.on_level_up(event)
        elif event.message.text.lower().strip(' ') == 'умри': #дебаг
            self.pepe._set_die()
        elif event.message.text.lower().strip(' ') == 'спи': #дебаг
            self.pepe._set_sleep()
        elif event.message.text.lower().strip(' ') == 'живи': #дебаг
            self.pepe._set_idle()
    
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
                + f'Текущее состояние: {self.pepe.current_state.__str__()}\n',
                event
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
    go_to_sleep_time = 23
    wake_up_time = 7

    chance_of_answer_on_message = 10

    def __init__(self, pepe) -> None:
        super().__init__(pepe)
        self._set_idle_timer()

        if pepe.health.current <= 0:
            pepe.current_state = DeadState(pepe)

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
        now = datetime.now()
        if now.hour >= self.go_to_sleep_time or now.hour <= self.wake_up_time:
            self.go_to_sleep()
            return

        super().on_message(event)

        self.pepe.health.change(1)
        self._restart_timer()
        self.pepe.current_exp += 1
        
        if self.pepe.current_exp >= self.pepe.next_level_exp:
            self.pepe.on_level_up(event)
        
        # С небольшим шансом бот будет как-то комментировать активность в беседе
        if random.randint(0, 100) <= self.chance_of_answer_on_message:
            #TODO: Иногда присылать гифки с облизывающимся Пепе
            return self.pepe.msg_func(self.pepe.chat_id, f'{self.pepe.bot_name} довольно облизывается, видя активность в беседе')
        else:
            return ''

    def on_pat(self, event) -> None:
        ''' 
            Событие-реакция бота на поглаживание через команду в беседе
            Обновляет таймер
        '''
        self._restart_timer()
        self.pepe.msg_func(self.pepe.chat_id, f'{self.pepe.bot_name} довольно нежится от поглаживаний', event)

    def get_bot_info(self, event):
        super().get_bot_info(event)

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
            self.die()

    def go_to_sleep(self, event = None) -> None:
        '''
            Отправляет Пепе спать. Срабатывает по таймеру, но так же может быть вызвана командой.
            Если вызывается командой, то есть шанс, что Пепе обидится и не послушается команды
        '''
        if event is None:
            self.pepe.msg_func(self.pepe.chat_id, f"{self.pepe.bot_name} укладывается спать")
            self.pepe.current_state = SleepState(self.pepe)
        else:
            self.pepe.msg_func(self.pepe.chat_id, f"{self.pepe.bot_name} обидчиво смотрит в сторону того, кто заставляет его лечь спать", event)

    def die(self) -> None:
        ''' 
            Событие-реакция бота на снижение здоровья до нуля.
            Останавливает таймер и отключает бота
        '''
        Log.log(LogType.WARNING, f'Пепе из беседы {self.pepe.chat_id} умер!')
        self._stop_timer()
        self.pepe.msg_func(self.pepe.chat_id, f'{self.pepe.bot_name} издаёт последний вздох, прежде чем отправиться к праотцам')
        self.pepe.current_state = DeadState(self.pepe)

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

        if event.message.text.lower().strip(' ') == self.pepe.bot_prefix + 'воскресить':
            self.revive()

    def on_pat(self, event):
        pass
    
    def get_bot_info(self, event):
        super().get_bot_info(event)

    def on_idle(self):
        super().on_idle()

    def revive(self) -> None:
        '''
             Возрождение бота. Восстанавливает значение здоровья до максимального,
             но обнуляет весь набранный опыт и уровни
        '''
        self.pepe.health.restore()
        self.pepe.current_exp = 0
        self.pepe.current_level = 1
        self.pepe.next_level_exp = 65
        self.pepe.progress = PepeProgress.Egg
        self.pepe.msg_func(self.pepe.chat_id, f'Круг жизни возвращается и {self.pepe.bot_name} вновь появляется на свет')
        self.pepe.current_state = IdleState(self.pepe)
    
    def __str__(self) -> str:
        return "Мёртв"
    
class SleepState(BaseState):

    def __init__(self, pepe) -> None:
        super().__init__(pepe)
        self.current_messages_count = 0
        self.count_message_to_awake = 10

        pepe._start_func_after_hours(self.wake_up, 8)

    def on_message(self, event):
        '''
            Бот проснётся, если количество сообщений превысит внутренний счётчик
            Если его разбудили ночью и какое-то время после никто ничего не писал в беседу, то он засыпает сам
        '''
        super().on_message(event)
        self.current_messages_count += 1

        if self.current_messages_count >= self.count_message_to_awake:
            self.wake_up()
        

    def on_pat(self, event):
        '''
            Сбрасывает счётчик сообщений, которые должны его разбудить
        '''
        self.current_messages_count = 0
        self.pepe.msg_func(self.pepe.chat_id, f'{self.pepe.bot_name} довольно бурчит в подушку и крепко засыпает', event)
        

    def wake_up(self, event = None) -> None:
        '''
            Будит Пепе. Срабатывает по таймеру, но так же может быть вызвана командой. 
            TODO: При вызове командой ночью (с 12 ночи до 7 утра) Пепе будет ворчать, но не встанет с постели
        '''
        if event is None:
            self.pepe.msg_func(self.pepe.chat_id, f"{self.pepe.bot_name}, потягиваясь, просыпается")
        else:
            self.pepe.msg_func(self.pepe.chat_id, f"{self.pepe.bot_name} недовольно ворчит, переворачиваясь на другой бок", event)

        self.pepe.current_state = IdleState(self.pepe)

    def get_bot_info(self, event):
        super().get_bot_info(event)

    def on_idle(self):
        super().on_idle()
    
    def __str__(self) -> str:
        return "Спит"