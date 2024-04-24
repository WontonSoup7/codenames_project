import sqlite3

conn = sqlite3.connect('codenames.db')
c = conn.cursor()

c.execute("DROP TABLE IF EXISTS GAME")
#c.execute("DROP TABLE BOARD")
c.execute("DROP TABLE IF EXISTS WORD")
c.execute("DROP TABLE IF EXISTS PROMPT")
c.execute("DROP TABLE IF EXISTS TURN")