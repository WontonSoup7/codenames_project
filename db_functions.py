import sqlite3
import json

def get_db_connection():
    conn = sqlite3.connect('3.5oneshotgvg.db', timeout=60)
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
                GAME_ID TEXT,
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
            CREATE TRIGGER IF NOT EXISTS update_wl_ratio AFTER UPDATE OF WINS, LOSSES ON PROMPT
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

def update_prompt_after_win_loss(prompt_id, game_id, win=True):
    conn = get_db_connection()
    try:

        c = conn.cursor()

        c.execute("""SELECT GAMES FROM PROMPT WHERE ID = ?""", (prompt_id,))
        row = c.fetchone()
        current_games = json.loads(row[0]) if row and row[0] else []
        current_games.append(game_id)
        updated_games = json.dumps(current_games)

        if(win):
            conn.execute("""
            UPDATE PROMPT
            SET WINS = WINS + 1,
                GAMES = ?
            WHERE ID = ?
            """, (updated_games, prompt_id))
            conn.commit()
        else:
            conn.execute("""
            UPDATE PROMPT
            SET LOSSES = LOSSES + 1,
                GAMES = ?
            WHERE ID = ?
            """, (updated_games, prompt_id))
            conn.commit()
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()


def fetch_top_n(table_name, col_name, n):
    conn = get_db_connection()
    try:
        c = conn.cursor()
        c.execute("""SELECT {} 
                  FROM {}
                  ORDER BY {} DESC
                  LIMIT {};""".format(col_name, table_name, col_name, n))
        res = c.fetchall()
        return res
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

# def update_prompt_after_loss(game_id):
#     conn = get_db_connection()
#     try:
#         conn.execute("""
#             UPDATE PROMPT
#             SET LOSSES = LOSSES + 1
#             WHERE ID = ?
#         """, (game_id, ))
#         conn.commit()
#     except Exception as e:
#         print(f"An error occurred: {e}")
#     finally:
#         conn.close()


def get_prompt_id(prompt_text, guesser=True):
    #select and return the prompt id for a guesser prompt if guesser = True (otherwise return id for CM prompt)
    conn = get_db_connection()
    c = conn.cursor()
    try:
        if guesser:
            c.execute("""SELECT ID FROM PROMPT WHERE GUESSER_PROMPT = ?""", (prompt_text,))
        else:
            c.execute("""SELECT ID FROM PROMPT WHERE CM_PROMPT = ?""", (prompt_text,))
        id = c.fetchone()
        return id[0] if id else None
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

def update_turn_trigger():
    #create a trigger so that the correct clue num ratio gets recalculated after an update of num_correct on turn
    conn = get_db_connection()
    try:
        conn.execute("""
            CREATE TRIGGER IF NOT EXISTS update_correct_clue_num_ratio
            AFTER UPDATE OF NUM_CORRECT, CLUE_NUM ON TURN
            BEGIN
                UPDATE TURN
                SET CORRECT_CLUE_NUM_RATIO = CASE
                    WHEN NEW.CLUE_NUM > 0 THEN CAST(NEW.NUM_CORRECT AS REAL) / NEW.CLUE_NUM
                    ELSE 0
                END
                WHERE ID = NEW.ID;
            END;
        """)
        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()
    

def update_turn_after_guess(guess="", correct=True):
    conn = get_db_connection()
    #correct is whether the guess was correct or not
    #updated_clue_guesses is the updated array of clue guesses (as a string)
    try:
        c = conn.cursor()

        c.execute("""SELECT MAX(ID) FROM TURN""")
        row = c.fetchone()
        current_turn = row[0] if row else None

        print(f"--------------\n ROW:  {row[0]} \n-------------------")

        if current_turn:
            c.execute("""SELECT CLUE_GUESSES FROM TURN WHERE ID = ?""", (current_turn,))
            row = c.fetchone()
            updated_clue_guesses = json.loads(row[0]) if row and row[0] else []
            updated_clue_guesses.append(guess)
            updated_clue_guesses = json.dumps(updated_clue_guesses)

            if correct:
                conn.execute("""
                UPDATE TURN
                SET CLUE_GUESSES = ?, NUM_CORRECT = NUM_CORRECT + 1
                WHERE ID = ?
                """, (updated_clue_guesses, current_turn))
            else:
                #don't incrememnt num_correct because the guess was incorrect
                conn.execute("""
                UPDATE TURN
                SET CLUE_GUESSES = ?
                WHERE ID = ?
                """, (updated_clue_guesses, current_turn))
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

def insert_game(game_id, num_turns=0, win=0):
    conn = get_db_connection()
    try:
        with conn:
            conn.execute("INSERT INTO GAME(ID, NUM_TURNS, WIN) VALUES(?, ?, ?)", (game_id, num_turns, win))
            conn.commit()
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

def fetch_all_turns():
    conn = get_db_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM TURN")
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

def get_prompt_id(prompt_text, guesser):
    #if guesser = 1, check if the prompt text exists in the guesser column, else check if it exists in the cm column
    conn = get_db_connection()
    #if guesser = 1, insert as guesser prompt, otherwise insert as cm prompt
    try:
        with conn:
            c = conn.cursor()
            p = None
            if guesser:
                c.execute("""SELECT ID FROM PROMPT WHERE GUESSER_PROMPT = ? AND CM_PROMPT IS NULL""", (prompt_text, ))
            else:
                c.execute("""SELECT ID FROM PROMPT WHERE CM_PROMPT = ? AND GUESSER_PROMPT IS NULL""", (prompt_text, ))
            p = c.fetchone()
            if p:
                p = p[0]
            return p # will return None if the prompt does not exist in the table
    finally:
        conn.close()

