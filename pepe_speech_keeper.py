# from pepe_entity import DBWrap
# import random

# class PepeSpeech:
#     '''
#         Возвращает одну случайную реплику из списка на на каждый описанный случай для Пепе
#     '''

#     @staticmethod
#     def on_idle(state, progress) -> str:
#         lst = DBWrap.get_speech(state, progress, PepeSpeech.on_idle.__name__)
#         return lst[random.randint(0, len(lst) - 1)][0]

#     @staticmethod
#     def on_pat(state, progress) -> str:
#         lst = DBWrap.get_speech(state, progress, PepeSpeech.on_pat.__name__)
#         return lst[random.randint(0, len(lst) - 1)][0]

#     @staticmethod
#     def on_level_up(state, progress) -> str:
#         lst = DBWrap.get_speech(state, progress, PepeSpeech.on_level_up.__name__)
#         return lst[random.randint(0, len(lst) - 1)][0]
    
#     @staticmethod
#     def on_message(state, progress) -> str:
#         lst = DBWrap.get_speech(state, progress, PepeSpeech.on_message.__name__)
#         return lst[random.randint(0, len(lst) - 1)][0]

#     @staticmethod
#     def on_night_message(state, progress) -> str:
#         lst = DBWrap.get_speech(state, progress, PepeSpeech.on_night_message.__name__)
#         return lst[random.randint(0, len(lst) - 1)][0]

#     @staticmethod
#     def on_die(state, progress) -> str:
#         lst = DBWrap.get_speech(state, progress, PepeSpeech.on_die.__name__)
#         return lst[random.randint(0, len(lst) - 1)][0]

#     @staticmethod
#     def on_revive(state, progress) -> str:
#         lst = DBWrap.get_speech(state, progress, PepeSpeech.on_revive.__name__)
#         return lst[random.randint(0, len(lst) - 1)][0]