import streamlit as st 
import random
import numpy as np

st.title("Codenames")

# GAME BOARD

word_list =  open('wordlist-eng.txt', 'r').readlines()
word_list = [word.strip() for word in word_list]

#For now, we will be playing for the red team and trying to guess the red words
#might have to make another page for GPT as the guesser....

words = random.sample(word_list, 25)

if 'words' not in st.session_state:
    st.session_state.words = words

words_dict = {}
words_dict["blue"] = random.sample(words, 9)
words_dict["red"] = random.sample([w for w in words if (w not in words_dict["blue"])], 9)
words_dict["neutral"] = random.sample([w for w in words if (w not in words_dict["blue"] and w not in words_dict["red"])], 6)
words_dict["assassin"] = random.sample([w for w in words if (w not in words_dict["blue"] and w not in words_dict["red"] and w not in words_dict["neutral"])], 1)

if 'words_dict' not in st.session_state:
    st.session_state.words_dict = words_dict


con_num = 0
cols = st.columns(5)
buttons = []
for i in range(len(cols)):
    with(cols[i]):
        for x in range(5):
                button = st.button(label=st.session_state.words[(i*5 + x)])
                buttons.append(button)

if 'board_cols' not in st.session_state:
    st.session_state.board_cols = cols

if 'board_buttons' not in st.session_state:
     st.session_state.board_buttons = buttons

if 'button_clicks' not in st.session_state:
    st.session_state.button_clicks = [False] * len(buttons)



#st.write(st.session_state)
