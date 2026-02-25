# -------------------------------
# Example 1 — Flat list (ints)
# -------------------------------

a = [1,2,3]          # a → L1
b = a.copy()         # b → L2 (new outer list)

# After copy:
# a → L1  = [1,2,3]
# b → L2  = [1,2,3]
# Elements (1,2,3) are the same objects in both lists,
# but the outer lists L1 and L2 are different objects.

b[0] = 99            # Rebinding slot 0 inside L2

# This replaces the reference in L2 only.
# It is an assignment and only affects b.
# It changes which object L2[0] refers to.

print(a,b)
# a = [1,2,3]
# b = [99,2,3]


# -------------------------------
# Example 2 — Nested list (shallow copy)
# -------------------------------

a = [[1,2], [3,4]]
b = a.copy()

# After shallow copy:
# a → L1 = [L3, L4]
# b → L2 = [L3, L4]
#
# L1 and L2 are different outer lists.
# But L3 and L4 (the inner lists) are SHARED.

b[0][0] = 99         # Mutating shared inner list L3

# Step-by-step:
# b[0] → L3
# L3[0] = 99  (assignment of slot 0 in the inner list, modifies L3)
#
# Since a[0] also points to L3,
# both a and b see the change.

print(a,b)
# a = [[99,2], [3,4]]
# b = [[99,2], [3,4]]

# Both a[0] and b[0] refer to the same object L3.


# -------------------------------
# Solution — Deep copy
# -------------------------------

from copy import deepcopy

a = [[1,2], [3,4]]
b = deepcopy(a)

# After deep copy:
# a → L1 = [L3, L4]
# b → L2 = [L5, L6]
#
# Outer lists are different.
# Inner lists are ALSO different.
#
# (Leaf elements may still be shared internally, but the INNER LISTS are not shared.
# So an assignment like L5[0] = 88 only rebinds a slot in L5 and cannot affect L3.)

b[0][0] = 88         # Mutates L5 only

# Since a[0] refers to L3 (not L5),
# a is unaffected.

print(a,b)
# a = [[1,2], [3,4]]
# b = [[88,2], [3,4]]

