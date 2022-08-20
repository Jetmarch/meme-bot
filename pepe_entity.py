import threading, random, math
from logger import Log, LogType
from pepe_progress import PepeProgress
from pepe_stat import Stat
from datetime import datetime, timedelta


class Pepe:
    bot_id = 0
    bot_name = ""
    chat_id = 1

    current_level = 1
    current_exp = 0
    next_level_exp = 0

    # Пепе будет укладываться спать в 11 вечера и просыпаться в 8 утра
    # Во время сна не будут обрабатываться сообщения, адресованные Пепе
    # А так же не будет происходить снижение здоровья за бездействие
    is_sleeping = False
    go_to_sleep_time = 23
    wake_up_time = 7

    # Каждый час
    time_to_idle = 60 * 60

    def __init__(self) -> None:
        self.happiness = Stat(10)
        self.health = Stat(10)
        self.next_level_exp = max(int((self.current_exp * self.current_exp) * 0.65), 65)
        self.is_alive = True
        self._set_timer()
        self.progress = PepeProgress.Egg

        now = datetime.now()

        if now.hour >= self.go_to_sleep_time or now.hour <= self.wake_up_time:
            self.go_to_sleep()
        else:
            self.wake_up()
    
    def set_msg_func(self, msg_func):
        # FIX_ME: Пересмотреть возможность взаимодействия с vk_api
        self.msg_func = msg_func
    
    
    def on_idle(self) -> str:
        ''' 
            Событие-реакция бота на отсутствие сообщений в течение определённого времени в беседе.
            Снижает уровень здоровья и оповещает об этом всех участников беседы
        '''

        if not self.is_alive or self.is_sleeping:
            return
        
        self._restart_timer()
        self.health.change(-1)

        Log.log(LogType.DEBUG, 'Текущее здоровье: ', self.health.current)

        if self.health.current > (int(self.health.max / 2)):
            return self.msg_func(self.chat_id, f'{self.bot_name} скучает')

        if self.health.current <= (int(self.health.max / 2)) and self.health.current > 0:
            return self.msg_func(self.chat_id, f'{self.bot_name} помирает со скуки')

        if self.health.current <= 0:
            return self.msg_func(self.chat_id, self.die())
       

    def on_pat(self, event) -> str:
        ''' 
            Событие-реакция бота на поглаживание через команду в беседе
            Обновляет таймер
        '''
        #print('Пепе довольно нежится от поглаживаний')
        self._restart_timer()
        self.msg_func(event.chat_id, f'{self.bot_name} довольно нежится от поглаживаний')

    
    def on_message(self, event) -> str:
        ''' 
            Событие-реакция бота на новое сообщение в беседе.
            Обновляет таймер, лечит Пепе (TODO: продумать механику лечения)
            Так же даёт ему немного опыта в зависимости от типа сообщения
        '''
        '''
            TODO: Отдельная реакция на следующий список разных сообщений
            1. Простое текстовое сообщение
            2. Простое сообщение с картинкой
            3. Пересланное текстовое сообщение из ленты
            4. Пересланное сообщение с картинкой из ленты
            5. Пересланное сообщение с несколькими картинками из ленты
            6. Пересланное сообщение с видео из ленты

        '''

        self.health.change(1)
        self._restart_timer()
        self.current_exp += 1
        Log.log(LogType.DEBUG, "Активность! Пепе доволен")

        
        if self.current_exp >= self.next_level_exp:
            self.on_level_up(event)
        
        # С небольшим шансом бот будет как-то комментировать активность в беседе
        if random.randint(0, 9) == 1:
            return self.msg_func(self.chat_id, f'{self.bot_name} довольно облизывается, видя активность в беседе')
        else:
            return ''

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
                + f'Текущий опыт: {self.current_exp}/{self.next_level_exp}\n' \
                + f'Текущее развитие: {self._get_str_state()}'\
                + f'Текущее состояние: {self._get_str_alive_status()}\n'
                )

    def die(self) -> str:
        ''' 
            Событие-реакция бота на снижение здоровья до нуля.
            Останавливает таймер и отключает бота
        '''
        Log.log(LogType.WARNING, f'Пепе из беседы {self.chat_id} умер!')
        self.is_alive = False
        self._stop_timer()
        return self.msg_func(self.chat_id, f'{self.bot_name} издаёт последний вздох, прежде чем отправиться к праотцам')
        
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
        self.progress = PepeProgress.Egg
        
    def go_to_sleep(self, event = None) -> None:
        '''
            Работает только из состояния PepeState.Idle
            Отправляет Пепе спать. Срабатывает по таймеру, но так же может быть вызвана командой.
            Если вызывается командой, то есть шанс, что Пепе обидится и не послушается команды
        '''
        if event is None:
            self.is_sleeping = True

            self.msg_func(self.chat_id, f"{self.bot_name} укладывается спать")
            self._start_func_at_hour(self.wake_up, self.wake_up_time)
        else:
            self.msg_func(self.chat_id, f"{self.bot_name} обидчиво смотрит в сторону того, кто заставляет его лечь спать")
    
    def wake_up(self, event = None) -> None:
        '''
            Работает только из состояния PepeState.Sleep
            Будит Пепе. Срабатывает по таймеру, но так же может быть вызвана командой. 
            При вызове командой ночью (с 12 ночи до 7 утра) Пепе будет ворчать, но не встанет с постели
        '''
        if event is None:
            self.is_sleeping = False
            self.msg_func(self.chat_id, f"{self.bot_name}, потягиваясь, просыпается. Доброе утро!")
            self._start_func_at_hour(self.go_to_sleep, self.go_to_sleep_time)
        else:
            self.msg_func(self.chat_id, f"{self.bot_name} недовольно ворчит, переворачиваясь на другой бок")

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

    def _get_str_state(self):
        if self.progress == PepeProgress.Egg:
            return 'Яйцо'
        if self.progress == PepeProgress.Young:
            return 'Молодой Пепега'
        if self.progress == PepeProgress.Adult:
            return 'Взрослый Пепега'
        if self.progress == PepeProgress.Ancient:
            return 'Мудрый Пепега'  

    def _get_str_alive_status(self):
        if self.is_alive:
            return "Жив"
        else:
            return "Мёртв"
    
    def _generate_name(self):
        '''
            Присваивает случайное имя из списка
        '''
        self.bot_name = '' #TODO: Класс, хранящий в себе все реплики, названия и имена


    def _start_func_at_hour(self, func, hour):
        now = datetime.now()
        run_at = now
        if now.hour <= hour:
            run_at = timedelta(hours=(hour - now.hour), minutes= - now.minute)
        else:
            run_at = timedelta(days=1, hours=(hour - now.hour), minutes= - now.minute)

        threading.Timer(abs(run_at.total_seconds()), func).start()

