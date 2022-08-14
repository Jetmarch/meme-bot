import sqlite3


class DBWrap:
    def __init__(self, db_file_name = 'db.sql') -> None:
        self.con = sqlite3.connect(db_file_name)
    
    def execute_query(self, query):
        cur = self.con.cursor()
        res = cur.execute(query)
        self.con.commit()
        return res.fetchone()

    def __del__(self):
        self.con.close()

#TODO: Специфичные функции для создания таблиц



