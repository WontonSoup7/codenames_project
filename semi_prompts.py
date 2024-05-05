# PROMPTS FROM SEMI 
# Prompt asks for explanation

from openai import OpenAI # type: ignore
# import random

from dotenv import load_dotenv # type: ignore
import os
import csv

# Load your API key from an environment variable
load_dotenv()
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")
client = OpenAI(api_key=OPEN_AI_API_KEY)

# Define the Codenames board (25 words for simplicity)
board_words = [
    "Egypt", "Pitch", "Deck", "Well", "Fair",
    "Tooth", "Staff", "Bill", "Shot", "King",
    "Pan", "Square", "Press", "Seal", "Bear",
    "Spike", "Center", "Face", "Palm", "Crane",
    "Rock", "Stick", "Tag", "Disease", "Yard"
]

# Teams' words (for simplicity, not used in clue generation/guessing logic here)
team_red_words = ["Egypt", "Pitch", "Deck", "Well", "Fair", "Tooth", "Staff", "Bill", "Shot"]
team_blue_words = ["King", "Pan", "Square", "Press", "Seal", "Bear", "Spike", "Center", "Face"]
neutral_words = ["Palm", "Crane", "Rock", "Stick", "Tag", "Disease", "Yard"]
assassin_word = ["Battery"] #was originally "Pitch" but that is a red team word so i wanted it to be different

def create_prompt(template, replacements):  
    return template.format(**replacements)

def gen_clue(red_words, blue_words, neutral_words, assassin_word):
    prompt = """
    Give a clue that represents some of the words from the list in some way.
    (Note: Your clue may not be any of these words):
    Red words: {red_words} 
    Blue words: {blue_words}
    Civilian words: {neutral_words}
    Assassin: {assassin_word}.
    The clue MUST relate to EACH words it aims to indicate.
    Clues must be easy.
    The clue number may not be more than the amount of red words.
    Your clue may not have appeared in any of these words and must be one word only. 
    The clue must be in the format "Clue: Word,Number". For example "Clue: Bird,3"
    
    Below is the example:
    ___
    Input:
    Red words: [BOMB, OPERA, PISTOL, BARK, BATTERY, DISEASE, ROW, BEAR]
    Blue words: [MARBLE, MILLIONAIRE, PORT, BOTTLE, TAP, VAN, NEEDLE, PUMPKIN]
    Assassin word: [KNIGHT]
    Civilian words: [BAR, ICE, BERLIN, PLOT, CYCLE, BOLT, RULER, CAT]
    Output:
    Clue: Loud, 4
    Answer: 
    [BOMB, OPERA, PISTOL, BARK]
    ___
    Output the Clue and related words in list format, put explanation in the last line. The response must be in 3 lines: clue in the first line and the list in the order.
    For example:
        Clue: Loud 4
        Bomb, Opera, Pistol, Bark
        All four makes loud sounds, and no other works make loud noises
        
    """
    # prompt = """
    # You are the red codemaster in a codenames game and your job is to give a clue at the end of the prompt given these words 
    # (Note: Your clue may not be any of these words):
    # Red words: {red_words} 
    # Blue words: {blue_words}
    # Civilian words: {neutral_words}
    # Assassin: {assassin_word}.
    # The clue MUST relate to EACH words it aims to indicate.
    # Clues must be easy.
    # The clue number may not be more than the amount of red words.
    # Your clue may not have appeared in any of these words and must be one word only. 
    # The clue must be in the format "Clue: Word,Number". For example "Clue: Bird,3"
    
    # Below is the example:
    # ___
    # Input:
    # Red words: [BOMB, OPERA, PISTOL, BARK, BATTERY, DISEASE, ROW, BEAR]
    # Blue words: [MARBLE, MILLIONAIRE, PORT, BOTTLE, TAP, VAN, NEEDLE, PUMPKIN]
    # Assassin word: [KNIGHT]
    # Civilian words: [BAR, ICE, BERLIN, PLOT, CYCLE, BOLT, RULER, CAT]
    # Output:
    # Clue: Loud, 4
    # Logic: 
    # [BOMB, OPERA, PISTOL, BARK]
    # ___
    # Output the Clue and related words in list format without any explanation. The response must be in 2 lines: clue in the first line and the list in the order.
    # For example 
    # "Clue: Bird, 3
    # Crow, Eagle"
    # """
    

    replacements = {
        'red_words' : red_words,
        'blue_words' : blue_words,
        'neutral_words' : neutral_words,
        'assassin_word' : assassin_word
    }

    old_prompt = prompt
    prompt = create_prompt(prompt, replacements)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {
                "role" : "user", 
                "content" : prompt,
            }, 
        ],
    )

    res = response.choices[0].message.content
    print(res)
    # clue = res.split("\n")[0]
    return res, old_prompt

