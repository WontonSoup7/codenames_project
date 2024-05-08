from openai import OpenAI # type: ignore
import random
import json

from dotenv import load_dotenv # type: ignore
import os

# Load your API key from an environment variable
load_dotenv()
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")
client = OpenAI(api_key=OPEN_AI_API_KEY)

# # Define the Codenames board (25 words for simplicity)
# all_words = [
#     "DRAGON", "GREEN",  "BAR", "CHOCOLATE", "PITCH", "SUIT", "RING", "CONDUCTOR", "CASINO", "HOLLYWOOD", "SATURN", "BOARD", "NURSE", "PLATYPUS", "BUFFALO", "LIMOUSINE", "AIR", "MINE", "BUG", "DOG", "CHAIR", "CRANE", "LUCK", "ENGINE",  "NEEDLE"
# ]

# # Teams' words (for simplicity, not used in clue generation/guessing logic here)

# team_red_words =  ["DRAGON", "GREEN", "NURSE", "PLATYPUS", "CONDUCTOR", "CASINO", "SATURN", "BOARD"]
# team_blue_words = ["BUFFALO", "LIMOUSINE", "BAR", "CHOCOLATE", "PITCH", "SUIT", "NEEDLE", "RING"]
# neutral_words = ["AIR", "MINE", "BUG", "DOG", "CHAIR", "CRANE", "LUCK", "ENGINE"]
# assassin_word =  ["HOLLYWOOD"]


word_list =  open('wordlist-eng.txt', 'r').readlines()
word_list = [word.strip() for word in word_list]
all_words = random.sample(word_list, 25)
team_red_words = random.sample(all_words, 8)
team_blue_words = random.sample([w for w in all_words if w not in team_red_words], 8)
neutral_words = random.sample([w for w in all_words if (w not in team_red_words and w not in team_blue_words)], 8)
assassin_word = random.sample([w for w in all_words if (w not in team_red_words and w not in team_blue_words and w not in neutral_words)], 1)

print("All: ", all_words)
# print("Red: ", team_red_words)
# print("Blue: ", team_blue_words)
# print("Neutral: ", neutral_words)
# print("Assassin: ", assassin_word)


def generate_clue(history, team_red_words, team_blue_words, neutral_words, assassin_word):
    # clue only
    # prompt = f"""
    # From your list,{team_red_words}, give me a clue that represents some of the words from the list in some way. 
    # For example, for the word cards ‘beach’, ‘whale’, and ‘water’, one could give the clue ‘ocean’, as these things are all related to the ocean. 
    # Also, give me a number that represents how many words match that clue. The single word clue must be related by meaning, so it cannot be purely phonetically related.
    # Avoid a clue that may relate to this words: {team_blue_words}.
    # Avoid a clue that relates to this words: {assassin_word}.
    # The clue word must not be from the list. 
    # Output(relationship_word, number) in tuple format. 
    # Your response must be 1 line: one tuple.
    # """

    prompt = f"""
    Give me a clue that represents some of the words from the list {team_red_words} in some way. 
    For example, for the word cards ‘beach’, ‘whale’, and ‘water’, one could give the clue ‘ocean’, as these things are all related to the ocean. 
    Also, give me a number that represents how many words in {team_red_words} match that clue. THE NUMBER MUST BE GREATER THAN 0! The single word clue must be related by meaning, so it cannot be purely phonetically or structurally related.
    The word clue cannot be a homonym for the word that the clue is for. For example, "knight" is not a valid clue for "night" because they are homonyms with completely different meaning.
    The word clue also cannot be a part of the word that it's a clue for (or vice versa). For example, "hero" is an INVALID clue for "superhero" (and vice versa).
    Avoid a clue that may relate to this words: {team_blue_words}.
    Avoid a clue that relates to this words: {assassin_word}.
    THE CLUE WORD MUST NOT BE A WORD FROM {all_words}! 
    THE CLUE MUST NOT CONTAIN ANY SPACES!
    Try to avoid using previously used clues and come up with an original clue.
    Output(relationship_word, number) in tuple format. 
    Your response must be 1 line: one tuple.
    """

    #messages = [{"role" : "user", "content" : prompt}]
    #messages.extend(history)

    message = [{"role" : "user", "content" : prompt}]
    msgs = history
    #history.extend(message)
    msgs.extend(message)

    # response = client.chat.completions.create(
    #     model="gpt-3.5-turbo-0125",
    #     # model="gpt-4-turbo",
    #     messages=[
    #         {
    #             "role" : "user", 
    #             "content" : prompt,
    #         }, 
    #     ],
    # )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=msgs#messages
    )

    clue = response.choices[0].message.content

    return clue

