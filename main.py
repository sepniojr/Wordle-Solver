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
    - We should prioritize any letters that we know are present in the word (e.g. Yellow letters)

    - Look at the domain of the variable and select the letter with the highest frequency in that slot of all valid Wordle words.
    - Possible sol'n: Organize the domain list of each variable and order it by Yellow letters first and then go down by letter frequency in that slot
        - Need a function that checks the yellow letters list before each search and moves the yellow letters to the front of the domain string
        - This function also indexes the list of letter frequency by position and orders the rest of the letters that way



TODO: Important questions to answer: What happens if the user enters a word and it's all wrong? How do we decide which word to recommend them?
"""
valid_words = []
impossible_pairs = []
var1 = {}
var2 = {}
var3 = {}
var4 = {}
var5 = {}

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
        self._grey_letters = []
        self._complete_domains = ["SPBCMTARDGFLHNWKOEVJUYIZQX",
                                  "AOEIURLHNYTPMCWKSBDGXVFZQJ",
                                  "ARINOELUTSMCDGPBKWVYFZHXJQ",
                                  "EAITNLORSKDUGPCMHBFVZWYJXQ",
                                  "SEYADTRNLOHIKMGPCUFXBWZVQJ"]


    def init_cells(self, word_string, result_string):
        """
        This function takes in the word the user guessed and the result of that word and sets the initial domain of each cell accordingly
        This function is only called once; Further modifications to the domain will be done in a separate consistency function

        If a letter in a guessed word is grey, that letter is removed from the domain of all variables
        If a letter in a guessed word is yellow, that letter is removed from the domain of the variable but put into a yellow letter list for later
        If a letter in a guessed word is green, the domain of the variable is set to that letter
        """
        word = list(word_string)
        result = list(result_string)
        row = []
        self._cells = []
        #self._grey_letters = []
        #self._yellow_letters = []

        for i in range(len(word_string)):
            if result[i] == 'X':
                # Remove this letter from all domains of the word
                row.append(self._complete_domains[i].replace(word[i], ''))
                self._grey_letters.append(word[i])
            if result[i] == 'Y':
                row.append(self._complete_domains[i].replace(word[i], ''))
                self._yellow_letters.append(word[i])
            elif result[i] == 'G':
                row.append(word[i])

        #print("Row: ", row)
        self._cells.extend(row)

        for grey_letter in self._grey_letters:
            for i in range(len(self.get_cells())):
                if grey_letter in self.get_cells()[i] and len(self.get_cells()[i]) != 1:
                    new_domain = self.get_cells()[i].replace(grey_letter, '')
                    self.get_cells()[i] = new_domain

        #FIXME: This is a test to adding the yellow letters to the front of the domain. Later on maybe make this its own function instead
        for yellow_letter in self._yellow_letters:
            for i in range(len(self.get_cells())):
                if yellow_letter in self.get_cells()[i]:
                    new_domain = self.get_cells()[i].replace(yellow_letter, '')
                    self.get_cells()[i] = yellow_letter + new_domain

        print(self.get_cells())
        pass

    def remove_yellow_letters(self, letter):
        self._yellow_letters.remove(letter)

    def get_yellow_letters(self):
        return self._yellow_letters
    
    def get_grey_letters(self):
        return self._grey_letters
    
    def get_cell_string(self):
        return ''.join(self.get_cells())

    def copy(self):
        copy_word = Word()
        copy_word._cells = [cell[:] for cell in self._cells]
        copy_word._yellow_letters = [cell[:] for cell in self._yellow_letters]
        #print("Copy cells: ", copy_word.get_cells())
        return copy_word
    
    def get_cells(self):
        return self._cells
    
    def get_width(self):
        return self._width

    def is_solution(self):
        if self.get_cell_string().lower() in valid_words:
            return True
        return False
    
class MRV:
    """
    Implements the MRV heuristic, which returns one of the variables with smallest domain. 
    """
    def select_variable(self, word):

        # Set the smallest tentative domain to the largest possible domain
        smallest_domain = 27
        var = None
        # Iterate through cells
        for i in range(word.get_width()):
            if (len(word.get_cells()[i]) < smallest_domain and len(word.get_cells()[i]) != 1):
                smallest_domain = len(word.get_cells()[i])
                var = i

        if var is None:
            pass

        return var

class AC3:

    def consistency(self, word):
        pass

    def remove_domain_pairs(self, word):
        for i in range(word.get_width()):
            if len(word.get_cells()[i]) == 1:
                # For each letter that we know exists in the word we want to constrain variables on either side
                # If the letter is in the first variable we only need to constrain the variable to the right, i.e. check cases where the letter is the first letter in the impossible pair
                # If the letter is the 2nd,3rd,4th variable, we need to check cases where the letter is in either pair and constrain variables on either side accordingly
                # If the letter is the 5th variable, we only need to constrain the variable to the left, i.e. check cases where the letter is the second letter in the impossible pair
                for pair in impossible_pairs:
                    if i == 1 or i == 2 or i == 3:
                        if word.get_cells()[i] == pair[0]:
                            new_domain = word.get_cells()[i+1].replace(pair[1], '')
                            word.get_cells()[i+1] = new_domain
                        if word.get_cells()[i] == pair[1]:
                            new_domain = word.get_cells()[i-1].replace(pair[0], '')
                            word.get_cells()[i-1] = new_domain
                    elif i == 0:
                        # This is the first variable in the word
                        if word.get_cells()[i] == pair[0]:
                            new_domain = word.get_cells()[i+1].replace(pair[1], '')
                            word.get_cells()[i+1] = new_domain
                    elif i == 4:
                        if word.get_cells()[i] == pair[1]:
                            new_domain = word.get_cells()[i-1].replace(pair[0], '')
                            word.get_cells()[i-1] = new_domain
                        # This is the last variable in the word
                pass


        pass

class Backtracking:

    def search(self, word, var_selector, ac3):

        if word.is_solution():
            return word
        

        i = var_selector.select_variable(word)
        print("Selecting new variable ", i)

        if i is None:
            return None
        
        for letter in word.get_cells()[i]:
            if word.get_yellow_letters():
                # If there are yellow cells
                print(word.get_yellow_letters())
                word.remove_yellow_letters(letter)


            copy_word = word.copy()
            copy_word.get_cells()[i] = letter

            # FIXME: Somehow check and maintain yellow letter list such that it stays at the front of the domain list until it has been found (across words specifically)
            # For example, if we guess WATER and then another word but we didn't find the right spot for T, then T will not be at the front of the domain list once we enter a new word,
            # even though it is still a priority value to find
            # Same thing if the letters are grey - the list of letters is not maintained
            # Will probably have to write a separate function to do this because init_cells() does this but is only called once

            # Lets say the word is WATER and the outcome is XXYXX. We put T to the front of the domains of all over variables but the middle one
            # Whatever variable is next chosen by MRV will be set to T. Now we should remove T from the front of the domain of the other variables.
            # Perhaps instead of moving the domain of T to the front of the queue we just add it to the front of the queue and keep 2 copies of the T in the domain list?
            # This way it would be easier to remove from the front of the queue without having to manually re-add it into the domain list.

            # If we implement this then I think that our algorithm will be a lot better because it will actually keep in priority the letters we still need to find
            # Although things may be tricky when dealing with creating new Word objects and maintaining this list of yellow variables to keep.

            ac3.remove_domain_pairs(copy_word)
            print(copy_word.get_cells())
            rb = self.search(copy_word, var_selector, ac3)
            if rb and rb.is_solution():
                return rb

        return None



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
    word = Word()  # Initialize Word object outside the loop

    file = open('valid-wordle-words.txt', 'r')
    for valid_word in file:
        valid_word = valid_word.strip()
        valid_words.append(valid_word)
    
    file = open('impossible-letter-combos.txt', 'r')
    for pair in file:
        pair = pair.strip()
        impossible_pairs.append(pair)

    while True:
        guessed_word = input("Please enter the word you guessed: ").upper()

        if not is_valid_word(guessed_word):
            break

        print("\nPlease indicate the result of your guess")

        result_guessed_word = input("X = letter is gray\nY = letter is yellow\nG = letter is green\n: ").upper()

        if not is_valid_result(result_guessed_word):
            print("NOT A VALID INPUT")
            break
        
        # Update the existing Word object with the obtained guess information

        word.init_cells(guessed_word, result_guessed_word)
        #print(word.get_cells())

        mrv = MRV()
        ac3 = AC3()
        ac3.remove_domain_pairs(word)

        bt = Backtracking()
        sol = bt.search(word.copy(), mrv, ac3)
        print(sol.get_cell_string())