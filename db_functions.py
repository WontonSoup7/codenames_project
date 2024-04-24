import sqlite3

def get_db_connection():
    conn = sqlite3.connect('codenames.db', timeout=60)
    return conn

def insert_word(word, game_id, team, guessed=0):
    conn = get_db_connection()
    try:
        with conn:
            conn.execute("INSERT INTO WORD(WORD, GAME_ID, TEAM, GUESSED) VALUES(?, ?, ?, ?)", (word, game_id, team, guessed))
    finally:
        conn.close()

def insert_game(game_id, type, num_turns=0, win=0):
    conn = get_db_connection()
    try:
        with conn:
            conn.execute("INSERT INTO GAME(ID, TYPE, NUM_TURNS, WIN) VALUES(?, ?, ?, ?)", (game_id, type, num_turns, win))
    finally:
        conn.close()

def fetch_all_games():
    conn = get_db_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM GAME")
            results = cursor.fetchall()
            return results
    finally:
        conn.close()

def fetch_all_prompts():
    conn = get_db_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM PROMPT")
            results = cursor.fetchall()
            return results
    finally:
        conn.close()

def fetch_all_words():
    conn = get_db_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM WORD")
            results = cursor.fetchall()
            return results
    finally:
        conn.close()

def check_game_id_exists_in_db(game_id):
    conn = get_db_connection()
    try:
        with conn:
            cursor = conn.cursor()
            # Note the comma after game_id to make it a tuple
            cursor.execute("SELECT ID FROM GAME WHERE ID = ?", (game_id,))
            results = cursor.fetchall()
            return results
    finally:
        conn.close()

def insert_prompt(game_id, prompt):
    conn = get_db_connection()
    try:
        with conn:
            conn.execute("INSERT INTO PROMPT(GAME_ID, PROMPT) VALUES(?, ?)", (game_id, prompt))
    finally:
        conn.close()