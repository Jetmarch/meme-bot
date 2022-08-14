


class Pepe:
    chat_id = 0
    is_alive = True
    is_hungry = False
    is_happy = True

    exp_counter = 0
    current_level = 0
    next_level_exp = 0


    def __init__(self) -> None:
        pass
    
    # Каждый час бездействия в беседе здоровье Пепе снижается на один пункт
    # Количество здоровья зависит от уровня Пепе

    # Отложить снижение здоровья можно погладив его
    # 

