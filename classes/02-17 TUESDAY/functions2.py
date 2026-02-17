import os
import time

def clear_screen():
    #only works in py files
    os.system("cls" if os.name == "nt" else "clear")

def pause(n=None):
    if n is None:
        input("Press Enter to continue...")
    else:
        time.sleep(n)

def print_header(title, n = 80):
    print("=" * n)
    print(title.center(n))
    print("=" * n + '\n\n')

def get_int(prompt):
    while True:
        try:
            num = input(prompt)
            if num == '': return None
            return int(num)
        except ValueError:
            prompt("Please enter a valid integer: ")

def get_float(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Please enter a valid number.")

def confirm(prompt):
    while True:
        answer = input(prompt + " (y/n): ").lower()
        if answer in ("y", "yes"):
            return True
        elif answer in ("n", "no"):
            return False
        else:
            print("Please enter y or n.")

def format_currency(amount):
    return f"${amount:,.2f}"

def print_dict(d):
    for key, value in d.items():
        print(f"{key}: {value}")

def safe_get(d, key, default = 'NOKEY'):
    return d.get(key, default)

def display_menu(options):
    for i, option in enumerate(options, start=1):
        print(f"{i}. {option}")

def get_menu_choice(options):
    while True:
        choice = get_int("\n\nSelect option: ")
        if choice == None: return None
        if 1 <= choice <= len(options):
            return choice
        print("Invalid selection.")

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
    
#text = read_file("text.txt")
#contents = text.splitlines() if text is not None else []

def write_file(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)