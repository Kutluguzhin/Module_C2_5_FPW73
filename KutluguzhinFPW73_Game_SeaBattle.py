from random import randint # импорт функции для случайного генерирования точек

# Класс Точки
class Dot:
    def __init__(self, x, y): # конструктор для присваивания координат точке
        self.x = x
        self.y = y

    def __eq__(self, other): # сравнение точек друг с другом во избежание повторений, например, при выстреле
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})" # возвращает код, который вводили при создании точки, удобен для создания списка
                                       # неоходим для проверки есть ли точка в списке

# Классы для выбрасывания исключений в процессе игры
class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"

class BoardWrongShipException(BoardException):
    pass

# Класс Корабли
class Ship:
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o # задает ориентацию корабля
        self.lives = l # количество жизней корабля, т.е. его точек (длина)

    @property
    def dots(self):
        ship_dots = [] # список со всеми точками корабля
        for i in range(self.l): # проходимся циклом от 0 до значения длины корабля
            cur_x = self.bow.x # координаты "носа" корабля
            cur_y = self.bow.y

            if self.o == 0: # горизонтальная ориентация корабля
                cur_x += i # проходимся по всей длине от "носа" корабля

            elif self.o == 1: # вертикальная ориентация корабля
                cur_y += i # проходимся по всей длине от "носа" корабля

            ship_dots.append(Dot(cur_x, cur_y)) # создаем список точек корабля

        return ship_dots # возвращаем этот список точек корабля

    # метод проверки выстрела на попадание
    def shooten(self, shot):
        return shot in self.dots

# Класс Доски
class Board:
    def __init__(self, hid=False, size=6):
        self.size = size # размер доски
        self.hid = hid # скрывать или не скрывать доску

        self.count = 0 # количество пораженных кораблей

        self.field = [["O"] * size for _ in range(size)] # сетка доски

        self.busy = [] # список занятых точек
        self.ships = [] # список кораблей на доске

    def add_ship(self, ship): # добавление корабля

        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False): # контуры корабля
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ] # список точек вокруг той, в которой мы находимся
        for d in ship.dots: # берем каждую точку корабля и проходимся по контуру
            for dx, dy in near: # так мы пройдем все точки, которые соседствуют с кораблем
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy: # если точки нет в списке занятых
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur) # записываем точку в список занятых

    def __str__(self): # вывод корабля на доску
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid: # параметр скрытия корабля
            res = res.replace("■", "O") # замена в случае необходимости точек на пустые символы
        return res

    def out(self, d): # проверка - находится ли точка за пределами доски
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d): # метод выстрела
        if self.out(d): # проверка точки - выходит ли он за границы
            raise BoardOutException() # если выходит, то выбрасывается исключение

        if d in self.busy: # проверка занята ли точка
            raise BoardUsedException() # если точка занята, то выбрасывается исключение

        self.busy.append(d) # добавляем точку, если она не была занята в список занятых точек

        for ship in self.ships: # проходимся в списке циклом по кораблям и проверяем
            if d in ship.dots: # принадлежит ли точка к кораблю или нет
                ship.lives -= 1 # уменьшаем количество жизней корабля если попали
                self.field[d.x][d.y] = "X" # ставим в подстреленную точку Х
                if ship.lives == 0: # если у корабля кончились жизни
                    self.count += 1 # прибавляем к счетчику уничтоженных кораблей единицу
                    self.contour(ship, verb=True) # проверка контура корабля, т.к. в точки рядом с кораблем мы не можем стрелять
                    print("Корабль уничтожен!") # выводим сообщение, что корабль уничтожен
                    return False # возвращаем False, чтобы дальше не делать ход
                else: # если кол-во жизней не нулевое
                    print("Корабль ранен!") # то корабль просто ранен - выводим сообщение
                    return True # возвращаем True, чтобы повторить ход

        self.field[d.x][d.y] = "." # ставим точку, если ни один корабль не был поражен
        print("Мимо!") # печатаем, что выстрел сделан мимо
        return False

    def begin(self):
        self.busy = [] # важно, чтобы перед игрой список занятых точек обнулился

