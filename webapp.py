import streamlit as st 
import random
import numpy as np
import json 
st.title("Codenames")
from test_prompts import gen_clue
from test_prompts import gen_guess
# RESTART GAME
def clear_ss():
    for key in ss.keys():
        del ss[key]
with st.columns([2, 1, 2])[1]:
    st.button("New Game", on_click=clear_ss)

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
    words_dict[words[-1]] = 3
    random.shuffle(words)
    ss.words = words
    ss.words_dict = words_dict

    # swap these two when all buttons need to be disabled
    ss.clicked = {word:False for word in words_dict}
    ss.all_disabled = {word:True for word in words_dict}
    ss.clicked, ss.all_disabled = ss.all_disabled, ss.clicked
    ss.guessed = {"Red":8, "Blue":8, "Neutral":8, "Assassin":1}
    ss.gs_left = 0
    ss.by_team = {"Red":[], "Blue":[], "Neutral":[], "Assassin":[]}
    for key, val in ss.words_dict.items():   
        ss.by_team[teams[val]].append(key)

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
        ss.game_started = False
        if team == "Red":
            st.text("YOU WIN :)")
        else:
            st.text("YOU LOSE :'(")
        return
    elif team != "Red":
        ss.gs_left = 0

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
            break
        except:
            pass
    print(ss.gs_array)
    for gs in ss.gs_array:
        guess(gs)

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