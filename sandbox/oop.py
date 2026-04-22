'''
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        if value < 0:
            raise ValueError("width must be >= 0")
        self._width = value

r = Rectangle(3, 4)

txt = 'input width of retangle: '
while True:
    try:
        r.width = int(input(txt))  # ValueError
        break
    except ValueError as e:
        print(e)
'''

class Cat:
    def speak(self):
        print('meow')

class Dog:
    def speak(self):
        print('bowwow')

def speak(obj):
    obj.speak()

luna = Cat()
rover= Dog()

speak(luna)
speak(rover)