def word_histogram(text):
    """
    Given a string of text, return a dictionary
    mapping each word to its frequency.
    Assume:
    - Words are separated by whitespace.
    - Convert words to lowercase.
    - Ignore punctuation.
    Example:
    "apple banana apple" -> {'apple': 2, 'banana': 1}
"""
    txt ='''the cat in the hat is back. is the cat back or is the hat back. 
if all cats have hats do all hats have cats. which really wears which? 
does the cat wear the hat or does the hat wear the cat?'''.lower()
    print(txt)

word_histogram('''the cat in the hat is back! is the cat back or is the hat back? 
if all cats have hats do all hats have cats. which really wears which? 
does the cat wear the hat or does the hat wear the cat?''')