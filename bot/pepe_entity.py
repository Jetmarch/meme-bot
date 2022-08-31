import threading, math, sqlite3, random
from logger import Log, LogType
from pepe_progress import PepeProgress
from pepe_stat import Stat
from datetime import timedelta, datetime
from image_creator import ImageCreator

class Config:

    @staticmethod
    def get_value(key):
        try:
            return DBWrap.find_config_value_by_key(key)[0][0]
        except IndexError:
            Log.log(LogType.ERROR, f'Не найден ключ "{key}" в конфиге базы данных')

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
    
    def set_msg_func(self, msg_func, photo_func):
        # FIX_ME: Пересмотреть возможность взаимодействия с vk_api
        self.msg_func = msg_func
        self.send_photo_func = photo_func
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

    def _start_func_after_time(self, func, hour, minutes = 0):
        run_at = timedelta(hours=hour, minutes=minutes)
        timer = threading.Timer(run_at.total_seconds(), func)
        timer.start()
        return timer

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
    def _execute_query_fetchall(query, arg_list = None):
        con = sqlite3.connect(DBWrap.db_file_name)
        cur = con.cursor()
        if arg_list is not None:
            res = cur.execute(query, arg_list)
        else:
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
        con = sqlite3.connect(DBWrap.db_file_name)
        cur = con.cursor()
        cur.execute("INSERT INTO t_pepe_entity (name, chat_id, current_level, current_exp, current_health, max_health, state) \
                VALUES (?, ?, ?, ?, ?, ?, ?)", [pepe.bot_name, pepe.chat_id, pepe.current_level,
                pepe.current_exp, pepe.health.current, pepe.health.max, pepe.progress.value])
        con.commit()
        con.close()
    
    @staticmethod
    def get_random_pepe_name():
        con = sqlite3.connect(DBWrap.db_file_name)
        cur = con.cursor()
        res = cur.execute("SELECT name FROM t_bot_names;")
        ls = []
        for name in res.fetchall():
            ls.append(name)
        con.close()

        return ls[random.randint(0, len(ls) - 1)][0]

    @staticmethod
    def find_config_value_by_key(key):
        res = DBWrap._execute_query_fetchall("SELECT value FROM t_config WHERE key = ?", [key])
        return res

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
    
    @staticmethod
    def get_answer(state, progress, event_name, question):
        #Удаление первого символа, если это "!"
        if question[0] == '!':
            question = question[1:]
        con = sqlite3.connect(DBWrap.db_file_name)
        cur = con.cursor()
        res = cur.execute("SELECT speech FROM t_speech WHERE state = ? and progress = ? and event = ? and question = ?;", [str(state), str(progress), str(event_name), str(question)])
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
        try:
            lst = DBWrap.get_speech(state, progress, PepeSpeech.on_message.__name__)
            return lst[random.randint(0, len(lst) - 1)][0]
        except:
            return None
    
    @staticmethod
    def on_question(state, progress, question) -> str:
        try:
            lst = DBWrap.get_answer(state, progress, PepeSpeech.on_question.__name__, question)
            return lst[random.randint(0, len(lst) - 1)][0]
        except:
            return None

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
        
        #
        self.command_set = {f'{self.pepe.bot_prefix}погладил': self.on_pat,
             f'{self.pepe.bot_prefix}статы': self.get_bot_info,
             f'{self.pepe.bot_prefix}помощь' : self.get_command_list,
             f'{self.pepe.bot_prefix}команды' : self.get_command_list
             }

    def on_message(self, event):
        # Команды вызываются с помощью словаря. Каждый метод-команда должен принимать в себя event
        try:
            self.command_set[event.message.text.lower().strip(' ')](event)
        except KeyError:
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
        img_name = ImageCreator.create_image_with_text( f'Имя: {self.pepe.bot_name}\n' \
                + f'Текущее здоровье: {self.pepe.health.current}/{self.pepe.health.max} \n' \
                + f'Текущий уровень: {self.pepe.current_level} \n' \
                + f'Текущий опыт: {self.pepe.current_exp}/{self.pepe.next_level_exp}\n' \
                + f'Текущее развитие: {self.pepe._get_str_state()}\n'\
                + f'Текущее состояние: {self.pepe.current_state.__str__()}\n', 230, 30, 16, img_size=(512, 250))
        img_name = ImageCreator.add_img_to_image('temp/Capture.PNG', img_name, 10, 30)
        self.pepe.send_photo_func(event.chat_id, img_name)
        # self.pepe.msg_func(event.chat_id, 
        #           f'Имя: {self.pepe.bot_name}\n' \
        #         + f'Текущее здоровье: {self.pepe.health.current}/{self.pepe.health.max} \n' \
        #         + f'Текущий уровень: {self.pepe.current_level} \n' \
        #         + f'Текущий опыт: {self.pepe.current_exp}/{self.pepe.next_level_exp}\n' \
        #         + f'Текущее развитие: {self.pepe._get_str_state()}\n'\
        #         + f'Текущее состояние: {self.pepe.current_state.__str__()}\n',
        #         event
        #         )
    
    def get_command_list(self, event):
        command_str = ''
        for key in self.command_set:
            command_str += f'{key} \n'
        self.pepe.msg_func(event.chat_id, f'Список доступных взаимодействий: \n {command_str}')

    def on_idle(self):
        pass

    def __str__(self) -> str:
        "База"

