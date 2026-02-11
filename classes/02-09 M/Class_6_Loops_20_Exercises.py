# %%
# Exercise 1
# ### Exercise 1
# Print the numbers 1–10, one per line.

# %%
# TODO: write your solution below
for i in range(1,11):
    print(i)

# %%
# Exercise 2
# ### Exercise 2
# Print only the even numbers from 0–20.

# %%
# TODO: write your solution below
for i in range(21):
    if i % 2 == 0:print(i)

# %%
# Exercise 3
# ### Exercise 3
# Given `word = "banana"`, count how many `'a'` characters appear.

# %%
# TODO: write your solution below
x = 'banana'
count = x.count('a')
    
print(count)

count = 0
for chr in x:
    if chr == 'a':
        count += 1

print(count)

# %%
# Exercise 4
# ### Exercise 4
# Given two lists:
# ```python
# names = ["Bob", "Alice", "Jen"]
# scores = [88, 92, 95]
# ```
# Print each name with its score.

# %%
# TODO: write your solution below
names = ["Bob", "Alice", "Jen"]
scores = [88, 92, 95]

for name, score in zip(names, scores):
    print(name, score)

# %%
# Exercise 5
# ### Exercise 5
# Given:
# ```python
# d = {"a": 1, "b": 2, "c": 3}
# ```
# Print each key-value pair in the format `a -> 1`.

# %%
# TODO: write your solution below
d = {"a": 1, "b": 2, "c": 3}

for key, value in d.items():
    print(f"{key} -> {value}")

# %%
# Exercise 6
# ### Exercise 5.6 (Continue)
# Given a list of integers, build a new list containing only the positive numbers.
# 
# Use `continue` to skip negatives and zero.

# %%
# TODO: write your solution below
numbers = [4, -2, 0, 7, -5, 3]

positives = []

for n in numbers:
    if n <= 0:
        continue
    positives.append(n)

print(positives)

# %%
# Exercise 7
# ### Exercise 5.7 (Pass)
# Create a loop that prints each character in a string, but **leave a placeholder** for handling vowels later using `pass`.

# %%
# TODO: write your solution below


# %%
# Exercise 8
# ### Exercise 6
# Use a `while` loop to print numbers from 10 down to 1.

# %%
# TODO: write your solution below


# %%
# Exercise 9
# ### Exercise 7
# Repeatedly ask for input until the user types `"quit"`.

# %%
# TODO: write your solution below


# %%
# Exercise 10
# ### Exercise 8
# Given a 3×3 grid (list of lists), print only the diagonal elements.

# %%
# TODO: write your solution below


# %%
# Exercise 11
# ### Exercise 9
# Given a list of dictionaries representing products, print the names of all products costing more than $50.

# %%
# TODO: write your solution below


# %%
# Exercise 12
# ### Exercise 10
# Given a dictionary mapping names to lists of scores, find the student with the highest average.

# %%
# TODO: write your solution below


# %%
# Exercise 13
# ### Exercise 11 — Rotate / Shift a List
# Given:
# ```python
# lst = ['a', 'b', 'c', 'd', 'e']
# ```
# Shift the elements **2 to the right** to end up with:
# ```python
# ['d', 'e', 'a', 'b', 'c']
# ```
# 
# Constraints:
# - Use a loop (no slicing shortcuts like `lst[-2:] + lst[:-2]` for the main solution).

# %%
# TODO: write your solution below


# %%
# Exercise 14
# ### Exercise 12 — Flatten a 3×3 Matrix to a List
# Given:
# ```python
# matrix = [
#     ['A',  'B',  'C'],
#     ['D',  'E',  'F'],
#     ['G',  'H',  'I']
# ]
# ```
# Convert to:
# ```python
# ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
# ```
# Use nested loops.

# %%
# TODO: write your solution below


# %%
# Exercise 15
# ### Exercise 13 — Unflatten a List into a 3×3 Matrix
# Given:
# ```python
# flat = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
# ```
# Convert to:
# ```python
# [
#     ['A',  'B',  'C'],
#     ['D',  'E',  'F'],
#     ['G',  'H',  'I']
# ]
# ```
# Use loops (you may use `range`).

# %%
# TODO: write your solution below


# %%
# Exercise 16
# ### Exercise 14 — Are These Two Matrices the Same?
# Is:
# ```python
# [
#     ['A',  'B',  'C'],
#     ['D',  'E',  'F'],
#     ['G',  'H',  'I']
# ]
# ```
# the same as:
# ```python
# [ ['A',  'B',  'C'], ['D',  'E',  'F'], ['G',  'H',  'I'] ]
# ```
# 
# Answer in two parts:
# 1. Are they **equal** (`==`)?
# 2. Are they the **same object** (`is`)?

# %%
# TODO: write your solution below


# %%
# Exercise 17
# ### Exercise 15 — Build a Histogram (Dictionary of Counts)
# Given a string, build a dictionary mapping each character to its count.
# Ignore spaces.

# %%
# TODO: write your solution below


# %%
# Exercise 18
# ### Exercise 16 — First Vowel Search (use `break`)
# Given a string, find the **first vowel** and its index.
# Stop as soon as you find one.
# If there is no vowel, report that.

# %%
# TODO: write your solution below


# %%
# Exercise 19
# ### Exercise 17 — Filter a List Using `continue`
# Given a list of integers, build a new list containing only numbers that are:
# - positive
# - divisible by 3
# 
# Use `continue` to skip everything else.

# %%
# TODO: write your solution below


# %%
# Exercise 20
# ### Exercise 18 — Sum Each Row and Each Column (Nested Loops)
# Given a 3×3 matrix of numbers:
# - compute the sum of each row (3 sums)
# - compute the sum of each column (3 sums)
# 
# Store results in two lists: `row_sums` and `col_sums`.

# %%
# TODO: write your solution below

