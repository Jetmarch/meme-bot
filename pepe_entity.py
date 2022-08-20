import threading, math, sqlite3, random
from logger import Log, LogType
from pepe_progress import PepeProgress
from pepe_stat import Stat
from datetime import timedelta, datetime

# from pepe_state import IdleState, DeadState, SleepState



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

class DBWrap:

    db_file_name = 'db.sql'
    
    
    @staticmethod
    def _execute_query_fetchone(query):
        con = sqlite3.connect(DBWrap.db_file_name)
        cur = con.cursor()
        res = cur.execute(query)
        con.commit()
        lst = res.fetchone()
        con.close()
        return lst
    
    @staticmethod
    def _execute_query_fetchall(query):
        con = sqlite3.connect(DBWrap.db_file_name)
        cur = con.cursor()
        res = cur.execute(query)
        con.commit()
        lst = res.fetchall()
        con.close()
        return lst

    @staticmethod
    def get_all_pepe():
        res = DBWrap._execute_query_fetchall("SELECT id, name, chat_id, is_alive, current_level, current_exp, current_health, max_health, state FROM t_pepe_entity;")
        list_of_pepe = []
        for data in res:
            pepe = Pepe()
            pepe.bot_id = data[0]
            pepe.bot_name = data[1]
            pepe.chat_id = data[2]
            pepe.is_alive = data[3]
            pepe.current_level = data[4]
            pepe.current_exp = data[5]
            pepe.health = Stat(data[7], data[6])
            pepe.progress = DBWrap._get_pepe_state(data[8])
            list_of_pepe.append(pepe)
        return list_of_pepe
    
    @staticmethod
    def _get_pepe_state(data):
        if data == PepeProgress.Egg.value:
            return PepeProgress.Egg
        elif data == PepeProgress.Young.value:
            return PepeProgress.Young
        elif data == PepeProgress.Adult.value:
            return PepeProgress.Adult
        elif data == PepeProgress.Ancient.value:
            return PepeProgress.Ancient

    @staticmethod
    def add_pepe(pepe):
        pass

    @staticmethod
    def update_pepe(pepe: Pepe):
        con = sqlite3.connect(DBWrap.db_file_name)
        cur = con.cursor()
        cur.execute("UPDATE t_pepe_entity SET is_alive = ?, current_level = ?, current_exp = ?, current_health = ?, max_health = ?, state = ? \
            WHERE id = ?", 
            [pepe.is_alive, pepe.current_level, pepe.current_exp, pepe.health.current, pepe.health.max, pepe.progress.value, pepe.bot_id])
        con.commit()
        con.close()
    
    @staticmethod
    def get_speech(state, progress, event_name):
        con = sqlite3.connect(DBWrap.db_file_name)
        cur = con.cursor()
        res = cur.execute("SELECT speech FROM t_speech WHERE state = ? and progress = ? and event = ?;", [str(state), str(progress), str(event_name)])
        ls = []
        for speech in res.fetchall():
            ls.append(speech)
        
        con.close()
        return ls

class PepeSpeech:
    '''
        Возвращает одну случайную реплику из списка на на каждый описанный случай для Пепе
    '''

    @staticmethod
    def on_idle(state, progress) -> str:
        lst = DBWrap.get_speech(state, progress, PepeSpeech.on_idle.__name__)
        return lst[random.randint(0, len(lst) - 1)][0]

    @staticmethod
    def on_pat(state, progress) -> str:
        lst = DBWrap.get_speech(state, progress, PepeSpeech.on_pat.__name__)
        return lst[random.randint(0, len(lst) - 1)][0]

    @staticmethod
    def on_level_up(state, progress) -> str:
        lst = DBWrap.get_speech(state, progress, PepeSpeech.on_level_up.__name__)
        return lst[random.randint(0, len(lst) - 1)][0]
    
    @staticmethod
    def on_message(state, progress) -> str:
        lst = DBWrap.get_speech(state, progress, PepeSpeech.on_message.__name__)
        return lst[random.randint(0, len(lst) - 1)][0]

    @staticmethod
    def on_night_message(state, progress) -> str:
        lst = DBWrap.get_speech(state, progress, PepeSpeech.on_night_message.__name__)
        return lst[random.randint(0, len(lst) - 1)][0]

    @staticmethod
    def on_die(state, progress) -> str:
        lst = DBWrap.get_speech(state, progress, PepeSpeech.on_die.__name__)
        return lst[random.randint(0, len(lst) - 1)][0]

    @staticmethod
    def on_revive(state, progress) -> str:
        lst = DBWrap.get_speech(state, progress, PepeSpeech.on_revive.__name__)
        return lst[random.randint(0, len(lst) - 1)][0]

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
    time_to_idle =  60 * 60

    # Пепе будет укладываться спать в 11 вечера и просыпаться в 8 утра
    # Во время сна не будет происходить снижение здоровья за бездействие
    go_to_sleep_time = 24
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
            self.pepe.msg_func(self.pepe.chat_id, PepeSpeech.on_message(self, self.pepe.progress))

    def on_pat(self, event) -> None:
        ''' 
            Событие-реакция бота на поглаживание через команду в беседе
            Обновляет таймер
        '''
        self._restart_timer()
        self.pepe.msg_func(self.pepe.chat_id, PepeSpeech.on_pat(self, self.pepe.progress), event)

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
            return self.pepe.msg_func(self.pepe.chat_id, PepeSpeech.on_idle(self, self.pepe.progress))

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
        self.pepe.msg_func(self.pepe.chat_id, PepeSpeech.on_die(self, self.pepe.progress))
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