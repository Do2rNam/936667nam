import sqlite3
import os


class FruitDB:
    def __init__(self, path='fruits.db'):
        self.path = path
        init_needed = not os.path.exists(path)
        self.conn = sqlite3.connect(path)
        if init_needed:
            self._init_db()

    def _init_db(self):
        cur = self.conn.cursor()
        cur.execute('''
        CREATE TABLE fruits (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE,
            calories TEXT,
            carbs TEXT,
            sugar TEXT,
            notes TEXT
        )
        ''')
        sample = [
            ('apple','52 kcal/100g','14 g','10 g','Good source of fiber and vitamin C'),
            ('banana','89 kcal/100g','23 g','12 g','High in potassium'),
            ('orange','47 kcal/100g','12 g','9 g','High in vitamin C')
        ]
        cur.executemany('INSERT INTO fruits (name,calories,carbs,sugar,notes) VALUES (?,?,?,?,?)', sample)
        self.conn.commit()

    def get_info(self, name):
        cur = self.conn.cursor()
        cur.execute('SELECT name,calories,carbs,sugar,notes FROM fruits WHERE name = ?', (name,))
        row = cur.fetchone()
        if not row:
            return None
        keys = ['name','calories','carbs','sugar','notes']
        return dict(zip(keys,row))

    def close(self):
        self.conn.close()
