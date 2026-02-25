# ------------------------------------------------------------
# Default-argument memory model
# Given: def omg(a, b, c = [])
#
# Key rule:
#   The default object for c (the []) is created ONCE when the
#   def statement executes, and stored with the function.
#
# On a call:
#   - If you OMIT c, Python binds the local name c to the stored default object.
#     (default is ACCESSED)
#   - If you PASS c, Python binds the local name c to what you passed.
#     (default is NOT accessed)
#
# Also:
#   c.append(...) modifies the list object that c refers to.
# ------------------------------------------------------------


# -------------------------------
# omg — default ACCESSED and MODIFIED
# -------------------------------

def omg(a, b, c=[]):
    # If caller omits c:
    #   c is bound to omg's stored default list object (call it D0)
    #   default is ACCESSED here (by being used as the binding for c)
    c.append(a + b)
    # append MODIFIES the list object c refers to (D0 if default was used)
    print(a, b, c)

omg(1, 1)
# Call details:
#   c omitted -> default D0 is ACCESSED (c -> D0)
#   D0.append(2) -> default object is MODIFIED: D0 becomes [2]

omg(2, 3)
# Call details:
#   c omitted -> SAME default D0 is ACCESSED again (c -> D0)
#   D0.append(5) -> default object is MODIFIED again: D0 becomes [2, 5]


# -------------------------------
# omg1 — first call bypasses default; second call uses default
# -------------------------------

def omg1(a, b, c=[]):
    # Default exists (call it E0) but is only used if c is omitted.
    c.append(a + b)          # modifies whatever list c refers to
    print(a, b, c)

omg1(1, 1, [])
# Call details:
#   c provided -> default E0 is NOT ACCESSED
#   c -> a brand-new empty list created at the call site (call it L1)
#   L1.append(2) -> L1 is MODIFIED to [2]
#   default E0 remains unchanged (still [])

omg1(2, 3)
# Call details:
#   c omitted -> default E0 IS ACCESSED (c -> E0)
#   E0.append(5) -> default object IS MODIFIED to [5]


# ------------------------------------------------------------
# omg2 — default is ACCESSED but (often) NOT MODIFIED
#
# WARNING: this pattern has a semantic gotcha:
#   "if not c:" triggers for ANY empty list the caller passes.
#   That means it may discard the caller's list even when they
#   passed it intentionally.
# ------------------------------------------------------------

def omg2(a, b, c=[]):
    # If caller omits c:
    #   c initially binds to omg2's stored default list object (call it F0)
    #   default is ACCESSED here (as the initial binding for c)
    if not c:
        # If c is empty, we REBIND c to a NEW list object.
        # This does NOT modify F0; it simply stops using it.
        c = []

    c.append(a + b)
    # append MODIFIES the list object c refers to (the NEW list if we rebounded)
    print(a, b, c)

omg2(1, 1)
# Call details:
#   c omitted -> default F0 is ACCESSED (c -> F0, which starts as [])
#   if not c is True -> c is REBOUND to a NEW list (call it L2)
#   L2.append(2) -> L2 is MODIFIED to [2]
#   default F0 was NOT MODIFIED (it stayed [])

omg2(2, 3)
# Call details:
#   c omitted -> default F0 is ACCESSED again (still [])
#   if not c is True -> c is REBOUND to a NEW list (call it L3)
#   L3.append(5) -> L3 is MODIFIED to [5]
#   default F0 still NOT MODIFIED


# ------------------------------------------------------------
# (Optional) The clean idiom (for reference):
#
# def omg_fixed(a, b, c=[]):
#     if not c:
#         c = []
#     c.append(a+b)
#     print(a, b, c)
#
# Here:
#   - Default [] is always rebind to []
#  The default is looked at, but never modified
# ------------------------------------------------------------

