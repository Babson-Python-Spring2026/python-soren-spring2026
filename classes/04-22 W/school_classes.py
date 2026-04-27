import json

class Student:
    def __init__(self, name, student_id):
        self.name = name
        self.student_id = student_id

class School:
    def __init__(self, name):
        self.name = name
        self.students = []
    def add_student(self, student):
        in self.students
        self.students.append(student)

class Schools:
    def __init__(self):
        self.schools = []

    def add_school(self, school):
        self.schools.append(school)

mySchools = Schools()
babson = School('Babson')
mit = School('MIT')

mySchools.add_school(babson)
mySchools.add_school(mit)

eve = Student('Eve', 1)

babson.add_student(eve)

for school in mySchools.schools:
    print(school.name)

    for student in school.students:
        print(student.name, student.student_id)
