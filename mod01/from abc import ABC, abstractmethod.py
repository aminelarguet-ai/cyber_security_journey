class Person:
    nimber_of_people = 0

    def __init__(self, name):
        self.name = name 
        Person.nimber_of_people +=1

p1 = Person("tim")
p2 =Person("jill")
print (Person.nimber_of_people)