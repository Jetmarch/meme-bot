import sqlite3
from pepe_entity import Pepe, Stat

class DBWrap:
    def __init__(self, db_file_name = 'db.sql') -> None:
        self.con = sqlite3.connect(db_file_name)
    
    def _execute_query_fetchone(self, query):
        cur = self.con.cursor()
        res = cur.execute(query)
        self.con.commit()
        return res.fetchone()
    
    def _execute_query_fetchall(self, query):
        cur = self.con.cursor()
        res = cur.execute(query)
        self.con.commit()
        return res.fetchall()

    def __del__(self):
        self.con.close()

    def get_all_pepe(self):
        res = self._execute_query_fetchall("SELECT id, name, chat_id, is_alive, current_level, current_exp, current_health, max_health FROM t_pepe_entity;")
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
            list_of_pepe.append(pepe)
        return list_of_pepe
    
    def add_pepe(self, pepe):
        pass

    def update_pepe(self, pepe: Pepe):
        cur = self.con.cursor()
        cur.execute("UPDATE t_pepe_entity SET is_alive = ?, current_level = ?, current_exp = ?, current_health = ?, max_health = ?", 
            [pepe.is_alive, pepe.current_level, pepe.current_exp, pepe.health.current, pepe.health.max])
        self.con.commit()
        



