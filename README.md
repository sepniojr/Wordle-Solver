# Python Wordle Solver

This is my Wordle Solver, which I developed while taking **CMPUT 366 - Search and Planning in AI** at the University of Alberta. I was inspired by the constraint satisfaction problem (CSP), and saw Wordle as an opportunity to model a CSP for myself using the Arc-Consistency 3 algorithm.

# User Guide

To run this program, you will need to have some version of Python 3 installed. During development, I used v3.11.9.

Simply enter `python3 wordlesolver.py` to run the program.

With Wordle open in your browser, you will make your first guess on the Wordle website. Then, you enter the guess you made into the program.

You must then indicate the result of this guess, by entering a 5-letter string which contains X's, Y's, and G's:

-   X = letter is gray
-   Y = letter is yellow
-   G = letter is green

After entering the result of the guess, the program will offer the next word to guess. Do this enough times, and hopefully you will get the right answer!

# Disclaimer

This program isn't perfect, and I'm sure there are plenty of bugs that you'll run into. While this program _tries_ to solve Wordle in Hard Mode (Meaning that it will use all green and yellow letters given to it to find a new word), it runs into situations where it won't always use the yellow letters that it is given. I noticed that this only happens when there are 2 copies of a letter in a word, but even then it happens rarely.

I found throughout my testing that this program seems to solve Wordle correctly about 95% of the time and takes around 4-6 guesses to get it right.

If I ever revisit this project, I think it would be interesting to look into different ways to optimize the search algorithm as well as ensure that the program is always solving the Wordle in Hard Mode. Looking into other methods for determining letter frequency in words would also be quite interesting.

# Acknowledgements

-   https://www.jojhelfer.com/lettercombos : This was a super helpful resource for doing pre-processing on words and reducing the domain of letters.
-   https://gist.github.com/dracos/dd0668f281e685bad51479e5acaadb93 : A list of the possible Wordle words, which made this whole project possible.
