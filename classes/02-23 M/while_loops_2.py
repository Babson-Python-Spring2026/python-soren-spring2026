
import msvcrt

print('Press any key to run loop or enter return to break out of loop: ')
while True:
    print("\nEntered OUTER loop")

    key = msvcrt.getch()
    key = key.decode()
    
    if key == "\r":
        print("Breaking OUTER loop")
        break

    while True:
        print("   Inside INNER loop")
        
        key = msvcrt.getch()
        key = key.decode()
    
        if key == "\r":
            print("Breaking inner loop")
            break
