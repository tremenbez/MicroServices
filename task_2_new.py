from math import pi, sqrt
import time
"""
1.	Написать функцию, которая проверяет является ли строка палиндромом.
"""
# Определяем функцию 
def check_palindrom(x:str) -> bool:
    x1 = x.replace(" ", "").lower()
    return x1 == x1[::-1]

# Проверка
ex_1 = "Леша на полке клопа нашел"
check_palindrom(ex_1)

""" 
2. Написать функцию, которая принимает два аргумента: лямбда функция для фильтрации массива, массив строк. Сделать вызов данной функции для следующих функций фильтрации: 
•	Исключить строки с пробелами
•	Исключить строки, начинающиеся с буквы “a”
•	Исключить строки, длина которых меньше 5
"""
def filter_strings(filter_func, strings):
    return list(filter(filter_func, strings))

# Фильтрации
no_spaces = lambda s: " " not in s
no_a_start = lambda s: not s.startswith("a")
length_ge_5 = lambda s: len(s) >= 5

"""
3.	Создать иерархию классов Фигур: квадрат, прямоугольник, треугольник, круг. Каждый класс должен реализовывать следующие методы:
•	вычисление площади
•	вычисление периметра
•	сравнение площади с другой фигурой (больше или меньше)
•	сравнение периметра с другой фигурой (больше или меньше)
"""
class Figure:
    def area(self):
        pass
    
    def perimeter(self):
        pass
    
    def compare_area(self, other):
        return self.area() - other.area()
    
    def compare_perimeter(self, other):
        return self.perimeter() - other.perimeter()

class Square(Figure):
    def __init__(self, side):
        self.side = side
    
    def area(self):
        return self.side ** 2
    
    def perimeter(self):
        return 4 * self.side

class Rectangle(Figure):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def area(self):
        return self.width * self.height
    
    def perimeter(self):
        return 2 * (self.width + self.height)

class Triangle(Figure):
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c
    
    def area(self):
        s = (self.a + self.b + self.c) / 2
        return sqrt(s * (s - self.a) * (s - self.b) * (s - self.c))
    
    def perimeter(self):
        return self.a + self.b + self.c

class Circle(Figure):
    def __init__(self, radius):
        self.radius = radius
    
    def area(self):
        return pi * self.radius ** 2
    
    def perimeter(self):
        return 2 * pi * self.radius

# Примеры сравнения площадей
square = Square(4)
circle = Circle(3)

rectangle = Rectangle(4, 5)
triangle = Triangle(3, 4, 5)

print(f"Площадь квадрата: {square.area()}")
print(f"Площадь круга: {circle.area()}")
print(f"Разница площадей (квадрат - круг): {square.compare_area(circle)}\n")

print(f"Площадь прямоугольника: {rectangle.area()}")
print(f"Площадь треугольника: {triangle.area()}")
print(f"Разница площадей (прямоугольник - треугольник): {rectangle.compare_area(triangle)}")

"""
4.	Создать классы студент, аспирант. Студент содержит свойства: номер группы, средний балл. Аспирант отличается от студента наличием научной работы (название работы в виде строки). Реализовать в классах следующие методы: 
•	вывести информацию о человеке (фио, возраст)
•	вывести размер стипендии. Если средняя оценка равна 5, то стипендия 8000р для аспиранта и 6000р для студента, если меньше 5, то стипендия для аспиранта 6000р, для студента 4000р, в других случаях стипендия 0р
•	Сравнение размера стипендии с другим студентом/аспирантом (больше или меньше)
"""
class Student:
    def __init__(self, name: str, surname: str, middlename: str, age: int, group_id: str, avg_score: float):
        self.name = name
        self.surname = surname
        self.middlename = middlename
        self.age = age
        self.group_id = group_id
        self.avg_score = avg_score

    def fio(self):
        return f"Данный пользователь: {self.surname} {self.name} {self.middlename}. Возраст: {self.age} г."   

    def stipendia(self):
        if self.avg_score == 5:
            return 6000 
        elif 3.5 <= self.avg_score < 5:
            return 4000
        return 0

    def compare_stipend(self, other):
        return self.stipendia() - other.stipendia()

kostya = Student("Константин", "Безверхий", "Андреевич", 22, "5142704/40801", 4.5)
kostya.fio()
kostya.stipendia()

class Aspirant(Student):
    def __init__ (self, name: str, surname: str, middlename: str, age: int, group_id: str, avg_score: float, work:str):
        super().__init__(name, surname, middlename, age, group_id, avg_score)
        self.work = work
        
    def written(self):
        return f"Написал научную статью на тему '{self.work}'"
    
    def stipendia(self):
        if self.avg_score == 5:
            return 8000
        elif 3.5 <= self.avg_score < 5:
            return 6000 
        return 0

denis = Aspirant("Денис", "Лопухин", "Васильевич", 31, "522604/40801", 3.5, 'Молекулярные грибы')
denis.written()
denis.stipendia()
denis.compare_stipend(kostya)

"""
5.	Реализовать декоратор, который выводит в консоль время выполнения декорируемой функции. Протестировать работу декоратора на двух функциях:
•	Функция вычисляет сумму двух чисел a и b, выводит результат в консоль
•	Функция читает из файла input.txt значение двух чисел a и b, записывает результат вычисления в файл output.txt (файлы приложить к репозиторию)
"""

def timing_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time() 
        result = func(*args, **kwargs)
        end_time = time.time()  
        elapsed_time = end_time - start_time
        print(f"Функция {func.__name__} выполнена за {elapsed_time:.5f} секунд")
        return result
    return wrapper

@timing_decorator
def add(a,b):
    return a+b

add(4,3222)

@timing_decorator
def file():
    with open("input.txt", "r") as f:
        a, b = map(int, f.read().split())
    result = a + b
    with open("output.txt", "w") as f:
        f.write(str(result))
    print("Результат записан в output.txt")

file()