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
        self._grey_letters = ['','','','','']
        self._complete_domains = ["SPBCMTARDGFLHNWKOEVJUYIZQX",
                                  "AOEIURLHNYTPMCWKSBDGXVFZQJ",
                                  "ARINOELUTSMCDGPBKWVYFZHXJQ",
                                  "EAITNLORSKDUGPCMHBFVZWYJXQ",
                                  "SEYADTRNLOHIKMGPCUFXBWZVQJ"]


    def init_cells(self, word_string, result_string):
        """
        This function takes in the word the user guessed and the result of that word and sets the initial domain of each cell accordingly

        If a letter in a guessed word is grey, that letter is removed from the domain of all variables and added to a list of grey letters for all variables
        If a letter in a guessed word is yellow, that letter is removed from the domain of the variable, added to the grey list of that variable, and put into the yellow letter list
        If a letter in a guessed word is green, the domain of the variable is set to that letter
        """
        word = list(word_string)
        result = list(result_string)
        row = []
        self._cells = []

        for i in range(len(word_string)):
            # If the letter is in the word and in the correct location
            if result[i] == 'G':
                row.append(word[i])
                if word[i] in self.get_yellow_letters():
                    self.remove_yellow_letters(word[i])

            # If the letter is not in the word
            if result[i] == 'X':
                # Remove 
                row.append(self._complete_domains[i].replace(word[i], ''))
                if word[i] not in self._grey_letters[i] and word[i] not in self._yellow_letters:
                    for j in range(len(self.get_grey_letters())):
                        self._grey_letters[j] += word[i]

            if result[i] == 'Y':
                row.append(self._complete_domains[i].replace(word[i], ''))
                #row.append(word[i] + self._complete_domains[i])
                self._grey_letters[i] += word[i]
                if word[i] not in self._yellow_letters:
                    self._yellow_letters.append(word[i])
                if len(self.get_yellow_letters()) > 5:
                    print("\nList of yellow letters is impossibly large: ", len(self.get_yellow_letters()))
                    print("Did you enter in something wrong?")
                    exit()

        self._cells.extend(row)
        
        for i, (domain, grey_letters) in enumerate(zip(self.get_cells(), self.get_grey_letters())):
            if len(self.get_cells()[i]) != 1:
                self.get_cells()[i] = ''.join([char for char in domain if char not in grey_letters])
        print("Grey letters ", self.get_grey_letters())


        '''
        We want to prioritize guessing letters that are yellow, as we know they exist in the word.
        If a yellow letter exists in the domain of a variable, we add a copy of the letter to the beginning of the domain so that it gets priority in being chosen in the next generated word
        '''
        for yellow_letter in self._yellow_letters:
            for i in range(len(self.get_cells())):
                if yellow_letter in self.get_cells()[i] and len(self.get_cells()[i]) != 1:
                    new_domain = self.get_cells()[i]
                    self.get_cells()[i] = yellow_letter + new_domain


        self.check_only_option()


        pass
    
    def check_only_option(self):
        '''
        This function deals with the case where there is only one possible spot a yellow letter can be based off previous guesses.
        If there is, we set the domain of that one possible spot to the yellow letter in question

        For example, we guess:
        SORER -> result: XXYGG
        then,
        PRIER -> result: XYYGG

        We know that the only possible spot for 'R' to be in is in variable 1, the first spot
        ''' 
        possible_single = 0
        candidate = 0
        letter = 0

        for i in range(len(self.get_yellow_letters())):
            count = 0
            for j in range(len(self.get_grey_letters())):
                count += 1
                if possible_single > 1:
                    break
                elif self.get_yellow_letters()[i] not in self.get_grey_letters()[j] and len(self.get_cells()[j]) != 1:
                    possible_single += 1
                    candidate = j
                    letter = i
            if count == 5 and possible_single == 1:
                self.get_cells()[candidate] = self.get_yellow_letters()[letter]

        pass

    def check_all_variables_assigned(self):
        for i in range(self.get_width()):
            if len(self.get_cells()[i]) != 1:
                return False
        
        return True
    
    def check_all_yellow_letters_included(self):
        
        for i in range(len(self.get_yellow_letters())):
            if self.get_yellow_letters()[i] not in self.get_cell_string():
                return False
            
        return True
    
    def deprioritize_domain(self, letter):
        """
        Removes the domain 
        
        """
        print(self.get_cells())
        print("Letter to deprio: ", letter)
        for i in range(self.get_width()):
            if len(self.get_cells()[i]) == 1:
                continue
            if self.get_cells()[i].count(letter) != 1:
                index = self.get_cells()[i].find(letter)
                print(i,index)
                if index != -1:
                    new_domain = self.get_cells()[i].replace(letter, '',1)
                    self.get_cells()[i] = new_domain

        
        #FIXME: Might be removing all instances of the letter instead of just the first one
        print("NEW DOMAIN AFTER DEPRIO: ", self.get_cells())

        


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
        copy_word._grey_letters = [cell[:] for cell in self._grey_letters]
        return copy_word
    
    def get_cells(self):
        return self._cells
    
    def get_width(self):
        return self._width

    def is_solution(self):
        if self.get_cell_string().lower() in valid_words:
            return True
        return False
    
