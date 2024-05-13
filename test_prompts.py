import json
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

def gen_clue(red_words, blue_words, neutral_words, assassin_word, prev_clues):
    prompt = """
        CODENAME SPYMASTERS MUST FOLLOW THESE CLUE CREATION RULES:
            THE CLUE MUST BE RELATED BY MEANING
            THE CLUE CANNOT BE PURELY PHONETICALLY RELATED, A HOMONYM, A PART OF THE WORDS(OR VICE VERSA) THAT IT IS MEANT TO INDICATE.
            THE CLUE MUST BE ONLY ONE WORD AND MAY NOT BE ANY OF THESE WORDS: {prev_clues}.
        YOU ARE THE ASSISTANT FOR THE RED SPYMASTER IN A CODENAMES MATCH.
        THE RED SPYMASTER IS ASKING FOR ASSISTANCE. 
        RED WORDS={red_words},
        BLUE WORDS={blue_words},
        CIVILIAN WORDS={neutral_words},
        ASSASSIN={assassin_word}.
        THE CLUE MUST RELATE TO ATLEAST ONE RED WORD AND ALSO HAVE ABSOLUTE ZERO RELATION TO THE ASSASSIN WORD.
        THE CLUE MUST ALSO HAVE ZERO RELATION TO EVERY BLUE AND CIVILIAN WORD.
        THE NUMBER OF RED WORDS THE CLUE STRONGLY RELATES TO IS THE NUMBER OF ALLOWED GUESSES. 
        GIVE THE CLUE FOLLOWED BY THE RED WORDS ({red_words}) THAT THE CLUE AIMS TO INDICATE IN THE FORMAT IS [WORD: ALLOWED GUESSES]>(INDICATED WORDS).
        DO NOT RETURN ANYTHING ELSE.
    """
    usr_prompts = [
        # {
        #     'red_words': ['BOMB', 'OPERA', 'PISTOL', 'BARK', 'BATTERY', 'DISEASE', 'ROW', 'BEAR'],
        #     'blue_words': ['MARBLE', 'MILLIONAIRE', 'PORT', 'BOTTLE', 'TAP', 'VAN', 'NEEDLE', 'PUMPKIN'],
        #     'neutral_words': ['BAR', 'ICE', 'BERLIN', 'PLOT', 'CYCLE', 'BOLT', 'RULER', 'CAT'],
        #     'assassin_word': ['KNIGHT'],
        # },
        # {
        #     'red_words': ['COLD', 'WAR', 'NUT', 'BELT', 'WEB', 'PLATE', 'WORM', 'RING'],
        #     'blue_words': ['OPERA', 'BOOM', 'HEAD', 'MICROSCOPE', 'STRING', 'GLOVE', 'BOARD', 'TRACK', 'CLOAK'],
        #     'neutral_words': ['STAR', 'SERVER', 'TUBE', 'LUCK', 'BRUSH', 'ROUND', 'POINT'],
        #     'assassin_word': ['CIRCLE'],
        # },
        # {
        #     "red_words": ["ANGEL", "STAR", "BOX", "PARK", "KID", "SWITCH", "TAIL", "BUG", "TABLE"],
        #     "blue_words": ["STAFF", "COPPER", "EUROPE", "PRESS", "CELL", "SCORPION", "WORM", "DUCK"],
        #     "neutral_words": ["BOLT", "MOSCOW", "APPLE", "COTTON", "SPINE", "DISEASE", "SERVER"],
        #     "assassin_word": ["SKYSCRAPER"],
        # },
        # {
        #     "red_words" : ["WALL", "WASHINGTON", "RABBIT", "GIANT", "ICE CREAM", "TOOTH", "HONEY", "NEEDLE"],
        #     "blue_words" : ["MASS", "CHURCH", "HORSESHOE", "SHADOW", "KING", "CIRCLE", "TRACK"],
        #     "neutral_words" : ["SCHOOL", "WAR", "SOUND", "TAP", "NURSE", "MOON", "ROOT", "NIGHT", "TABLET"],
        #     "assassin_word" : ["NINJA"],
        # },
        {
            "red_words" : ["MOUTH", "TELESCOPE", "ALPS", "HOSPITAL", "DRILL", "OLYMPUS", "GAME", "MOUNT"],
            "blue_words" : ["MATCH", "HORSE", "TURKEY", "CHEST", "SCHOOL", "PIT", "FIRE"],
            "neutral_words" : ["FILE", "CRASH", "ORANGE", "CRICKET", "SCORPION", "PLOT", "BANK", "CARROT", "ROME"],
            "assassin_word" : ["PLATE"],
        }
    ]

    outputs = [
        # '["LOUD", 4]>(BOMB, OPERA, PISTOL, BARK)',
        # '["USSR", 2]>(COLD, WAR)',
        # '["CHRISTMAS", 3]>(ANGEL, STAR, BOX)',
        # '["SWEET", 2]>(HONEY, ICE CREAM)',
        '["SUMMIT", 3]>(MOUNT, ALPS, OLYMPUS)'
    ]

    replacements = {
        'red_words' : red_words,
        'blue_words' : blue_words,
        'neutral_words' : neutral_words,
        'assassin_word' : assassin_word,
    }

    replacements2 = {
        'red_words' : red_words,
        'blue_words' : blue_words,
        'neutral_words' : neutral_words,
        'assassin_word' : assassin_word,
        'prev_clues': prev_clues
    }


    

    old_prompt = prompt
    prompt = create_prompt(prompt, replacements2)

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

    msgs.append(
        {
            "role": "user",
            "content": prompt,
        },
    )

    done = False
    clues = []
    while not done:
        random.shuffle(replacements['red_words'])
        prompt = create_prompt(prompt, replacements)
        msgs[-1] = {
            "role": "user",
            "content": prompt,
        }
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=msgs
        )
        curr_clue = response.choices[0].message.content
        if curr_clue.split(">")[0] in clues:
            done = True
        clues.append(curr_clue.split(">")[0])
        print("CURRENT CLUE: " + curr_clue)
    print("CLUE MATCH: " + curr_clue)

    


    return curr_clue, old_prompt

