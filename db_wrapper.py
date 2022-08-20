# import sqlite3
# from pepe_stat import Stat
# from pepe_progress import PepeProgress
# from pepe_entity import Pepe

# class DBWrap:
#     db_file_name = 'db.sql'
#     con = sqlite3.connect(db_file_name)
    
#     @staticmethod
#     def _execute_query_fetchone(query):
#         cur = DBWrap.con.cursor()
#         res = cur.execute(query)
#         DBWrap.con.commit()
#         return res.fetchone()
    
#     @staticmethod
#     def _execute_query_fetchall(query):
#         cur = DBWrap.con.cursor()
#         res = cur.execute(query)
#         DBWrap.con.commit()
#         return res.fetchall()

#     @staticmethod
#     def close():
#         DBWrap.con.close()

#     @staticmethod
#     def get_all_pepe():
#         res = DBWrap._execute_query_fetchall("SELECT id, name, chat_id, is_alive, current_level, current_exp, current_health, max_health, state FROM t_pepe_entity;")
#         list_of_pepe = []
#         for data in res:
#             pepe = Pepe()
#             pepe.bot_id = data[0]
#             pepe.bot_name = data[1]
#             pepe.chat_id = data[2]
#             pepe.is_alive = data[3]
#             pepe.current_level = data[4]
#             pepe.current_exp = data[5]
#             pepe.health = Stat(data[7], data[6])
#             pepe.progress = DBWrap._get_pepe_state(data[8])
#             list_of_pepe.append(pepe)
#         return list_of_pepe
    
#     @staticmethod
#     def _get_pepe_state(data):
#         if data == PepeProgress.Egg.value:
#             return PepeProgress.Egg
#         elif data == PepeProgress.Young.value:
#             return PepeProgress.Young
#         elif data == PepeProgress.Adult.value:
#             return PepeProgress.Adult
#         elif data == PepeProgress.Ancient.value:
#             return PepeProgress.Ancient

#     @staticmethod
#     def add_pepe(pepe):
#         pass

#     @staticmethod
#     def update_pepe(pepe: Pepe):
#         cur = DBWrap.con.cursor()
#         cur.execute("UPDATE t_pepe_entity SET is_alive = ?, current_level = ?, current_exp = ?, current_health = ?, max_health = ?, state = ? \
#             WHERE id = ?", 
#             [pepe.is_alive, pepe.current_level, pepe.current_exp, pepe.health.current, pepe.health.max, pepe.progress.value, pepe.bot_id])
#         DBWrap.con.commit()
    
#     @staticmethod
#     def get_speech(state, progress, event_name):
#         cur = DBWrap.con.cursor()
#         res = cur.execute("SELECT speech FROM t_speech WHERE state = ? and progress = ? and event = ?;", [state, progress, event_name])
#         ls = []
#         for speech in res.fetchall():
#             ls.append(speech)
#         return ls