def gen_guess(clue, board_words):
    prompt = """Act as a guesser in Codenames game.
    You are given the clue: '{clue}' and the list of words on the 
    board: {board_words}.
    Give your best guesses from {board_words} in a python array format: 
        "[Guess1, Guess2, Guess3, etc.]". 
    Example:
    ___
    Input: 
    Clue: [Loud, 4], Board Words: ['BOMB', 'PORT', 'BOLT', 'CYCLE', 
    'BATTERY', 'DISEASE', 'MARBLE', 'CAT', 'VAN', 'BEAR', 'ROW', 
    'PISTOL', 'NEEDLE', 'PUMPKIN', 'BAR', 'BERLIN', 'OPERA', 'ICE', 
    'TAP', 'PLOT', 'RULER', 'MILLIONAIRE', 'BARK', 'BOTTLE', 'KNIGHT']
    Output: 
    [BOMB, OPERA, PISTOL, BARK] 
    ___
    There must be {clue[1]} number of guesses. 
    The guesses must be ordered from your best guess to your worst guess.
    Each guess must be one of these words: {board_words}.
    The number of guesses must match the number provided in the clue.
    Do not return anything else besides your array of guesses."""

    replacements = {
        'clue' : clue,
        'board_words' : board_words
    }

    old_prompt = prompt
    prompt = create_prompt(prompt, replacements)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {
                "role" : "user", 
                "content" : prompt,
            }, 
        ],
    )

    guess = response.choices[0].message.content
    return guess, old_prompt



# Example gameplay loop for one round
if __name__ == "__main__":
    #clue = generate_clue(selected_words)
    #clue, _ = gen_guess(team_red_words, team_blue_words, neutral_words, assassin_word)


    data = []
    # Board 1 
    for i in range(30):
        # print("Test", i)
        raw_clue, _ = gen_clue(team_red_words, team_blue_words, neutral_words, assassin_word)
        data.append(raw_clue.strip().split('\n'))
        
    ### Board 2
    board_words = [
        "NUT", "CLIFF", "MICROSCOPE", "BANK", "CHOCOLATE", 
        "LEPRECHAUN", "KETCHUP", "MAIL", "TAP", "MAMMOTH", 
        "PASTE", "POISON", "BELT", "PLASTIC", "CYCLE", 
        "SPRING", "FLUTE", "MOUTH", "BOND", "CAPITAL", 
        "CLOAK", "FLY", "TAG", "SINK", "HAM"
    ]
    team_red_words = ["NUT", "CLIFF", "MICROSCOPE", "BANK", "CHOCOLATE", "LEPRECHAUN", "KETCHUP", "MAIL"]
    team_blue_words = ["TAP", "MAMMOTH", "PASTE", "POISON", "BELT", "PLASTIC", "CYCLE"]
    neutral_words = ["SPRING", "FLUTE", "MOUTH", "BOND", "CAPITAL", "CLOAK", "FLY", "TAG", "SINK"]
    assassin_word = ["HAM"]

    for i in range(30):
        # print("Test", i)
        raw_clue, _ = gen_clue(team_red_words, team_blue_words, neutral_words, assassin_word)
        data.append(raw_clue.strip().split('\n'))


    ### Board 3
    board_words = [
        "KETCHUP", "CLOAK", "HIMALAYAS", "BEAT", 
        "SPOT", "TRIP", "POST", "SPRING", "SHIP",
        "NUT", "BUCK", "DROP", "SOCK", "COURT", "POISON", 
        "FOREST", "BEAR", "LAB", "WAKE", "LOCK", "STATE", 
        "ENGLAND", "STREAM", "PISTOL", "KNIFE"
    ]
    team_red_words = ["KETCHUP", "CLOAK", "HIMALAYAS", "BEAT", "SPOT", "TRIP", "POST", "SPRING"]
    team_blue_words = ["WAKE", "LOCK", "STATE", "ENGLAND", "STREAM", "PISTOL", "KNIFE"]
    neutral_words = ["NUT", "BUCK", "DROP", "SOCK", "COURT", "POISON", "FOREST", "BEAR", "LAB"]
    assassin_word = ["SHIP"]

    for i in range(30):
        # print("Test", i)
        raw_clue, _ = gen_clue(team_red_words, team_blue_words, neutral_words, assassin_word)
        data.append(raw_clue.strip().split('\n'))

    with open('output.csv', mode='w', newline='') as file:
        writer = csv.writer(file)

        # Writing the data to the CSV file
        writer.writerows(data)

    #guess, _ = gen_clue(clue, board_words)
    # guess, _ = gen_guess(clue, board_words)
    # print(f"Guesser's Guess: {guess}")
    # print(_)