def get_prompt_id_gvg(cm_prompt, guesser_prompt=None):
    #if guesser = 1, check if the prompt text exists in the guesser column, else check if it exists in the cm column
    conn = get_db_connection()
    #if guesser = 1, insert as guesser prompt, otherwise insert as cm prompt
    try:
        with conn:
            c = conn.cursor()
            p = None
            if guesser_prompt:
                c.execute("""SELECT ID FROM PROMPT WHERE CM_PROMPT = ? AND GUESSER_PROMPT = ?""", (cm_prompt, guesser_prompt))
            else:
                c.execute("""SELECT ID FROM PROMPT WHERE CM_PROMPT = ? AND GUESSER_PROMPT IS NOT NULL""", (cm_prompt, ))
            p = c.fetchone()
            if p:
                p = p[0]
            return p # will return None if the prompt does not exist in the table
    finally:
        conn.close()

def insert_prompt(game_id, prompt, guesser):
    conn = get_db_connection()
    #if guesser = 1, insert as guesser prompt, otherwise insert as cm prompt
    try:
        with conn:
            game_ids = [game_id]
            if guesser:
                if (get_prompt_id(prompt, guesser) == None): #if prompt doesn't already exist in db
                    conn.execute("INSERT INTO PROMPT(GAMES, GUESSER_PROMPT, CM_PROMPT) VALUES(?, ?, NULL)", (json.dumps(game_ids), prompt)) 
                    conn.commit()
                    return get_prompt_id(prompt, guesser)   
            else:
                if (get_prompt_id(prompt, guesser) == None):
                    conn.execute("INSERT INTO PROMPT(GAMES, CM_PROMPT, GUESSER_PROMPT) VALUES(?, ?, NULL)", (json.dumps(game_ids), prompt))
                    conn.commit()
                    return get_prompt_id(prompt, guesser)
    finally:
        conn.close()

def insert_prompt_gvg(game_id, cm_prompt, guesser_prompt=None):
    conn = get_db_connection()
    try:
        with conn:
            game_ids = [game_id]
            if ((guesser_prompt==None) and (get_prompt_id_gvg(cm_prompt)==None)):
                conn.execute("INSERT INTO PROMPT(GAMES, CM_PROMPT, GUESSER_PROMPT) VALUES (?, ?, ?)", (json.dumps(game_ids), cm_prompt, 'x'))
                conn.commit()
                return get_prompt_id_gvg(cm_prompt, 'x')
            elif (get_prompt_id_gvg(cm_prompt, guesser_prompt)==None):
                conn.execute("INSERT INTO PROMPT(GAMES, CM_PROMPT, GUESSER_PROMPT) VALUES (?, ?, ?)", (json.dumps(game_ids), cm_prompt, guesser_prompt))
                conn.commit()
                return get_prompt_id_gvg(cm_prompt, guesser_prompt)
            return get_prompt_id_gvg(cm_prompt, guesser_prompt)
    finally:
        conn.close()

#used only for gvg
def update_row_for_guesser_prompt(prompt_id, game_id, cm_prompt, guesser_prompt):
    conn = get_db_connection()
    try:
        c = conn.cursor()
        c.execute("""SELECT GUESSER_PROMPT FROM PROMPT WHERE ID = ? AND CM_PROMPT = ?""", (prompt_id, cm_prompt))

        g_prompt = c.fetchone()[0]
        if not g_prompt:
            raise Exception("g_prompt is None")

        #print(f""" ~~~~~~ /n UPDATING {g_prompt}""")

        #if the guesser_prompt does not exist for the row with that prompt id, 
        #for gvg the guesser_prompt column will be set to 'x' at first upon insertion to distinguish it from human vs gpt
        if (g_prompt=='x'): 
            conn.execute("""
            UPDATE PROMPT
            SET GUESSER_PROMPT = ?
            WHERE ID = ?
                """, (guesser_prompt, prompt_id))
            print("ID: ", str(prompt_id))
            conn.commit()
        #if there is a different guesser prompt in that row, create a new row with the cm_prompt and the guesser_prompt
        else:
            #g_prompt = g_prompt[0]
            if (g_prompt != guesser_prompt):
                print("hello")
                game_ids = [game_id]
                conn.execute("""INSERT INTO PROMPT(CM_PROMPT, GAMES, GUESSER_PROMPT) VALUES(?, ?, ?)""", (cm_prompt, json.dumps(game_ids), guesser_prompt))
                conn.commit()    
        return get_prompt_id_gvg(cm_prompt, guesser_prompt)   
    finally:
        conn.close()


def insert_turn(game_id, red_words, blue_words, neutral_words, assassin_words, clue_word, clue_num):
    conn = get_db_connection()
    try:
        with conn:
            conn.execute("""INSERT INTO TURN(GAME_ID, RED_WORDS, BLUE_WORDS, NEUTRAL_WORDS, ASSASSIN_WORDS, CLUE_WORD, CLUE_NUM)
                         VALUES(?, ?, ?, ?, ?, ?, ?)""", (game_id, red_words, blue_words, neutral_words, assassin_words, clue_word, clue_num))
            conn.commit()
    finally:
        conn.close()

def add_triggers():
    add_prompt_wl_ratio_trigger()
    update_turn_trigger()