def guess_word(clue, board_words):
    word, number = clue
    #prompt = f"This is the word list: {board_words}. Find {number} words that are relate to {word}. Output {number} words in python list format in one line. The {word} must not be on the output list. Sort the words in the list so the words that is mostly related to {word} comes first"

    prompt = f"""
    From the words in the list {board_words}, determine the top {number} words that are closest to the word {word}, in terms of semantic meaning.
    For example, given the list of words ['SNOWMAN', 'KETCHUP', 'DATE', 'FALL', 'TURKEY', 'LITTER', 'EUROPE', 'CODE', 'PILOT', 'STRIKE', 'SUB', 'LASER', 'MISSILE', 'DRILL', 'CLIFF', 'HELICOPTER', 'CRASH', 'ROUND', 'TABLE', 'SEAL', 'AFRICA', 'KID', 'GHOST', 'RACKET', 'SPY'],
    the top 2 words related to the word "continent" are 'EUROPE' and 'AFRICA' because both words refer to continents.
    Given the list of words  ['STAFF', 'TEMPLE', 'LION', 'CELL', 'PIN', 'BOTTLE', 'WAVE', 'GOLD', 'SCALE', 'ORGAN', 'FRANCE', 'SOLDIER', 'BOMB', 'HOSPITAL', 'LOCH NESS', 'SCORPION', 'GAME', 'PLASTIC', 'BOARD', 'KANGAROO', 'PALM', 'SINK', 'CARROT', 'TAG', 'WHIP'],
    the top 2 words related to the word "cage" are 'LION' and 'CELL'. 'Cage' is related to 'cell' because a cage and a cell are similar in that they are both enclosures meant to restrict movement and freedom
    'Cage' is related to 'lion' because lions are frequently kept in cages. So the output would be ['CELL', 'LION'].
    Output {number} words in python list format in one line. The word {word} must not be in the output list. Sort the words in the list in descending order of how closely related they are to the word {word}
    """


    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        # model="gpt-4-turbo",
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

    chat_history = []

    spymaster = generate_clue(chat_history, team_red_words, team_blue_words, neutral_words, assassin_word)
    # spymaster = random.choice(spymaster_output)
    # print(spymaster)
    try:
        clue, answer = spymaster.split("\n")
    except ValueError:
        clue, _, answer = spymaster.split("\n")

    clue = response_format(clue)
    clue[1] = int(clue[1])

    chat_history.append({"role": "system", "content": json.dumps(clue)})

    answer = response_format(answer)

    print(f"Spymaster's Clue: {clue}")
    print(f"Spymaster's Answer: {answer}")

    guess = guess_word(clue, all_words)
    # guess = random.choice(guesser_output)
    guess = response_format(guess)

    chat_history.append({"role" : "user", "content" : json.dumps(guess)})

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


def gpt_vs_gpt():
    matches = 1
    correct = 0
    partial_correct = 0
    incorrect = 0
    
    error = 0 
    curr_team = "red"
    curr_lst = team_red_words


    while team_red_words:
        print(f"Turn {matches}, {curr_team} team")

        clue, answer, guess = match(all_words, curr_lst, assassin_word)
        if validation(all_words, curr_lst, clue, answer, guess):
            # for ans in answer:
            for ans in curr_lst:
                partial = 0
                if ans in guess:
                    print(f"{ans} guessed correctly!")
                    partial += 1
                    
                    all_words.remove(ans)
                    curr_lst.remove(ans)
                    

            if partial == len(ans):
                correct += 1
            elif partial > 0:
                partial_correct += 1
            else:
                incorrect += 1
        else:
            error += 1

        matches += 1
        print()

    print(f"Statistics: total {matches - 1} turns")
    print(f"Correct: {correct}")
    print(f"Partial Correct: {partial_correct}")
    print(f"Incorrect: {incorrect}")
    print(f"Error: {error}")

def gpt_vs_user():
    """
    gpt gives clue, guess in the input
    """
    matches = 1
    correct = 0
    incorrect = 0
    
    chat_history = []

    while team_red_words:
        spymaster = generate_clue(chat_history, team_red_words, team_blue_words, neutral_words, assassin_word)
        
        print("CLUE: ", spymaster)

        clue = response_format(spymaster)

        chat_history.append({"role": "system", "content": json.dumps(clue)})

        clue_num = int(clue[1].strip())

        print(f"Spymaster's Clue: {clue}")
        print( "Word Board: ", all_words)
        guesses = []
        for _ in range(clue_num):
            guess = input("Guess one word: ")
            guesses.append(guess.upper())
            if guess.upper() in team_red_words:
                print("correct!")
                team_red_words.remove(guess.upper())
                all_words.remove(guess.upper())
                correct += 1
            else:
                print("incorrect")
                incorrect += 1
                break

        chat_history.append({"role" : "user", "content" : json.dumps(guesses)})
        chat_history = chat_history[-10:]

        matches += 1
        print()

    print(f"Statistics: total {matches - 1} turns")
    print(f"Correct: {correct}")
    print(f"Incorrect: {incorrect}")

    print("All: ", all_words)
    print("Red: ", team_red_words)
    print("Blue: ", team_blue_words)
    print("Neutral: ", neutral_words)
    print("Assassin: ", assassin_word)
    # print(f"Error: {error}")


# # main()
# for _ in range(5):
#     print(generate_clue(team_red_words, team_blue_words, neutral_words, assassin_word))
#     print()

#gpt_vs_user() 
gpt_vs_gpt()