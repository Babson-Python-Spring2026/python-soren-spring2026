def print_menu_data(MENU_DATA):
    print("# ---------------------------------------------------------")
    print("# MENU_DATA")
    print("#")
    print("# This dictionary defines the ENTIRE menu system.")
    print("#")
    print("# Each key (like \"HOME\", \"CLIENTS\", etc.) represents")
    print("# one \"menu screen\" (also called a frame or state).")
    print("#")
    print("# Each menu has:")
    print("#   - a \"title\" (what we display at the top)")
    print("#   - an \"options\" list")
    print("#")
    print("# Each option is a dictionary with either:")
    print("#   - \"goto\": go to another menu (a transition)")
    print("#   - \"action\": perform an action (a leaf node)")
    print("#")
    print("# Non-leaf menus use \"goto\".")
    print("# Leaf menus use \"action\".")
    print("# ---------------------------------------------------------")
    print("MENU_DATA = {")

    # Print each menu
    for menu_id, menu in MENU_DATA.items():

        # Determine if leaf or not
        first_option = menu["options"][0] if menu["options"] else {}
        is_leaf = "action" in first_option

        print("    # =========================")
        if is_leaf:
            print("    # Leaf (action)")
        else:
            print("    # Goto menu")
        print("    # =========================")

        print(f'    "{menu_id}": {{')
        print(f'        "title": "{menu["title"]}",')
        print('        "options": [')

        for opt in menu["options"]:
            if "goto" in opt:
                print(f'            {{"text": "{opt["text"]}", "goto": "{opt["goto"]}"}},')
            else:
                print(f'            {{"text": "{opt["text"]}", "action": "{opt["action"]}"}},')

        print("        ],")
        print("    },\n")

    print("}")



"""
Given:
  EDGES  = list of (parent_id, parent_title, option_text, child_id)
  LEAVES = dict: leaf_id -> leaf_title

Produce:
  MENU_DATA in the exact format your menu engine expects.

Notes:
- Parents become "goto menus" (their options are goto-only).
- Leaves become "action menus" with a single RETURN action.
"""

import pprint

# ----------------------------
# Example inputs (replace with yours)
# ----------------------------

EDGES = [
    ("HOME", "Home", "Clients", "CLIENTS"),
    ("HOME", "Home", "Portfolios", "PORTFOLIOS"),
    ("CLIENTS", "Clients", "Select Client", "SELECT_CLIENT"),
    ("CLIENTS", "Clients", "Create Client", "CREATE_CLIENT"),
    ("SELECT_CLIENT", "View or Manage Client", "View Client Summary", "VIEW_CLIENT_SUMMARY"),
    ("SELECT_CLIENT", "View or Manage Client", "Manage Client Cash", "MANAGE_CLIENT_CASH"),
    ("CREATE_CLIENT", "Create Client", "New Individual", "CREATE_INDIVIDUAL"),
    ("CREATE_CLIENT", "Create Client", "New Joint", "CREATE_JOINT"),
    ("PORTFOLIOS", "Portfolios", "Trade", "TRADE"),
    ("PORTFOLIOS", "Portfolios", "Performance", "PERFORMANCE"),
    ("TRADE", "Trade", "Buy", "BUY"),
    ("TRADE", "Trade", "Sell", "SELL"),
    ("PERFORMANCE", "Performance", "Holdings Snapshot", "HOLDINGS_SNAPSHOT"),
    ("PERFORMANCE", "Performance", "P/L Report", "PL_REPORT"),
]

LEAVES = {
    "VIEW_CLIENT_SUMMARY": "View Client Summary Page",
    "MANAGE_CLIENT_CASH": "Manage Client Cash Page",
    "CREATE_INDIVIDUAL": "New Individual Page",
    "CREATE_JOINT": "New Joint Page",
    "BUY": "The BUY action",
    "SELL": "The SELL action",
    "HOLDINGS_SNAPSHOT": "Holdings Snapshot Page",
    "PL_REPORT": "P/L Report Page",
}

# ----------------------------
# Build MENU_DATA
# ----------------------------

MENU_DATA = {}

# 1) Build all goto-menus from EDGES
for parent_id, parent_title, option_text, child_id in EDGES:

    # Create the parent menu if it doesn't exist
    if parent_id not in MENU_DATA:
        MENU_DATA[parent_id] = {
            "title": parent_title,
            "options": []
        }

    # Add the goto option
    MENU_DATA[parent_id]["options"].append({
        "text": option_text,
        "goto": child_id
    })

# 2) Build all leaf menus from LEAVES
for leaf_id, leaf_title in LEAVES.items():
    MENU_DATA[leaf_id] = {
        "title": leaf_title,
        "options": [
            {"text": leaf_title, "action": "RETURN"}
        ]
    }

# ----------------------------
# Optional: sanity checks
# ----------------------------

# Check that every goto target exists in MENU_DATA
for menu_id, menu in MENU_DATA.items():
    for opt in menu["options"]:
        if "goto" in opt:
            target = opt["goto"]
            if target not in MENU_DATA:
                print(f"WARNING: {menu_id} has goto -> {target}, but {target} is not defined")

# ----------------------------
# Print the result
# ----------------------------

print("\nMENU_DATA produced:\n")
#pprint.pprint(MENU_DATA, width=100, sort_dicts=False)

print_menu_data(MENU_DATA)