class BankAccount:
    
    bank_name = 'Babson Bank'
    
    def __init__(self, name, amount):
        self.name = name
        self.amount = amount

    def __str__(self):
        return f'my account name is {self.name} and the balance is ${self.amount:,.2f}'
    # returns amount as an f string as a float to 2 decimal points
    def __add__(self, other):
        name = self.name + ' and ' + other.name
        amount = self.amount + other.amount
        a = BankAccount(name, amount)
        return a
    @property
    def name(self):
        if len(self._name) == 3: self._name = 'jim'
        # error checking ^ not useful here, but can be used to validate name or number length for acc numbers etc
        return self._name
    
    @name.setter
    def name(self, name):
        self._name = name

    @classmethod
    def from_string(cls, info):
        tokens = info.split(',')
        object = BankAccount(tokens[0], tokens[1])
        return object
new_account = BankAccount.from_string('rob', 500)
print(new_account.name, new_account.amount)


bob = BankAccount('bob', 500)
carol = BankAccount('carol', 10000)

a = ['bob', 500]
b = {'bob': 500}

joint = bob + carol

print(bob)
print(carol)
print(joint)
print(bob.name, bob._name)

class Animal:
    def __init__(self, species, name, age):
        self.species = species
        self.name = name
        self.age = age
    def speak(self):
        return 'growl'
    
class Cat(Animal):
    def __init__(self, species, name, age, whiskers, lives_used):
        super().__init__(species, name, age)
        self.whiskers = whiskers
        self.lives_used = 4
    def speak(self):
        print(super().speak())
        return 'meow meow'
    
class Dog(Animal):
    def __init__(self, species, name, age):
        super().__init__(species, name, age)

    def speak(self):
        return 'Bow wow'
    
luna = Cat('tabby', 'luna', 10, True, 5)
rover = Dog('lab', 'Rover', 4)

animals = [luna, rover]
print(luna.speak())
for a in animals:
    print(a.speak())


class Vehicle:
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return "I'm an electric vehicle"
    def moves(self):
        print("i'm moving")


class Car(Vehicle):
    def __init__(self, name):
        super().__init__(name)
    def moves(self):
        print("drives")

class Boat(Vehicle):
    def __init__(self, name):
        super().__init__(name)
    def moves(self):
        print("sailing")

betsy = Car('betsy')
aurora = Boat('Aurora')

transports = [betsy, aurora]

for t in transports:
    t.moves()