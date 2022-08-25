from enum import Enum

# Каждое значение обозначает уровень, требуемый для получения нового статуса
class PepeProgress(Enum):
    Egg = 1
    Young = 2
    Adult = 15
    Ancient = 50