class VarSelector:
    """
    Implements the MRV heuristic, which returns one of the variables with smallest domain. 
    """
    def select_variable(self, word):

        # Set the smallest tentative domain to the largest possible domain
        smallest_domain = 27
        var_smallest_domain = None
        yellow_letter_count = 100
        var_least_yellow_letter = None

        print("In varselector: ", word.get_yellow_letters())

        # If there are no yellow letters in the word, pick the variable with the smallest domain

        if not word.get_yellow_letters():
            for i in range(word.get_width()):
                if (len(word.get_cells()[i]) < smallest_domain and len(word.get_cells()[i]) != 1):
                   smallest_domain = len(word.get_cells()[i])
                   var_smallest_domain = i
            return var_smallest_domain
        
        # If there are yellow letters in the word, pick the variable with the least of them
        for i in range(word.get_width()):
            temp_count = 0
            for yellow_letter in word.get_yellow_letters():
                if yellow_letter in word.get_cells()[i] and len(word.get_cells()[i]) != 1:
                    temp_count += word.get_cells()[i].count(yellow_letter)
            if temp_count < yellow_letter_count and temp_count != 0:
                yellow_letter_count = temp_count
                var_least_yellow_letter = i
        return var_least_yellow_letter

class AC3:

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
    def __init__(self):
        self._iteration_count = 0
        self._initial_domains = []
        self._initial_yellow_letters = []
        # Change the selector if the previous search did not yield a valid word
        self._previous_selector = 0

    def get_iteration_count(self):
        return self._iteration_count
    
    def get_initial_domains(self):
        return self._initial_domains
    def get_initial_yellow_letters(self):
        return self._initial_yellow_letters
    
    def copy_initial_domains(self, word):
        copy_list = word.get_cells().copy()
        self._initial_domains = copy_list
        return copy_list
    
    def copy_yellow_letters(self,word):
        copy_list = word.get_yellow_letters().copy()
        self._initial_yellow_letters = copy_list
        return copy_list
    
    def pre_search(self,word,var_selector,ac3):
        pass   

    def search(self, word, var_selector, ac3):

        if self.get_iteration_count() == 0:
            print("Copy of domain for word: ",self.copy_initial_domains(word))
            print("Copy of yellow letters for word:", self.copy_yellow_letters(word))
            # This is the first iteration

        self._iteration_count += 1

        if word.is_solution():
            print("This is a solution too!")
            return word
        elif word.check_all_variables_assigned() and not word.is_solution() and not word.check_all_yellow_letters_included():
            # If the order of the letters does not reach a valid solution, we reset the domains to when the results were first entered

            #FIXME: If all yellow letters are present in the domains of all variables but we still haven't found a word, I still want to search through the domains and try each letter
            # But only if all yellow letters have been accounted for
            # How to do this? First check that all yellow letters have been placed first, then once this happens, we can allow the search to loop through all letters for the remaining variables until a valid word is reached
            #   Multiple options to change outcome of letter search:
            #   - change selected variable from the one previously selected
            #   - change order of domain


            #FIXME: Also check that all other word attributes are being reset accordinly

            
            word._cells = self.get_initial_domains()
            word._yellow_letters = self.get_initial_yellow_letters()
            print("Resetting initial domains: ", word.get_cells())
            print("Resetting initial yellows: ", word.get_yellow_letters())

        print(word.get_cells())
        i = var_selector.select_variable(word)

        print("Selector: ", i)

        if i is None:
            print(word.get_cell_string())
            return None
        
        #FIXME: If yellow letters exist, and are put into the word but a word is not found with those combinations (selector is None), try to reset back and try a different combination of the yellow letters
        # Not quite sure how to logistically do that
        # For example, Water => xyxyy into rheas -> ygyyy produces SHRUG
        # A way to fix it would have to be stopping backtracking and re-choosing variables
        # Maybe dynamically change the domains of the variables depending on what letters are beside it?
        
        for letter in word.get_cells()[i]:
            copy_word = word.copy()
            copy_word.get_cells()[i] = letter
            if letter in copy_word.get_yellow_letters():
                # If the letter selected is in the yellow letter list
                copy_word.deprioritize_domain(letter)
                copy_word.remove_yellow_letters(letter)

            ac3.remove_domain_pairs(copy_word)

            #print("copy of init domain: ",self.get_initial_domains())
            print(copy_word.get_cells())


            rb = self.search(copy_word, var_selector, ac3)
            if rb and rb.is_solution():
                print("This is a solution!")
                return rb
            
        return None



def is_valid_result(result_guessed_word):
    if result_guessed_word == "I WON!":
        print("\nYAY! Thanks for playing!")
        exit()

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

    guessed_word = input("Please enter the word you guessed: ").upper()

    if not is_valid_word(guessed_word):
        exit()

    while True:

        print("\nFor the guess: ", guessed_word)
        print("\nPlease indicate the result of your guess")

        result_guessed_word = input("X = letter is gray\nY = letter is yellow\nG = letter is green\nOR type 'I WON!' if you won :)\n: ").upper()

        if not is_valid_result(result_guessed_word):
            print("NOT A VALID INPUT")
            break
        

        word.init_cells(guessed_word, result_guessed_word)

        var_selector = VarSelector()
        ac3 = AC3()
        ac3.remove_domain_pairs(word)

        bt = Backtracking()
        sol = bt.search(word.copy(), var_selector, ac3)
        if sol == None:
            print("No solution found :(")
            exit()
        else:
            print(sol.get_cell_string())
            guessed_word = sol.get_cell_string()