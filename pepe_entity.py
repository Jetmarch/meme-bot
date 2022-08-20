import threading, math
from logger import Log, LogType
from pepe_progress import PepeProgress
from pepe_stat import Stat
from datetime import timedelta

from pepe_state import IdleState, DeadState, SleepState



class Pepe:
    bot_id = 0
    bot_name = ""
    bot_prefix = "!"
    chat_id = 1

    current_level = 1
    current_exp = 0
    next_level_exp = 0
   

    def __init__(self) -> None:
        self.happiness = Stat(10)
        self.health = Stat(10)
        self.next_level_exp = max(int((self.current_exp * self.current_exp) * 0.65), 65)
        self.is_alive = True
        self.progress = PepeProgress.Egg
        self.current_state = IdleState(self)
        
    
    def _set_die(self):
        self.current_state = DeadState(self)

    def _set_sleep(self):
        self.current_state = SleepState(self)

    def _set_idle(self):
        self.current_state = IdleState(self)
    
    def set_msg_func(self, msg_func):
        # FIX_ME: Пересмотреть возможность взаимодействия с vk_api
        self.msg_func = msg_func
        #self.greeting()

    def greeting(self) -> None:
        if self.chat_id != 0:
            self.msg_func(self.chat_id, f"{self.bot_name} неожиданно появляется и приветствует всех!")
    
    def on_idle(self) -> None:
        self.current_state.on_idle()

    def on_pat(self, event) -> None:
        ''' 
            Событие-реакция бота на поглаживание через команду в беседе
        '''
        self.current_state.on_pat(event)
    
    def on_message(self, event) -> None:
        ''' 
            Событие-реакция бота на новое сообщение в беседе.
            Обновляет таймер, лечит Пепе (TODO: продумать механику лечения)
            Так же даёт ему немного опыта в зависимости от типа сообщения
        '''
        self.current_state.on_message(event)

    def on_level_up(self, event) -> None:
        ''' 
            Событие-реакция бота на поднятие уровня.
            Обновляет здоровье до максимального
            и устанавливает другой статус Пепе.
            Так же устанавливает следующие границы для повышения уровня
        '''

        self.next_level_exp += int(math.sqrt(self.next_level_exp) * 0.7)
        self.current_exp = 0
        self.current_level += 1

        #Границы поднятия на новый статус установлены в значениях PepeState
        if self.current_level == PepeProgress.Young.value:
            self.progress = PepeProgress.Young
            self.msg_func(self.chat_id, f'{self.bot_name} впервые увидел этот мир, вылупившись из яйца!')
        
        elif self.current_level == PepeProgress.Adult.value:
            self.progress = PepeProgress.Adult
            self.msg_func(self.chat_id, f'Похоже, что {self.bot_name} не на шутку повзрослел!')

        elif self.current_level == PepeProgress.Ancient.value:
            self.progress = PepeProgress.Ancient
            self.msg_func(self.chat_id, f'Ничего не попишешь. Наш {self.bot_name} стал настоящим мудрецом!')

        else:
            self.msg_func(self.chat_id, f'{self.bot_name} стал чуточку лучше!')

    def get_bot_info(self, event) -> None:
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
                + f'Текущий опыт: {self.current_exp}/{self.next_level_exp}\n' \
                + f'Текущее развитие: {self._get_str_state()}\n'\
                + f'Текущее состояние: {self.current_state.__str__()}\n'
                )

    def _get_str_state(self):
        if self.progress == PepeProgress.Egg:
            return 'Яйцо'
        if self.progress == PepeProgress.Young:
            return 'Молодой Пепега'
        if self.progress == PepeProgress.Adult:
            return 'Взрослый Пепега'
        if self.progress == PepeProgress.Ancient:
            return 'Мудрый Пепега'  
    
    def _generate_name(self):
        '''
            Присваивает случайное имя из списка
        '''
        self.bot_name = '' #TODO: Класс, хранящий в себе все реплики, названия и имена

    def _start_func_after_hours(self, func, hour, minutes = 0):
        run_at = timedelta(hours=hour, minutes=minutes)
        threading.Timer(run_at.total_seconds(), func).start()
        print(run_at)