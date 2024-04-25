import sqlite3

def get_db_connection():
    conn = sqlite3.connect('codenames.db', timeout=60)
    return conn

def create_tables():
    conn = get_db_connection()
    try:
        with conn:
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS GAME(
                ID TEXT PRIMARY KEY,
                NUM_TURNS INT NOT NULL DEFAULT 0,
                WIN BOOLEAN
                )""")
            c.execute("""
                CREATE TABLE IF NOT EXISTS WORD(
                WORD TEXT,
                GAME_ID TEXT,
                TEAM TEXT,    -- 'red', 'blue', 'neutral', or 'assassin'
                GUESSED BOOLEAN NOT NULL DEFAULT 0,
                PRIMARY KEY (WORD, GAME_ID),
                FOREIGN KEY (GAME_ID) REFERENCES GAME(ID) ON DELETE CASCADE
                )""")
            c.execute("""
                CREATE TABLE IF NOT EXISTS TURN(
                ID INTEGER PRIMARY KEY,
                RED_WORDS TEXT,
                BLUE_WORDS TEXT,
                NEUTRAL_WORDS TEXT,
                ASSASSIN_WORDS TEXT,
                CLUE_NUM INT,
                CLUE_WORD TEXT,
                CLUE_GUESSES TEXT,
                NUM_CORRECT INT NOT NULL DEFAULT 0,
                CORRECT_CLUE_NUM_RATIO REAL NOT NULL DEFAULT 0
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS PROMPT(
                ID INTEGER PRIMARY KEY,
                CM_PROMPT TEXT,
                GUESSER_PROMPT TEXT,
                GAMES TEXT,
                WINS INT NOT NULL DEFAULT 0,
                LOSSES INT NOT NULL DEFAULT 0,
                WL_RATIO REAL
                )
            """)
            conn.commit()
    finally:
        conn.close()


def add_prompt_wl_ratio_trigger():
    conn = get_db_connection()
    try:
        conn.execute("""
            CREATE TRIGGER update_wl_ratio AFTER UPDATE OF WINS, LOSSES ON PROMPT
            BEGIN
                UPDATE PROMPT
                SET WL_RATIO = CASE
                    WHEN NEW.LOSSES > 0 THEN CAST(NEW.WINS AS REAL) / NEW.LOSSES
                    ELSE NULL
                END
            WHERE ID = NEW.ID;
        END;          
    """)
    finally:
        conn.close()

def update_prompt_after_win(game_id):
    conn = get_db_connection()
    try:
        conn.execute("""
            UPDATE PROMPT
            SET WINS = WINS + 1
            WHERE ID = ?
        """, (game_id, ))
        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

def update_prompt_after_loss(game_id):
    conn = get_db_connection()
    try:
        conn.execute("""
            UPDATE PROMPT
            SET LOSSES = LOSSES + 1
            WHERE ID = ?
        """, (game_id, ))
        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()


def get_prompt_id(guesser, prompt_text):
    #select and return the prompt id for a guesser prompt if guesser = True (otherwise return id for CM prompt)
    conn = get_db_connection()
    c = conn.cursor()
    try:
        if guesser:
            c.execute("""SELECT ID FROM PROMPT WHERE GUESSER_PROMPT = ?""", (prompt_text,))
        else:
            c.execute("""SELECT ID FROM PROMPT WHERE CM_PROMPT = ?""", (prompt_text,))
        id = c.fetchone()
        return id
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

def update_turn_trigger():
    #create a trigger so that the correct clue num ratio gets recalculated after an update of num_correct on turn
    conn = get_db_connection()
    #...

def update_turn_after_guess(prompt_id, updated_clue_guesses, correct):
    conn = get_db_connection()
    #correct is whether the guess was correct or not
    #updated_clue_guesses is the updated array of clue guesses (as a string)
    try:
        if correct:
            conn.execute("""
            UPDATE TURN
            SET CLUE GUESSES = ?, NUM_CORRECT = NUM_CORRECT + 1
            WHERE PROMPT_ID = ?
            """, (prompt_id, updated_clue_guesses))
        else:
            conn.execute("""""")
        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

def drop_tables():
    conn = get_db_connection()
    try:
        conn.execute("DROP TABLE IF EXISTS PROMPT ON DELETE CASCADE")
        conn.execute("DROP TABLE IF EXISTS WORD ON DELETE CASCADE")
        conn.execute("DROP TABLE IF EXISTS TURN ON DELETE CASCADE")
        conn.execute("DROP TABLE IF EXISTS GAME ON DELETE CASCADE")
    finally:
        conn.close()
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