import streamlit as st 
import random
import numpy as np

st.title("Codenames")

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
word_list =  open('wordlist-eng.txt', 'r').readlines()
word_list = [word.strip() for word in word_list]

#For now, we will be playing for the red team and trying to guess the red words
#might have to make another page for GPT as the guesser....

# Generate words and assign them
if 'words' not in st.session_state:
    words = random.sample(word_list, 25)
    words_dict = {}
    for i in range(3):
        for j in range(8):
            words_dict[words[8*i + j]] = i
    words_dict[words[-1]] = 3
    random.shuffle(words)
    st.session_state.words = words
    st.session_state.words_dict = words_dict

def click(i):
    st.session_state.test.append(i) #this works
    #st.write(st.session_state)
    #st.color_picker(st.session_state.words[i], "#33FF8D")

if 'board_cols' not in st.session_state:
    cols = st.columns(5)
    buttons = []
    for i in range(len(st.session_state.words)):
        with(cols[i // 5]):
            print(i)
            button = st.button(label=st.session_state.words[i], key=i, on_click=click, args=[i])
            buttons.append(button)
    st.session_state.board_cols = cols
    st.session_state.board_buttons = buttons

# words_dict["blue"] = random.sample(words, 9)
# words_dict["red"] = random.sample([w for w in words if (w not in words_dict["blue"])], 9)
# words_dict["neutral"] = random.sample([w for w in words if (w not in words_dict["blue"] and w not in words_dict["red"])], 6)
# words_dict["assassin"] = random.sample([w for w in words if (w not in words_dict["blue"] and w not in words_dict["red"] and w not in words_dict["neutral"])], 1)   

if 'test' not in st.session_state:
    st.session_state.test = [] 

st.write(st.session_state.words_dict)

#st.write(st.session_state)
