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
assassin_word = ["Pitch"]

def generate_clue(red_words, blue_words, neutral_words, assassin_word):
    #prompt = f"Act as a spymaster in Codenames game. Provide a one-word clue that relates to these words: {', '.join(words)}."
    prompt = f"""Act as a spymaster for the red team in Codenames game. 
    The red team words are {red_words}. The blue team words are {blue_words}. The neutral words are {neutral_words}.
    The assassin word is {assassin_word}.
    Generate a clue for the red team Codenames based on these words."""


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

def guess_word(clue, board_words):
    prompt = f"Act as a guesser in Codenames game. Given the clue '{clue}', which of these words: {', '.join(board_words)} is most related?"

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
    clue = generate_clue(team_red_words, team_blue_words, neutral_words, assassin_word)
    print(f"Spymaster's Clue: {clue}")
    
    guess = guess_word(clue, board_words)
    print(f"Guesser's Guess: {guess}")