class IdleState(BaseState):

    # Пепега будет уведомлять о скуке каждый час
    time_to_idle =  int(Config.get_value('bot_idle_interval'))

    # Пепе будет укладываться спать в 11 вечера и просыпаться в 8 утра
    # Во время сна не будет происходить снижение здоровья за бездействие
    go_to_sleep_time = int(Config.get_value('bot_go_to_sleep_hour'))
    wake_up_time = int(Config.get_value('bot_wake_up_hour'))

    def __init__(self, pepe) -> None:
        super().__init__(pepe)
        self._set_idle_timer()
        if pepe.health.current <= 0:
            pepe.current_state = DeadState(pepe)
        
        now = datetime.now()
        self.last_time_activity = now
        # Пример добавления новой команды
        self.command_set[f'{self.pepe.bot_prefix}спи'] = self.go_to_sleep
        self.command_set[f'{self.pepe.bot_prefix}умри'] = self.die

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
        for key in self.command_set:
            if event.message.text.lower().strip(' ') == key:
                return
        
        now = datetime.now()
        if now.hour >= self.go_to_sleep_time or now.hour <= self.wake_up_time:
            self.go_to_sleep()
            return

        self.pepe.health.change(1)
        self._restart_timer()
        self.pepe.current_exp += 1
        
        if self.pepe.current_exp >= self.pepe.next_level_exp:
            self.pepe.on_level_up(event)
        
        self._comment_activity(event)

    def _comment_activity(self, event):
        '''
            Отвечает на вопрос, либо комментирует активность с шансом, зависящим от времени последней активности
            Чем больше времени никто не писал, тем выше шанс того, что Пепега ответит
        '''
        if event.message.text != '':
            if '!' == event.message.text.lower()[0]:
                speech = PepeSpeech.on_question(self, self.pepe.progress, event.message.text.lower())
                if speech is not None:
                    self.pepe.msg_func(self.pepe.chat_id, speech)
                else:
                    self.pepe.msg_func(self.pepe.chat_id, PepeSpeech.on_question(self, self.pepe.progress, 'нет ответа'))
            else:
                self._time_based_chance_default_comment() 
    
    def _time_based_chance_default_comment(self):
        now = datetime.now()
        time_sub = now - self.last_time_activity

        if (time_sub.seconds / 60) <= 15:
            self._send_message_with_random_chance(5)
        
        if (time_sub.seconds / 60) > 15 and (time_sub.seconds / 60) <= 30:
            self._send_message_with_random_chance(20)

        if (time_sub.seconds / 60) > 30 and (time_sub.seconds / 60) <= 40:
            self._send_message_with_random_chance(50)
        
        if (time_sub.seconds / 60) > 40:
            self._send_message_with_random_chance(100)
        
        self.last_time_activity = datetime.now()
    
    def _send_message_with_random_chance(self, chance_in_percent):
        '''
            Отправляет сообщение в беседу с указанным шансом
        '''
        if random.randint(0, 100) <= chance_in_percent:
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
            self.die(None)

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

    def die(self, event) -> None:
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
        self.command_set[f'{self.pepe.bot_prefix}воскресить'] = self.revive

    def on_message(self, event):
        '''
            Реагирует только на команды "статы" и "воскресить"
        '''
        super().on_message(event)

        # if event.message.text.lower().strip(' ') == self.pepe.bot_prefix + 'воскресить':
        #     self.revive()

    def on_pat(self, event):
        self.pepe.msg_func(self.pepe.chat_id, f'+ Бедный Пепе уже покинул этот бренный мир. Поглаживания ему не помогут +')
    
    def get_bot_info(self, event):
        super().get_bot_info(event)

    def on_idle(self):
        super().on_idle()

    def revive(self, event) -> None:
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
        self.count_messages_to_awake = int(Config.get_value('bot_count_messages_to_awake'))

        self.alarm = pepe._start_func_after_time(self.wake_up, int(Config.get_value('bot_sleep_time_in_hours')))

    def on_message(self, event):
        '''
            Бот проснётся, если количество сообщений превысит внутренний счётчик
            Если его разбудили ночью и какое-то время после никто ничего не писал в беседу, то он засыпает сам
        '''
        super().on_message(event)
        self.current_messages_count += 1

        if self.current_messages_count >= self.count_messages_to_awake:
            self.wake_up(event)
        

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
            self.pepe.msg_func(self.pepe.chat_id, f"{self.pepe.bot_name} недовольно ворчит, сонно протирает глаза и встаёт с постели", event)
        self.alarm.cancel()
        self.pepe.current_state = IdleState(self.pepe)

    def get_bot_info(self, event):
        super().get_bot_info(event)

    def on_idle(self):
        super().on_idle()
    
    def __str__(self) -> str:
        return "Спит"