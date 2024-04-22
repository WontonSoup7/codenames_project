from openai import OpenAI
import random

from dotenv import load_dotenv
import os

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

def gen_clue(red_words, blue_words, neutral_words, assassin_word):
    #prompt = f"Act as a spymaster in Codenames game. Provide a one-word clue that relates to these words: {', '.join(words)}."
    prompt = f"""

    Examples:
    ___
    Input:
    Red words: [BOMB, OPERA, PISTOL, BARK, BATTERY, DISEASE, ROW, BEAR]
    Blue words: [MARBLE, MILLIONAIRE, PORT, BOTTLE, TAP, VAN, NEEDLE, PUMPKIN]
    Assassin word: [KNIGHT]
    Civilian words: [BAR, ICE, BERLIN, PLOT, CYCLE, BOLT, RULER, CAT]
    Output:
    Clue: Loud, 4
    Logic: 
    [BOMB, OPERA, PISTOL, BARK]
    ___

    You are the red codemaster in a codenames game and your job is to 
    give a clue at the end of the prompt given these words 
    (Note: Your clue may not be any of these words):
    Red words: {red_words} 
    Blue words: {blue_words}
    Civilian words: {neutral_words}
    Assassin: {assassin_word}.
    Your clue may not have appeared in any of these words.
    The clue must be in the format "Clue: Word,Number". For example "Clue: Bird,3"
    """
    # THe clue must be semantically far from all the bad words, 
    # have little semantically association with the neutral words,
    # and have no semantic association with the instant death word.
    # Pick the words in good words that have the strongest semantic connection
    # and derive a clue that is semantically relates to these words.
    # The number you give should be the number of words your clue aims to indicate.
    # The clue should encourage diversity.
    # The clue must be in the format "Word:Number". For example "Bird: 3"
    # Do not return aynthing else."""


    # prompt = f"""Act as a spymaster for the red team in Codenames game. 
    # The red team words are {red_words}. 
    # The blue team words are {blue_words}. 
    # The neutral words are {neutral_words}.
    # The assassin word is {assassin_word}.
    # Generate a clue for the red team Codenames based on these words.
    # Check your knowledge base for the rules of the codenames game.
    # Your clue must abide by these rules. For example one of the rules is
    # that the word must not appear in red team, blue team, neutral, or assassin.
    # The clue must be in the format "Word:Number". For example "Bird: 3"
    # Do not return aynthing else."""


    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {
                "role" : "user", 
                "content" : prompt,
            }, 
        ],
    )

    clue = response.choices[0].message.content
    return clue

def gen_guess(clue, board_words):
    prompt = f"""Act as a guesser in Codenames game.
    You are given the clue: '{clue}' and the list of words on the 
    board: {board_words}.
    Give your best guesses from {board_words} in a python array format: "[Guess1, Guess2, Guess3, etc.]". 
    Example:
    ___
    Input: 
    Clue: [Loud, 4], Board Words: ['BOMB', 'PORT', 'BOLT', 'CYCLE', 'BATTERY', 'DISEASE', 'MARBLE', 'CAT', 'VAN', 'BEAR', 'ROW', 'PISTOL', 'NEEDLE', 'PUMPKIN', 'BAR', 'BERLIN', 'OPERA', 'ICE', 'TAP', 'PLOT', 'RULER', 'MILLIONAIRE', 'BARK', 'BOTTLE', 'KNIGHT']
    Output: 
    [BOMB, OPERA, PISTOL, BARK] 
    ___
    There must be {clue[1]} number of guesses. 
    The guesses must be ordered from your best guess to your worst guess.
    Each guess must be one of these words: {board_words}.
    The number of guesses must match the number provided in the clue.
    Do not return anything else besides your array of guesses."""

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
    return guess



# Example gameplay loop for one round
if __name__ == "__main__":
    #selected_words = random.choice(board_words)

    #clue = generate_clue(selected_words)
    clue = gen_guess(team_red_words, team_blue_words, neutral_words, assassin_word)
    print(f"Spymaster's Clue: {clue}")
    
    guess = gen_clue(clue, board_words)
    print(f"Guesser's Guess: {guess}")
