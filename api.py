from openai import OpenAI
import random

from dotenv import load_dotenv
import os

# Load your API key from an environment variable
load_dotenv()
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")
client = OpenAI(api_key=OPEN_AI_API_KEY)

# Define the Codenames board (25 words for simplicity)
all_words = [
    "DIVER", "TEMPLE", "HOOD", "ROUND", "CHINA", "TRAIN", "COVER", "STICK", "LION", "CAST", "MINE", "HORSESHOE", "ROW", "CONCERT", "BRUSH", "LASER", "PHOENIX", "BELL", "DROP", "SPIKE", "NINJA", "COPPER", "ROSE", "FAIR", "ORANGE"
]

# Teams' words (for simplicity, not used in clue generation/guessing logic here)
team_red_words = ["DIVER", "TEMPLE", "HOOD", "ROUND", "CHINA", "TRAIN", "COVER", "STICK"]
team_blue_words = ["LION", "CAST", "MINE", "HORSESHOE", "ROW", "CONCERT", "BRUSH", "LASER"]
neutral_words = ["PHOENIX", "BELL", "DROP", "SPIKE", "NINJA", "COPPER", "ROSE", "FAIR"]
assassin_word = ["ORANGE"] 


spymaster_output = ["('Ensemble', 4)\n['ROW', 'CONCERT', 'BRUSH', 'LASER']"]
guesser_output =  ["['CONCERT', 'BELL', 'PHOENIX', 'DIVER']"]

def generate_clue(board_words, team_words, assassin):
    prompt = f"This is the entire word list: {board_words}. This word list is your team's words: {team_words}. Give the relationship word that would describe the relationship of the some of the words on your team's list. The relationship word should not be in the provided list and should be specific enough to guess the exact words that are related from the list. The relationship word must not be related to other words than your team's word list. The relationship word must be one word and not related to {assassin}. Give the relationship word and number of the related words. Output(relationship_word, number) in tuple format, and related words in list format without any explanation. The relationship word cannot be from the list. Your response must be 2 lines: one tuple in first line, and one list in the other"

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
    word, number = clue
    prompt = f"This is the word list: {board_words}. Find {number} words that are relate to {word}. Output {number} words in python list format in one line. The {word} must not be on the output list. Sort the words in the list so the words that is mostly related to {word} comes first"

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

def response_format(raw):
    """
    format strings into list
    """
    raw = raw.replace("(", "").replace(")", "").replace("'", "").replace(",", "").replace("\"", "").replace("[", "").replace("]", "")
    raw_lst = raw.split()


    return raw_lst


def match(all_words, team_words, assassin_word):
    spymaster = generate_clue(all_words, team_words, assassin_word)
    # spymaster = random.choice(spymaster_output)
    clue, answer = spymaster.split("\n")

    clue = response_format(clue)
    clue[1] = int(clue[1])
    answer = response_format(answer)

    print(f"Spymaster's Clue: {clue}")
    print(f"Spymaster's Answer: {answer}")

    guess = guess_word(clue, all_words)
    # guess = random.choice(guesser_output)
    guess = response_format(guess)
    print(f"Guesser's Guess: {guess}")

    return clue, answer, guess

def validation(all_words, team_words, clue, answer, guess):
    """
    check for rules
        1. incorrect guessing count
        2. guessing word not from all words list
        3. answer word not from current team's list
    """
    if len(guess) != clue[1]:
        print("number of guesses are wrong")
        return False
    
    for g in guess:
        if g not in all_words:
            print("Guess not in words board")
            return False
    
    for a in answer:
        if a not in team_words:
            print("Answer not from team words")
            return False
    
    return True
    

def main():
    matches = 1
    correct = 0
    partial_correct = 0
    incorrect = 0
    
    error = 0 
    curr_team = "red"
    curr_lst = team_red_words

    while team_red_words or team_blue_words:
        print(f"match {matches}, {curr_team} team")

        clue, answer, guess = match(all_words, curr_lst, assassin_word)
        if validation(all_words, curr_lst, clue, answer, guess):
            for ans in answer:
                partial = 0
                if ans in guess:
                    print(f"{ans} guessed correctly!")
                    partial += 1
                    
                    all_words.remove(ans)
                    curr_lst.remove(ans)
                    
                    if not curr_lst:
                        curr_team = "blue"
                        curr_lst = team_blue_words

            if partial == len(ans):
                correct += 1
            elif partial > 0:
                partial_correct += 1
            else:
                incorrect += 1
        else:
            error += 1

        matches += 1

    print(f"Statistics: total {matches - 1} matches")
    print(f"Correct: {correct}")
    print(f"Partial Correct: {partial_correct}")
    print(f"Incorrect: {incorrect}")
    print(f"Error: {error}")
main()