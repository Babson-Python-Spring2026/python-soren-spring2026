

while True:
    print("\nEntered OUTER loop")

    cmd_outer = input("Press c to run inner loop (enter to break outer): ")

    if cmd_outer == "":
        print("Breaking OUTER loop")
        break

    while True:
        print("   Inside INNER loop")

        cmd_inner = input("   Press c to repeat inner (enter to break inner): ")

        if cmd_inner == "":
            print("   Breaking INNER loop")
            break