# Класс Игрока
class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self): # этот метод не определяем, но он должен быть
        raise NotImplementedError() # так как будет у потомков этого класса (здесь работает наследие)

    def move(self): # метод в бесконечном цикле, где мы пытаемся сделать выстрел
        while True: # бесконечный цикл
            try:
                target = self.ask() # просим предоставить игрока координаты выстрела
                repeat = self.enemy.shot(target) # если выстрел прошел успешно
                return repeat # возвращаем - нужно ли нам повторить ход
            except BoardException as e: # если выстрел прошел не успешно
                print(e) # выбрасываем ошибку и цикл продолжается

# Класс Игрока - Компьютера
class AI(Player): # в скобках указываем родительский класс
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5)) # случайно генерируем две точки от 0 до 5
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}") # показываем в консоли ход компьютера
        return d # возвращаем точку

# Класс Игрока - Пользователя
class User(Player): # в скобках указываем родительский класс
    def ask(self): # запрашиваем точку выстрела
        while True:
            cords = input("Ваш ход: ").split() # просим ввести координаты выстрела через пробел

            if len(cords) != 2: # проверка, что именно две координаты введены
                print(" Введите 2 координаты! ") # вывод сообщения о вводе ровно 2 координат, если ввод некорректен
                continue # продолжаем цикл

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()): # проверка введенных данных, что это числа
                print(" Введите числа! ") # просьба ввести числа, если это не так
                continue # продолжаем ицкл

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1) # возвращаем точку, убирая единичку, т.к. у нас в списке индексация с 0

# Класс Игры
class Game:
    def __init__(self, size=6): # конструктор игры
        self.size = size # задаем размер доски
        pl = self.random_board() # генерируем доску для пользователя
        co = self.random_board() # генерируем доску для компьютера
        co.hid = True # скрываем корабли компьютера

        # создаем наших игроков - Пользователя и Компьютер
        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self): # метод случайного создания доски
        board = None # пустая доска
        while board is None:
            board = self.random_place() # создаем доску
        return board # возвращаем результат

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1] # список длин кораблей
        board = Board(size=self.size) # создаем доску
        attempts = 0
        for l in lens: # для каждой длины корабля
            while True: # будем в бесконечном цикле ставить этот корабль
                attempts += 1 # счетчик попыток ввода
                if attempts > 2000:
                    return None # если количество попыток больше 2000, то вернем пустую доску
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1)) # параметры корабля
                try:
                    board.add_ship(ship) # проверка добавлений корабля
                    break # если все хорошо, то break и цикл закончится
                except BoardWrongShipException:
                    pass # если выбросится исключение, то цикл продолжится и начинаем итерацию заново
        board.begin()
        return board # возвращаем доску, чтобы подготовить ее к игре

    def greet(self): # приветствие пользователя, вывод сообщений
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def loop(self):
        num = 0 # номер хода
        while True: # создание бесконечного игрового цикла
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0: # если номер хода четный - ходит пользователь
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.us.move() # вызываем метод, отвечающий за ход игрока
            else: # если номер хода нечетный - ходит компьютер
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move() # вызываем метод, отвечающий за ход игрока
            if repeat:
                num -= 1 # уменьшаем на единицу если есть необходимость в дополнительном ходе у того же игрока

            if self.ai.board.count == 7: # если количество пораженных кораблей 7, то игрок выиграл
                print("-" * 20)
                print("Пользователь выиграл!")
                break # останавливаем цикл

            if self.us.board.count == 7: # если количество пораженных кораблей 7, то компьютер выиграл
                print("-" * 20)
                print("Компьютер выиграл!")
                break # останавливаем цикл
            num += 1 # добавляем к ходу единичку и продолжаем цикл, если нет победителя

    # метод старт, которые совмещает методы приветствия и игрового цикла
    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start() # вызов метода Старт