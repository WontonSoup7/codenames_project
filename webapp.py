import streamlit as st 
import random
import numpy as np
import json 
st.title("Codenames")

ss = st.session_state
# Dummy api calls for testing
def generate_clue():
    return ""

def generate_guess(words):
    guess = words[random.randrange(0, 24)]
    while isinstance(words[guess], int):
        guess = words[random.randrange(0, 24)]
    return guess

teams = ["Red", "Blue", "Neutral", "Assassin"]

# GAME BOARD


#For now, we will be playing for the red team and trying to guess the red words
#might have to make another page for GPT as the guesser....

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

    ss.guessed = {"Red":8, "Blue":8, "Neutral":8, "Assassin":1}
    ss.by_team = {"Red":[], "Blue":[], "Neutral":[], "Assassin":[]}
    for key, val in ss.words_dict.items():   
        ss.by_team[teams[val]].append(key)

# words_dict["blue"] = random.sample(words, 9)
# words_dict["red"] = random.sample([w for w in words if (w not in words_dict["blue"])], 9)
# words_dict["neutral"] = random.sample([w for w in words if (w not in words_dict["blue"] and w not in words_dict["red"])], 6)
# words_dict["assassin"] = random.sample([w for w in words if (w not in words_dict["blue"] and w not in words_dict["red"] and w not in words_dict["neutral"])], 1)   

# for key, val in enumerate(ss.guessed):
ss = ss
if 'test' not in ss:
    ss.test = [] 

if 'logs' not in ss:
    ss.logs = []

def click(name):
    team = teams[ss.words_dict[name]]
    ss.logs.append(name + ": " + team)
    ss.guessed[team] -= 1
    ss.by_team[team].remove(name)
    if not ss.guessed[team] and team != "Neutral":
        ss.clicked, ss.all_disabled = ss.all_disabled, ss.clicked
        return
    ss.clicked[name] = not ss.clicked[name]
    #this works
    #st.write(ss)
    #st.color_picker(ss.words[i], "#33FF8D")

st.write(ss.guessed)
rev_teams = st.checkbox(label="Teams", value=False)
if rev_teams: 
    for key, val in ss.by_team.items():
        st.text(key + ": " + json.dumps(val))

cols = st.columns(5)
for i in range(len(ss.words)):
    with(cols[i // 5]):
        name = ss.words[i]
        st.button(label=name, key=name, 
                  on_click=click, args=[name],
                  disabled=ss.clicked[name])

# st.write(ss.logs)
# st.write(ss.guessed)
# st.write(ss.words_dict)

