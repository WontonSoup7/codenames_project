import streamlit as st 
import random
import numpy as np
import json 
import sqlite3
import string
st.title("Codenames")
from test_prompts import gen_clue
from test_prompts import gen_guess
# RESTART GAME
def clear_ss():
    for key in ss.keys():
        del ss[key]
with st.columns([2, 1, 2])[1]:
    st.button("New Game", on_click=clear_ss)

conn = sqlite3.connect('codenames.db', timeout=60)
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

# c.execute("INSERT INTO BOARD(WORD, TEAM, GUESSED) VALUES ('W', 'RED', '1')")
# conn.commit()
# c.execute("SELECT WORD FROM BOARD")
# w = c.fetchone()
#st.write(w)
#st.title(w)

ss = st.session_state
# Dummy api calls for testing
# def gen_clue():
#     return ["Baseball", 3]

# def gen_guess(words):
#     guess = words[random.randrange(0, 24)]
#     while isinstance(words[guess], int):
#         guess = words[random.randrange(0, 24)]
#     return guess

teams = ["Red", "Blue", "Neutral", "Assassin"]



# Generate words and assign them
if 'words' not in ss:
    word_list =  open('wordlist-eng.txt', 'r').readlines()
    word_list = [word.strip() for word in word_list]
    words = random.sample(word_list, 25)
    words_dict = {}
    for i in range(3):
        for j in range(8):
            words_dict[words[8*i + j]] = i
            #add the words to the db
            #if (i == 0 and j == 0):
            #    c.execute(f"INSERT INTO BOARD()")
    words_dict[words[-1]] = 3
    random.shuffle(words)
    ss.words = words
    ss.words_dict = words_dict

    #st.write("WORD DICT: ", words_dict) #delete later

    # swap these two when all buttons need to be disabled
    ss.clicked = {word:False for word in words_dict}
    ss.all_disabled = {word:True for word in words_dict}
    ss.clicked, ss.all_disabled = ss.all_disabled, ss.clicked
    ss.guessed = {"Red":8, "Blue":8, "Neutral":8, "Assassin":1}
    ss.gs_left = 0
    ss.by_team = {"Red":[], "Blue":[], "Neutral":[], "Assassin":[]}
    for key, val in ss.words_dict.items():   
        ss.by_team[teams[val]].append(key)

    #new addition
    ss.num_turns = 0

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

def insert_game(game_id, num_turns=0, win=0):
    conn = get_db_connection()
    try:
        with conn:
            conn.execute("INSERT INTO GAME(ID, NUM_TURNS, WIN) VALUES(?, ?, ?)", (game_id, num_turns, win))
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

def generate_unique_game_id():
    new_game_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    while check_game_id_exists_in_db(new_game_id):
        new_game_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return new_game_id

# Use this function to set ss.game_id when needed, not at the top level of your script
if 'game_id' not in ss:
    ss.game_id = generate_unique_game_id()



# #add words to the db
# for key, val in ss.words_dict.items():
#     #c.execute("INSERT INTO BOARD (ID, WORD, TEAM) VALUES (?, ?, ?)", (ss.board_id, key, val))
#     c.execute("INSERT INTO WORD (WORD, GAME_ID, TEAM) VALUES(?, ?, ?)", (key, ss.game_id, val))
#     conn.commit()
# c.execute("INSERT INTO GAME(ID) VALUES(?)", (ss.game_id,))
# conn.commit()


ss = ss
if 'test' not in ss:
    ss.test = [] 
if 'cm_logs' not in ss:
    ss.cm_logs = []
    ss.gs_logs = []



# GAME BOARD BUTTON CALLBACK
def guess(name):
    team = teams[ss.words_dict[name]]
    ss.gs_logs[-1].append(name)
    ss.gs_left -= 1
    ss.guessed[team] -= 1
    ss.by_team[team].remove(name)
    if not ss.guessed[team] and team != "Neutral":
        toggle_board()
        for key, val in ss.words_dict.items():
            tm = teams[val]
            if (key not in ss.by_team[tm]): #word has been guessed
                #c.execute("INSERT INTO WORD(WORD, GAME_ID, TEAM, GUESSED) VALUES(?, ?, ?, ?)", (key, ss.game_id, tm, 1)) 
                insert_word(key, ss.game_id, tm, 1)
            else: #word was not guessed, the value for the guessed column is 0 by default
                #c.execute("INSERT INTO WORD(WORD, GAME_ID, TEAM) VALUES(?, ?, ?)", (key, ss.game_id, tm))
                insert_word(key, ss.game_id, tm)
        #conn.commit()
        if team == "Red":
            st.text("YOU WIN :)")
            #c.execute("INSERT INTO GAME(ID, WIN) VALUES(?, ?)", (ss.game_id, 1))
            insert_game(game_id=ss.game_id, num_turns=ss.num_turns, win=1)
        else:
            st.text("YOU LOSE :'(")
            #c.execute("INSERT INTO GAME(ID, WIN) VALUES(?, ?)", (ss.game_id, 0))
            insert_game(game_id=ss.game_id, num_turns=ss.num_turns, win=0)
    

        #JUST for test purposeses- delete these next lines (after this comment and before return) later
        #c.execute("SELECT * FROM GAME")
        #game_data = c.fetchall()
        game_data = fetch_all_games()
        st.text(game_data)
        #c.execute("SELECT * FROM WORD")
        #word_data = c.fetchall()
        word_data = fetch_all_words()
        st.text(word_data)

        return
    elif team != "Red":
        ss.gs_left = 0
        ss.num_turns += 1 #increment number of turns after incorrect guess

    ss.clicked[name] = not ss.clicked[name]

