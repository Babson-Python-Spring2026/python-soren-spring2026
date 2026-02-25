# ---------------------------------------------------------
# MENU_DATA
#
# This dictionary defines the ENTIRE menu system.
#
# Each key (like "HOME", "CLIENTS", etc.) represents
# one "menu screen" (also called a frame or state).
#
# Each menu has:
#   - a "title" (what we display at the top)
#   - an "options" list
#
# Each option is a dictionary with either:
#   - "goto": go to another menu (a transition)
#   - "action": perform an action (a leaf node)
#
# Non-leaf menus use "goto".
# Leaf menus use "action".
# ---------------------------------------------------------
MENU_DATA = {
    # =========================
    # Level 1
    # =========================
    "HOME": {
        "title": "Home",
        "options": [
            {"text": "Clients", "goto": "CLIENTS"},
            {"text": "Portfolios", "goto": "PORTFOLIOS"},
        ],
    },

    # =========================
    # Level 2 (Clients branch)
    # =========================
    "CLIENTS": {
        "title": "Clients",
        "options": [
            {"text": "Select Client", "goto": "SELECT_CLIENT"},
            {"text": "Create Client", "goto": "CREATE_CLIENT"},
        ],
    },

    # =========================
    # Level 3 (Select Client branch)
    # =========================
    "SELECT_CLIENT": {
        "title": "Select Client Options",
        "options": [                      
            {"text": "View Client Summary", "goto": "VIEW_CLIENT_SUMMARY"},
            {"text": "Manage Client Cash", "goto": "MANAGE_CLIENT_CASH"},           
        ],
    },


    # =========================
    # Level 4 (leaf action)
    # =========================
    "VIEW_CLIENT_SUMMARY": {
        "title": "View Client Summary Page",
        "options": [                        
            {"text": "View Client Summary", "action": "RETURN"},            
        ],
    },
    # =========================
    # Level 4 (leaf action)
    # =========================
    "MANAGE_CLIENT_CASH": {
        "title": "Manage Client Cash Page",
        "options": [ 
            {"text": "Manage Client Cash", "action": "RETURN"},
        ],
    },


    # =========================
    # Level 3 (Create Client branch)
    # =========================
    "CREATE_CLIENT": {
        "title": "Create Client",
        "options": [
            {"text": "New Individual", "goto": "CREATE_INDIVIDUAL"},
            {"text": "New Joint", "goto": "CREATE_JOINT"},
            
        ],
    },
    # =========================
    # Level 4 (leaf action)
    # =========================
    "CREATE_INDIVIDUAL": {
        "title": "New Individual Page",
        "options": [            
            {"text": "New Individual", "action": "RETURN"},            
        ],
    },
    # =========================
    # Level 4 (leaf action)
    # =========================
    "CREATE_JOINT": {
        "title": "New JOINT Page",
        "options": [            
            {"text": "New Joint", "action": "RETURN"},            
        ],
    },

    # =========================
    # Level 2 (Portfolios branch)
    # =========================
    "PORTFOLIOS": {
        "title": "Portfolios",
        "options": [
            {"text": "Trade", "goto": "TRADE"},
            {"text": "Performance", "goto": "PERFORMANCE"},
        ],
    },

    # =========================
    # Level 3 (Trade branch)
    # =========================
    "TRADE": {
        "title": "Trade",
        "options": [
            {"text": "Buy", "goto": "BUY"},
            {"text": "Sell", "goto": "SELL"},            
        ],
    },
    # =========================
    # Level 4 (leaf action)
    # =========================
    "BUY": {
        "title": "the BUY action",
        "options": [            
            {"text": "BUY", "action": "RETURN"},            
        ],
    },
    # =========================
    # Level 4 (leaf action)
    # =========================
    "SELL": {
        "title": "the SELL action",
        "options": [            
            {"text": "SELL", "action": "RETURN"},            
        ],
    },            
    # =========================
    # Level 3 (Performance branch)
    # =========================
    "PERFORMANCE": {
        "title": "Performance",
        "options": [
            {"text": "Holdings Snapshot", "goto": "HOLDINGS_SNAPSHOT"},
            {"text": "P/L Report", "goto": "PL_REPORT"},  
        ],
    },
    # =========================
    # Level 4 (leaf action)
    # =========================
    "HOLDINGS_SNAPSHOT": {
        "title": "Holdings Snapshot Page",
        "options": [            
            {"text": "Holdings Snapshot", "action": "RETURN"},            
        ],
    },
    # =========================
    # Level 4 (leaf action)
    # =========================
    "PL_REPORT": {
        "title": "P/L Report Page",
        "options": [            
            {"text": "P/L Report", "action": "RETURN"},            
        ],
    },       
}
from myImports import functions as fn


# The stack keeps track of where we are in the menu system.
# The LAST item in the list is always the current menu.
menu_stack = ['HOME']
prn_flg = True
def display_goto(current_menu):
    # Clear the screen and print the title of the current menu
    if prn_flg:fn.clear_screen()
    title = current_menu['title']
    fn.print_header(title)

    # Get all options for this menu
    options = current_menu['options']     

    # Build a simple list of (text, destination)
    # text gets displayed as an option destination
    # is the menu we go to if that option is selected.
    
    menu_list = []
    for opt in options:
        if 'goto' in opt:
            menu_list.append((opt['text'], opt['goto']))  


    # Display the numbered menu and get how many choices exist
    choices = fn.display_menu(menu_list)    

    print('\n\n')
    # get return or a valid number from the menu
    choice_num = fn.get_selection(choices, "Enter your selection: ")

    # check choice_num for return -> indicates to go back to previous menu
    if choice_num is None:
        menu_stack.pop()
        if prn_flg:       # clears screen if we have bad input and had to enter again
            fn.clear_screen()
        return 
    

    # Convert to zero-based index
    selection_index = choice_num - 1

    # Find which menu we are going to
    next_menu_id = menu_list[selection_index][1]  # get the destination key 
   
    # Look up the next menu in MENU_DATA
    next_menu = MENU_DATA[next_menu_id]

    # ----------------------------------------
    # CHECK: Is this a leaf (action-only)?
    # ----------------------------------------
    if 'action' in next_menu['options'][0]:
        # If yes, perform the leaf action
        leaf_action(next_menu)
        return
    else:
        # Otherwise, push the next menu onto the stack
        # This is the "transition" in our state machine
        menu_stack.append(next_menu_id)
        return



def leaf_action(leaf):
    # Leaf menus do not transition to another menu.
    # Instead, they perform some action.

    if prn_flg:fn.clear_screen()
    title = leaf['title']
    fn.print_header(title)

    print('\n\n\n')
    print('You have reached ' + title)
    print('pausing and returning to top\n\n')

    fn.pause(4)

    # After a leaf action, we reset to HOME
    menu_stack.clear()
    menu_stack.append('HOME')

# -----------------------------------------
# MAIN ENGINE LOOP
#
# This loop runs the entire menu system.
#
# It keeps running as long as there is
# something in the stack.
#
# The current menu is ALWAYS the last
# item in menu_stack.
# -----------------------------------------

while menu_stack:

    # The current menu ID is the last item
    current = menu_stack[-1]

    # Look up that menu in MENU_DATA
    current_menu = MENU_DATA[current]

    
    # Display it and handle one transition
    display_goto(current_menu)

    






