import threading


class Pepe:
    chat_id = 0
    is_alive = True
    is_hungry = False
    is_happy = True

    current_exp = 0
    next_level_exp = 0

    # Каждый час
    time_to_idle = 1 #60 * 60

    def __init__(self) -> None:
        self.happiness = Stat(10)
        self.health = Stat(10)
        self.is_alive = True
        self._set_timer()

    def on_idle(self) -> None:
        ''' 
            Событие-реакция бота на отсутствие сообщений в течение определённого времени в беседе.
            Снижает уровень здоровья и оповещает об этом всех участников беседы
        '''

        if not self.is_alive:
            return
        
        self.health.change(-1)
        print(self.health.current)

        if self.health.current > (int(self.health.max / 2)):
            print('Пепе скучает')
            self._restart_timer()

        if self.health.current <= (int(self.health.max / 2)) and self.health.current > 0:
            print('Пепе помирает со скуки')
            self._restart_timer()
        
        if self.health.current <= 0:
            self.die()
       

    def on_pat(self, event) -> None:
        ''' 
            Событие-реакция бота на поглаживание через команду в беседе
            Обновляет таймер
        '''

        print('Пепе довольно нежится от поглаживаний')
        self._restart_timer()

    '''
        TODO: Отдельная реакция на следующий список разных сообщений
        1. Простое текстовое сообщение
        2. Простое сообщение с картинкой
        3. Пересланное текстовое сообщение из ленты
        4. Пересланное сообщение с картинкой из ленты
        5. Пересланное сообщение с несколькими картинками из ленты
        6. Пересланное сообщение с видео из ленты

    '''
    def on_message(self, event) -> None:
        ''' 
            Событие-реакция бота на новое сообщение в беседе.
            Обновляет таймер, лечит Пепе (TODO: продумать механику лечения)
            Так же даёт ему немного опыта в зависимости от типа сообщения
        '''

        print('Пепе довольно облизывается, поедая мем из поста сверху')
        self._restart_timer()

    def on_level_up(self, event) -> None:
        ''' 
            Событие-реакция бота на поднятие уровня.
            Обновляет здоровье до максимального
            и устанавливает другой статус Пепе.
            Так же устанавливает следующие границы для повышения уровня
        '''
        #Вычисление количества опыта для следующего уровня происходят по формуле (x * x) * 0.65
        pass
    
    def get_bot_info(self) -> None:
        '''
            Возвращает информацию о Пепе:
            * Текущий уровень, количество текущего опыта / количество опыта до следующего уровня
            * Текущий уровень здоровья / максимальный уровень здоровья
            * Картинку его статуса (яйцо, маленький Пепе, Пепе-подросток, Пепе-взрослый, Пепе-мудрец)
            * TODO: Продумать несколько промежуточных статусов
        '''

    def die(self) -> None:
        ''' 
            Событие-реакция бота на снижение здоровья до нуля.
            Останавливает таймер и отключает бота
        '''

        print('Пепе издаёт последний вздох, прежде чем отправиться к праотцам')
        self._stop_timer()
    
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

        pass

    
    
    # Каждый час бездействия в беседе здоровье Пепе снижается на один пункт
    # Количество здоровья зависит от уровня Пепе

    # Отложить снижение здоровья можно погладив его
    # 

class Stat:
    def __init__(self, max_amount, current_amount = 0) -> None:
        self.max = max_amount
        if current_amount == 0:
            self.current = max_amount
        else:
            self.current = current_amount

    def change(self, value) -> None:
        self.current += value

    def restore(self) -> None:
        self.current = self.max

p = Pepe()
event = 'str'
timer = threading.Timer(5, p.on_pat, [event])
timer.start()