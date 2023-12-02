import time

"""

Python Wordle solver


User enters the word they guessed (e.g. WATER)
Then user indicates if the letters are grey, yellow or green (e.g. the first letter is yellow and the third letter is green: YXGXX)
X = letter is not in the word
Y = letter is in the word but not in the correct position
G = letter is in the word and in the correct position

Set constraints based on letters we know are/aren't in the word based on user input
    - Letters marked as X are removed from the domain of all variables in the word
    - Letters marked and Y are removed from the domain of the variable(s) it was guessed for
    - Letters marked as G constrain that variable to 1 domain

Also set constraints based on letter combinations that dont exist in the English language:
    - We can try to attempt this by iterating through each 'duo' of letters in the word (1st and 2nd letter, 2nd and 3rd, 3rd and 4th, 4th and 5th) and if one of the letter's position is present
    in the impossible letter combinations list then we set a constraint on each of them 
    - For example, user gives us the word EQUES but the result is XGGXG so we know the word has QU in the middle and S at the end. (Real word is AQUAS)
    - We set remove letters that cannot be in Slot 1 from the domain of the 1st variable. These are letters that don't appear in front of Q in the English language
    (e.g. b,f,j,k,p, etc.)
    - We also remove letters that cannot be in Slot 4 from the domain of the 4th variable. These are letters that don't appear after E in the English language.
    In this case since E is a vowel all letters can appear after E. But also we remove letters that don't appear before the letter S in the English language. (e.g. q)
This can be done in a preprocessing step 

If two letters are consecutive in the word then we set constraints so that the other variables beside the consecutive letters cannot be the same letter
(e.g. the letters in the word are _EE__ we can remove E from the domain of the first and fourth letters)

How to select the next variable?
Choose the next variable based on whichever slot has the smallest domain.

How to select the next value for that variable?


Any word within the list of valid Wordle words represents a solution to the problem, so there may be multiple solutions for the same constraints.
"""
valid_words = []

class Word:
    """
     Class to represent a 5-letter word and an assignment of letters to each variable in the word.
    
     Variable _cells stores a matrix with 5 entries, one for each variable in the puzzle
    """
    def __init__(self):
        self._width = 5
        self._cells = []
    
    def copy(self):
        copy_word = Word()
        copy_word._cells = self._cells.copy()
        return copy_word
    
    def get_cells(self):
        return self._cells
    
    def get_width(self):
        return self._width
    
    def get_cell_string(self):
        return(''.join(self._cells))

    def is_solution(self):
        if self.get_cell_string in valid_words:
            return True
        return False
    
class MRV:
    """
    Implements the MRV heuristic, which returns one of the variables with smallest domain. 
    """
    def select_variable(self, word):

        # Set the smallest tentative domain to the largest possible domain
        smallest_domain = 27

        # Iterate through cells
        for i in range(word.get_width()):
            if (len(word.get_cells()[i]) < smallest_domain and len(word.get_cells()[i]) != 1):
                smallest_domain = len(word.get_cells()[i])
                var = i


        return var

def is_valid_result(result_guessed_word):
    for char in result_guessed_word:
        if char not in ['X','Y','G']:
            return False
    if len(result_guessed_word) != 5:
        return False
    return True

def is_valid_word(guessed_word):
    if len(guessed_word) != 5:
        print("Please guess a 5-letter word\n")
        return False
    elif guessed_word not in valid_words:
        print("Not a valid Wordle word!\n")
        return False
    return True

if __name__ == "__main__":

    file = open('valid-wordle-words.txt', 'r')
    for valid_word in file:
        valid_word = valid_word.strip()
        valid_words.append(valid_word)

    while(True):
        guessed_word = input("Please enter the word you guessed: ").upper()

        if not is_valid_word(guessed_word):
            break

        print("\nPlease indicate the result of your guess")

        result_guessed_word = input("X = letter is gray\nY = letter is yellow\nG = letter is green\n: ").upper()

        if not is_valid_result(result_guessed_word):
            print("NOT A VALID INPUT")
            break