def do_nothing(name):
    pass


if "game_started" not in ss:
    ss.game_started = False
    ss.disable_user_input = True
def toggle_board():
    ss.clicked, ss.all_disabled = ss.all_disabled, ss.clicked
def codemaster():
    ss.role = 0
    ss.disable_user_input = False
    toggle_board()
    ss.game_started = True
def guesser():
    ss.role = 1
    toggle_board()
    ss.game_started = True
cols_play = st.columns([.5, 1, 1, .5], gap="large")
with cols_play[1]: cm_btn = st.button(label = "Play as CodeMaster", on_click=codemaster, disabled=ss.game_started)
with cols_play[2]: g_btn = st.button(label = "Play as Guesser", on_click=guesser, disabled=ss.game_started)

bt_guess = do_nothing
if ss.game_started:
    if ss.gs_left == 0:
        # Guesser
        if ss.role:
            # FOR DEVELOPMENT ONLY
            while True:
                try:
                    ss.clue = gen_clue(ss.by_team['Red'], ss.by_team['Blue'],
                                    ss.by_team['Neutral'], ss.by_team['Assassin'])
                    # st.text(ss.clue)
                    ss.clue = ss.clue.split(":")
                    ss.clue_word, ss.gs_left = ss.clue[0], int(ss.clue[1])
                    if ss.clue_word.upper() not in ss.words:
                        break
                except:
                    pass
            print(ss.clue_word, ss.gs_left)
            ss.cm_logs.append(ss.clue)
            ss.gs_logs.append([])
            bt_guess = guess
        # Codemaster
        # TODO: Get user input for guess
        else:
            if "clue" in ss:
                del ss['clue']
            bt_guess = do_nothing
            ss.disable_user_input = False
    else:
        bt_guess = guess
        if not ss.role:
            bt_guess = do_nothing
            ss.disable_user_input = True



def parse_clue():
    ss.clue = ss.user_input.split(": ")
    ss.clue[1] = int(ss.clue[1])
    ss.clue_word, ss.gs_left = ss.clue
    ss.cm_logs.append(ss.clue)
    ss.gs_logs.append([])
    ss.user_input = ""

def call_guesser():
    # FOR DEVELOPMENT ONLY
    while True:
        try:
            parse_clue()
            ss.gs_array = json.loads(gen_guess(json.dumps(ss.clue), ss.words))
            for gs in ss.gs_array:
                guess(gs)
            break
        except:
            ss.user_input = ""
            break

txt_input = st.text_input(label= "Enter Clue",
    key = "user_input",
    label_visibility="collapsed",
    placeholder= "Word: Number",
    disabled=ss.disable_user_input,
    on_change=call_guesser)

if "clue" in ss:
    st.text(ss.clue_word + ": " + str(ss.clue[1])) 
    st.text("Guesses remaining: " + str(ss.gs_left))
elif "role" in ss and not ss.role:
    st.text("Please enter a clue")
# GAME BOARD
cols = st.columns(5)
for i in range(len(ss.words)):
    with(cols[i // 5]):
        name = ss.words[i]
        st.button(label=name, key=name, 
                  on_click=bt_guess, args=[name],
                  disabled=ss.clicked[name])

st.write(ss.guessed)
# REVEAL TEAMS   
rev_teams = st.checkbox(label="Teams", value=True)
if rev_teams: 
    for key, val in ss.by_team.items():
        st.text(key + ": " + json.dumps(val))

for i in range(len(ss.cm_logs)):
    st.text("Clue: ")
    st.text(ss.cm_logs[i])
    st.text("Guesses: ")
    st.text(ss.gs_logs[i])