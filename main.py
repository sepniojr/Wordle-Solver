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


This problem differs from Sudoku in that any word within the list of valid Wordle words represents a solution to the problem, so there may be multiple solutions for the same constraints.
However, we are trying to help solve the Wordle, so it is in our best interest to try and search for the best possible solution.

How to select the next variable?
    - Choose the next variable based on whichever slot has the smallest domain. (MRV selector)

How to select the next value for that variable?
    - We should prioritize any letters that we know are present in the word (e.g. Yellow letters) (How to do this?) (Set up priority queue of letters?)
    - Look at the domain of the variable and select the letter with the highest frequency in that slot of all valid Wordle words.
    - Possible sol'n: Organize the domain list of each variable and order it by Yellow letters first and then go down by letter frequency in that slot
        - Need a function that checks the yellow letters list before each search and moves the yellow letters to the front of the domain string
        - This function also indexes the list of letter frequency by position and orders the rest of the letters that way



TODO: Important questions to answer: What happens if the user enters a word and it's all wrong? How do we decide which word to recommend them?
"""
valid_words = []

class Word:
    """
     Class to represent a 5-letter word and an assignment of letters to each variable in the word.
    
     Variable _domains stores a matrix with 5 entries, one for each variable in the puzzle. 
     Each entry of the matrix stores the domain of a variable. Initially, the domain of each variable is all letters of the English alphabet, ABCDEFGHIJKLMNOPQRSTUVWXYZ
     When the user enters their first guess, the domains of the variables are adjusted to fit their corresponding constraints
    """
    def __init__(self):
        self._width = 5
        self._domains = []
        self._cells = []
        self._yellow_letters = []
        self._complete_domain = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


    def init_cells(self, word_string, result_string):
        """
        This function takes in the word the user guessed and the result of that word and sets the initial domain of each cell accordingly
        This function is only called once; Further modifications to the domain will be done in a separate consistency function

        If a letter in a guessed word is grey, that letter is removed from the domain of the variable
        If a letter in a guessed word is yellow, that letter is removed from the domain of the variable but put into a yellow letter list for later
        If a letter in a guessed word is green, the domain of the variable is set to that letter
        """
        word = list(word_string)
        result = list(result_string)
        row = []

        for i in range(len(word_string)):
            if result[i] == 'X':
                row.append(self._complete_domain.replace(word[i], ''))
            elif result[i] == 'Y':
                row.append(self._complete_domain.replace(word[i], ''))
                self._yellow_letters.append(word[i])
            elif result[i] == 'G':
                row.append(word[i])

        self._cells.append(row)
        pass
        

    def copy(self):
        copy_word = Word()
        copy_word._cells = self._cells.copy()
        return copy_word
    
    def get_cells(self):
        return self._cells
    
    def get_width(self):
        return self._width

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
    elif guessed_word.lower() not in valid_words:
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

        word = Word()
        word.init_cells(guessed_word,result_guessed_word)

