class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)
    
    def checkSquare(self):
        if self.width == self.height:
            return True
        else:
            return False
    
rec1 = Rectangle(5,10)
rec2 = Rectangle(3,3)

print(rec1.area())
print(rec1.perimeter())
print(rec1.checkSquare())


# other practice

class Box:
    def __init__(self, value):
        self.value = value
    def add_one(self):
        self.value += 1

my_int = Box(5)
print(my_int.value)

class Student:
    def __init__(self, name, score):
        self.name = name
        self.score = score
    def describe(self):
        print(f'{self.name} has a grade of {self.score}')

