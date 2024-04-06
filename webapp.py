import streamlit as st 

st.title("Codenames")

# GAME BOARD

#st.write("")



cols = st.columns(5)

#click to guess a word

for i in range(len(cols)):
    with(cols[i]):
        for x in range(5):
            st.button(label=("word" + str(i) + str(x)))

"""
with cols[0]:
    st.button(label="word")
"""

clue = st.text_input(label="Clue", value="Enter clue here")

