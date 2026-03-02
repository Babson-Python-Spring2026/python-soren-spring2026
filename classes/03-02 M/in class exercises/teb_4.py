#Goal: Keep asking until division works
# Keep asking for two numbers until division succeeds.

while True:

    numerator = input('enter numerator: ')
    denominator = input('enter denominator: ')
    try:
        quotient = int(numerator) / int(denominator)
        break
    except ZeroDivisionError:
        print('try again zero divide\n')
    except ValueError:
        print('try again, no text\n')

print(quotient)