def gen_guess(clue, board_words):

    # ALL EXAMPLES OF OUTPUT MUST USE DOUBLE QUOTES
    prompt = """ACT AS THE GUESSER IN A CODENAMES GAME.
    YOU ARE GIVEN THE CLUE: {clue} AND THE LIST OF WORDS ON THE BOARD: {board_words}. 
    CHOOSE WORDS FROM THE BOARD MOST ASSOCIATED WITH THE CLUE IN DESCENDING ORDER: [BEST GUESS, SECOND BEST GUESS, THIRD BEST GUEST,...].
    THERE MUST BE {clue[1]} NUMBER OF GUESSES AND EACH GUESS FROM {board_words} MUST BE ORDERED FROM BEST GUESS TO WORST GUESS.
    GUESSES NOT IN THIS LIST: {board_words} ARE INVALID.
    THE NUMBER OF GUESSES MUST MATCH THE NUMBER PROVIDED IN THE CLUE.
    DO NOT RETURN ANYTHING ELSE BESIDES YOUR ARRAY OF GUESSES.
    NONE OF THE GUESSES CAN BE {clue[0]}.
    """

    usr_prompts = [
            # {
            #     'board_words': """['BOMB', 'OPERA', 'PISTOL', 'BARK', 'BATTERY', 'DISEASE', 'ROW', 'BEAR',
            #         'MARBLE', 'MILLIONAIRE', 'PORT', 'BOTTLE', 'TAP', 'VAN', 'NEEDLE', 'PUMPKIN',
            #         'BAR', 'ICE', 'BERLIN', 'PLOT', 'CYCLE', 'BOLT', 'RULER', 'CAT','KNIGHT']""",
            #     'clue': ["LOUD", 4]
            # },
            # {
            #     'board_words': """['COLD', 'WAR', 'NUT', 'BELT', 'WEB', 'PLATE', 'WORM', 'RING',
            #         'OPERA', 'BOOM', 'HEAD', 'MICROSCOPE', 'STRING', 'GLOVE', 'BOARD', 'TRACK', 'CLOAK',
            #         'STAR', 'SERVER', 'TUBE', 'LUCK', 'BRUSH', 'ROUND', 'POINT','CIRCLE']""",
            #     'clue': ["USSR", 2]
            # },
            # {
            #     'board_words': """['SKYSCRAPER', 'TAIL', 'SPINE', 'WORM', 
            #     'STAFF', 'MOSCOW', 'BOLT', 'SERVER', 'PRESS', 
            #     'KID', 'DUCK', 'SCORPION', 'ANGEL', 'TABLE', 'COTTON', 
            #     'APPLE', 'BOX', 'BUG', 'EUROPE', 'CELL', 'DISEASE', 
            #     'COPPER', 'STAR', 'SWITCH', 'PARK']""",
            #     'clue':["CHRISTMAS", 3]
            # },
            # {
            #     'board_words': """["PIRATE", "SUIT", "OLYMPUS", "KNIFE", 
            #     "BEACH", "HEAD", "BALL", "SCORPION", "HOLLYWOOD", "HORSESHOE", 
            #     "BUCK", "TOOTH", "CYCLE", "MAPLE", "SKYSCRAPER", "VET", 
            #     "BATTERY", "FILM", "CLOAK", "CHECK", 
            #     "SHAKESPEARE", "MILLIONAIRE", "MUG", "BOOT", "FOREST"]""",
            #     'clue':["ISLAND", 2]
            # },
            # {
            #     'board_words': """["TURKEY", "SLUG", "WORM", "PLATE",
            #     "BERRY", "MINT", "FIGHTER", "CONDUCTOR",
            #     "LOCK", "LINE", "CRICKET", "CAST", "PLOT",
            #     "THUMB", "SHOE", "CANADA", "LIFE", "NAIL", "TOWER",
            #     "SPACE", "EMBASSY", "AIR", "STREAM", "PART", "JACK"]""",
            #     'clue':["RECIPE", 4]            
            # },
            # {
            #     'board_words': """["SMUGGLER", "RING", "NOVEL", "FLUTE",
            #     "WITCH", "AMBULANCE", "BOTTLE", "HAND",
            #     "MAIL", "GIANT", "HORSESHOE", "GRASS", 
            #     "KANGAROO", "PASTE", "COMIC", "CASINO", 
            #     "CALF", "RABBIT", "SPINE", "ARM", 
            #     "SCREEN", "LITTER", "DATE", "SHOE", "BUFFALO"]""",
            #     'clue':["MEDICINE", 2]
            # },
            # {
            #     'board_words': """["WALL", "WASHINGTON", "RABBIT", "GIANT", "ICE CREAM", "TOOTH", "HONEY", "NEEDLE",
            #     "MASS", "CHURCH", "HORSESHOE", "SHADOW", "KING", "CIRCLE", "TRACK", 
            #     "SCHOOL", "WAR", "SOUND", "TAP", "NURSE", "MOON", "ROOT", "NIGHT", "TABLET", "NINJA"]""",
            #     'clue':["SWEET", 2]
            # },
            {
                'board_words': """["MOUTH", "TELESCOPE", "ALPS", "HOSPITAL", "DRILL", "OLYMPUS", "GAME", "MOUNT",
                "MATCH", "HORSE", "TURKEY", "CHEST", "SCHOOL", "PIT", "FIRE", "PLATE",
                "FILE", "CRASH", "ORANGE", "CRICKET", "SCORPION", "PLOT", "BANK", "CARROT", "ROME"
                ]""",
                'clue':["SUMMIT", 3]
            }
        ]

    outputs = [
        # '["BOMB", "OPERA", "PISTOL", "BARK"]',
        # '["COLD", "WAR"]',
        # '["ANGEL", "STAR", "BOX"]',
        # '["BEACH", "PIRATE"]',
        # '["PLATE", "BERRY", "TURKEY", "MINT"]',
        # '["AMBULANCE", "BOTTLE"]',
        # '["HONEY", "ICE CREAM"]',
        '["MOUNT", "ALPS", "OLYMPUS"]',
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
    print("board: " + board_words)
    # print("clue: " + json.dumps(clue))
    print("guess: " + guess)
    return guess, old_prompt



