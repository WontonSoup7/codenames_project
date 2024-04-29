from openai import OpenAI
import random

from dotenv import load_dotenv
import os

# Load your API key from an environment variable
load_dotenv()
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")
client = OpenAI(api_key=OPEN_AI_API_KEY)

def create_prompt(template, replacements):  
    return template.format(**replacements)

def gen_clue(red_words, blue_words, neutral_words, assassin_word):
    #prompt = f"Act as a spymaster in Codenames game. Provide a one-word clue that relates to these words: {', '.join(words)}."
    prompt = """
    You are the red codemaster in a codenames game and your job is to 
    give a clue at the end of the prompt given these words 
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
    Do not return anything else.
    """

    usr_prompts = [
        {
            'red_words': ['BOMB', 'OPERA', 'PISTOL', 'BARK', 'BATTERY', 'DISEASE', 'ROW', 'BEAR'],
            'blue_words': ['MARBLE', 'MILLIONAIRE', 'PORT', 'BOTTLE', 'TAP', 'VAN', 'NEEDLE', 'PUMPKIN'],
            'neutral_words': ['BAR', 'ICE', 'BERLIN', 'PLOT', 'CYCLE', 'BOLT', 'RULER', 'CAT'],
            'assassin_word': ['KNIGHT'],
        },
        {
            'red_words': ['COLD', 'WAR', 'NUT', 'BELT', 'WEB', 'PLATE', 'WORM', 'RING'],
            'blue_words': ['OPERA', 'BOOM', 'HEAD', 'MICROSCOPE', 'STRING', 'GLOVE', 'BOARD', 'TRACK', 'CLOAK'],
            'neutral_words': ['STAR', 'SERVER', 'TUBE', 'LUCK', 'BRUSH', 'ROUND', 'POINT'],
            'assassin_word': ['CIRCLE'],
        }
    ]

    outputs = [
        """
        Clue: Loud, 4
        """,
        """
        Clue: USSR, 2
        """,
    ]

    replacements = {
        'red_words' : red_words,
        'blue_words' : blue_words,
        'neutral_words' : neutral_words,
        'assassin_word' : assassin_word
    }

    msgs = []
    for i in range(len(usr_prompts)):
        tmp_prompt = create_prompt(prompt, usr_prompts[i])
        # print(tmp_prompt)
        msgs.append(
            {
                "role": "user",
                "content": tmp_prompt,
            },
        )
        msgs.append(
            {
                "role": "assistant",
                "content": outputs[i],
            },
        )

    old_prompt = prompt
    prompt = create_prompt(prompt, replacements)

    msgs.append(
        {
            "role": "user",
            "content": prompt,
        },
    )
 

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=msgs
    )

    clue = response.choices[0].message.content
    return clue, old_prompt

def gen_guess(clue, board_words):

    # ALL EXAMPLES OF OUTPUT MUST USE DOUBLE QUOTES
    prompt = """Act as a guesser in Codenames game.
    You are given the clue: '{clue}' and the list of words on the 
    board: {board_words}.
    Give your best guesses from {board_words} in a python array format: 
        ["Guess1", "Guess2", "Guess3", ...] 
    There must be {clue[1]} number of guesses. 
    The guesses must be ordered from your best guess to your worst guess.
    Each guess MUST be one of these words: {board_words}.
    Each guess MUST be one of these words: {board_words}.
    The number of guesses must match the number provided in the clue.
    Do not return anything else besides your array of guesses."""

    usr_prompts = [
            {
                'board_words': """['BOMB', 'OPERA', 'PISTOL', 'BARK', 'BATTERY', 'DISEASE', 'ROW', 'BEAR',
                    'MARBLE', 'MILLIONAIRE', 'PORT', 'BOTTLE', 'TAP', 'VAN', 'NEEDLE', 'PUMPKIN',
                    'BAR', 'ICE', 'BERLIN', 'PLOT', 'CYCLE', 'BOLT', 'RULER', 'CAT','KNIGHT'],""",
                'clue': ["LOUD", 4]
            },
            {
                'board_words': """['COLD', 'WAR', 'NUT', 'BELT', 'WEB', 'PLATE', 'WORM', 'RING',
                    'OPERA', 'BOOM', 'HEAD', 'MICROSCOPE', 'STRING', 'GLOVE', 'BOARD', 'TRACK', 'CLOAK',
                    'STAR', 'SERVER', 'TUBE', 'LUCK', 'BRUSH', 'ROUND', 'POINT','CIRCLE'],""",
                'clue': ["USSR", 2]
            }
        ]

    outputs = [
        """
        ["BOMB", "OPERA", "PISTOL", "BARK"]
        """,
        """
        ["COLD", "WAR"]
        """
    ]
    replacements = {
        'clue' : clue,
        'board_words' : board_words
    }

    msgs = []
    for i in range(len(usr_prompts)):
        tmp_prompt = create_prompt(prompt, usr_prompts[i])
        # print(tmp_prompt)
        msgs.append(
            {
                "role": "user",
                "content": tmp_prompt,
            },
        )
        msgs.append(
            {
                "role": "assistant",
                "content": outputs[i],
            },
        )

    old_prompt = prompt
    prompt = create_prompt(prompt, replacements)

    #print(prompt)
    msgs.append(
        {
            "role": "user",
            "content": prompt,
        },
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=msgs
    )

    guess = response.choices[0].message.content
    print("guess: " + guess)
    return guess, old_prompt



