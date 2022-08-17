import sqlite3
from pepe_stat import Stat
from pepe_state import PepeState
from pepe_entity import Pepe

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
        res = self._execute_query_fetchall("SELECT id, name, chat_id, is_alive, current_level, current_exp, current_health, max_health, state FROM t_pepe_entity;")
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
            pepe.state = self._get_pepe_state(data[8])
            list_of_pepe.append(pepe)
        return list_of_pepe
    
    def _get_pepe_state(self, data):
        if data == PepeState.Egg.value:
            return PepeState.Egg
        elif data == PepeState.Young.value:
            return PepeState.Young
        elif data == PepeState.Adult.value:
            return PepeState.Adult
        elif data == PepeState.Ancient.value:
            return PepeState.Ancient

    def add_pepe(self, pepe):
        pass

    def update_pepe(self, pepe: Pepe):
        cur = self.con.cursor()
        cur.execute("UPDATE t_pepe_entity SET is_alive = ?, current_level = ?, current_exp = ?, current_health = ?, max_health = ?, state = ? \
            WHERE id = ?", 
            [pepe.is_alive, pepe.current_level, pepe.current_exp, pepe.health.current, pepe.health.max, pepe.state.value, pepe.bot_id])
        self.con.commit()
        



