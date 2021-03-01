import pygame  # импортируем pygame
from random import choice  # импортируеи random.choice для случайного выбора цвета, формы и т.д.
from copy import deepcopy  # импортируем deepcopy для копирования вложенных массивов,
# описывающих тетрамино
import os  # нужно для поиска изображений в операционной системе
import sys

# словарь с различными формами тетрамино, представленных в виде координат соответствующих клеток
FIGURES = {'I': ([0, 0], [0, 1], [0, 2], [0, 3]),
           'L': ([0, 0], [0, 1], [0, 2], [1, 2]),
           'J': ([1, 0], [1, 1], [1, 2], [0, 2]),
           'O': ([0, 0], [0, 1], [1, 0], [1, 1]),
           'S': ([2, 0], [1, 0], [1, 1], [0, 1]),
           'Z': ([0, 0], [1, 0], [1, 1], [2, 1]),
           'T': ([0, 0], [1, 0], [2, 0], [1, 1]),
           }

# словарь, хранящий форму повернутых тетрамино
ROTATION = {'I': [((2, 1), (1, 0), (0, -1), (-1, -2)),
                  ((-1, 2), (0, 1), (1, 0), (2, -1)),
                  ((-2, -1), (-1, 0), (0, 1), (1, 2)),
                  ((1, -2), (0, -1), (-1, 0), (-2, 1))],
            'L': [((-1, 1), (0, 0), (1, -1), (0, -2)),
                  ((1, 1), (0, 0), (-1, -1), (-2, 0)),
                  ((1, -1), (0, 0), (-1, 1), (0, 2)),
                  ((-1, -1), (0, 0), (1, 1), (2, 0))],
            'J': [((-1, 1), (0, 0), (1, -1), (2, 0)),
                  ((1, 1), (0, 0), (-1, -1), (0, -2)),
                  ((1, -1), (0, 0), (-1, 1), (-2, 0)),
                  ((-1, -1), (0, 0), (1, 1), (0, 2))],
            'S': [((-2, 0), (-1, 1), (0, 0), (1, 1)),
                  ((0, 2), (1, 1), (0, 0), (1, -1)),
                  ((2, 0), (1, -1), (0, 0), (-1, -1)),
                  ((0, -2), (-1, -1), (0, 0), (-1, 1))],
            'Z': [((0, 2), (-1, 1), (0, 0), (-1, -1)),
                  ((2, 0), (1, 1), (0, 0), (-1, 1)),
                  ((0, -2), (1, -1), (0, 0), (1, 1)),
                  ((-2, 0), (-1, -1), (0, 0), (1, -1))],
            'T': [((1, 1), (0, 0), (-1, -1), (1, -1)),
                  ((1, -1), (0, 0), (-1, 1), (-1, -1)),
                  ((-1, -1), (0, 0), (1, 1), (-1, 1)),
                  ((-1, 1), (0, 0), (1, -1), (1, 1))]
            }

# словарь с цветами в формате rgb для единства цветовой гаммы
COLORS = {-1: (0, 0, 0),
          1: (0, 0, 255),
          2: (0, 255, 255),
          3: (255, 255, 0),
          4: (255, 0, 255),
          5: (255, 0, 0),
          6: (0, 255, 0),
          7: (50, 50, 50)}

# список с различными формами тетрамино, необходим для случайного выбора фигуры
FIGURES_TYPES = list(FIGURES.keys())
# кортеж с различными видами поворота фигуры (0 - 0 градусов от исходной,
# 1 - 90 градусов и т.д.
ROTATION_TYPES = (0, 1, 2, 3)
# таблица, в которой ключи - количество убранных за один раз слоёв, значения - начисленные очки
SCORE_TABLE = {0: 0,
               1: 100,
               2: 300,
               3: 800,
               4: 1500}
WIDTH, HEIGHT = 520, 620  # размеры экрана
GRAVITY = 0.25  # гравитация нужна для реалистичного падения частиц
pygame.init()  # инициализация pygame
pygame.display.set_caption('Tetris')  # установка заголовка окна
size = WIDTH, HEIGHT
fps = 15  # установка частоты кадров
clock = pygame.time.Clock()  # игровые часы
screen = pygame.display.set_mode(size)  # оснновной экран
is_pause = False  # состояние игры: пауза/нет паузы


# функция для загрузки изображения
def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)  # image полуаем полный путь к файлу
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    # работа с фоном
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


# начальный экран
def start_screen():
    intro_text = ["Чтобы играть щекните", "любой кнопкой мыши"]  # текст на стартовом экране
    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))  # фоновое изображение
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)  # шрифт
    text_coord = 50  # координаы текста
    for line in intro_text:  # построчное размещеие текста
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру при щелчке мышью
        pygame.display.flip()
        clock.tick(fps)


# функция выхода
def terminate():
    pygame.quit()
    sys.exit()


# спрайт кнопки паузы
class Pause(pygame.sprite.Sprite):
    def __init__(self, x1, y1, text):
        # НЕОБХОДИМО вызвать конструктор родительского класса Sprite.
        # Это очень важно!!!
        super().__init__(all_sprites)
        # размещение надписи на кнопке и само кнопки на экране
        color = (255, 255, 255)
        font = pygame.font.Font(None, 50)
        text = font.render(text, True, color)
        size = text.get_width(), text.get_height()
        self.image = pygame.Surface(size)
        self.image.fill((50, 140, 90))
        self.rect = pygame.Rect(x1, y1, *size)
        self.image.blit(text, (0, 0))

    def update(self, *args):
        global is_pause  # используем глобальную переменную
        # ставим на паузу или снимаем с нее при щелчке по кнопке
        if args and args[0].type == pygame.MOUSEBUTTONDOWN and \
                self.rect.collidepoint(args[0].pos):
            is_pause = not is_pause


class Board:
    # создание поля
    def __init__(self, width, height):
        # размеры поля
        self.width = width
        self.height = height
        # значения по умолчанию
        self.board = [[-1] * width for _ in range(height)]
        # координаты верхнего левого угла
        self.left = 10
        self.top = 10
        self.cell_size = 30  # размер одной клетки

    # настройка внешнего вида
    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    # отрисовка доски
    def render(self, screen):
        for i in range(self.height):
            for j in range(self.width):
                if self.board[i][j] == -1:
                    color = (0, 0, 0)
                else:
                    color = (0, 255, 0)
                pygame.draw.rect(screen, color, ((self.left + j * self.cell_size,
                                                  self.top + i * self.cell_size),
                                                 (self.cell_size, self.cell_size)))
                pygame.draw.rect(screen, (255, 255, 255), ((self.left + j * self.cell_size,
                                                            self.top + i * self.cell_size),
                                                           (self.cell_size, self.cell_size)), 1)


# наследованный от Board класс самого поля для игры - Tetris
class Tetris(Board):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game_over = False  # окончена ли игра
        self.figure_type = choice(FIGURES_TYPES)  # тип первой фигуры
        self.figure = deepcopy(FIGURES[self.figure_type])  # координаты первой фигуры
        self.move_figure(int(self.width // 2) - 2, 0)  # перемещение фигуры в центр экрана
        self.next_figure_type = choice(FIGURES_TYPES)  # тип следующей фигуры
        self.next_figure = deepcopy(FIGURES[self.next_figure_type])  # координаты следующей фигуры
        self.figure_rotation = 0  # вид поворота
        self.frame = 0  # значение кадра, используется каждый self.speed кадр,
        # чтобы регулировать скорость
        self.color = choice([1, 2, 3, 4, 5, 6])  # выбор цвета первой фигуры
        self.next_color = choice([1, 2, 3, 4, 5, 6])  # выбор цвета следующей фигуры
        self.score = 0  # начальный счёт
        self.speed = 5  # начальная скорость
        self.shadow_mode = False  # тень ли фигурка(см. ниже)
        preview_display.change_figure(self.next_figure, self.next_color)  # отображение
        # следующей фигурки на втором дисплее

    # функция, генерирующая фигуру
    def generate_figure(self):
        # генерируем новую фигиру, меняем self.figure на self.next_figure
        self.figure_type, self.next_figure_type = self.next_figure_type, choice(FIGURES_TYPES)
        self.figure, self.next_figure = self.next_figure, deepcopy(FIGURES[self.next_figure_type])
        self.figure_rotation = 0  # сбрасываем тип поворота
        self.move_figure(int(self.width // 2) - 2, 0)  # перемещение фигуры в центр экрана
        # смена цвета и выбор цвета следующей фигуры
        self.color, self.next_color = self.next_color, choice([1, 2, 3, 4, 5, 6])
        # отображаем следующую фигуру на специальном экране
        preview_display.change_figure(self.next_figure, self.next_color)

    # проверка возможности смещения фигуры
    def check_move(self, x, y):
        # в цикле проходимся по клеткам фигуры,
        # проверяя пересечение с другими непустыми клетками и выходом за границы поля
        for cell in self.figure:
            x1, y1 = cell[0] + x, cell[1] + y
            if x1 >= self.width or y1 >= self.height or y1 < 0 or x1 < 0:
                return False
            if self.board[y1][x1] != -1 and [x1, y1] not in self.figure:
                return False
        return True

    # поворот фигуры
    def rotate_figure(self):
        # если поворот возможен, то согласно ROTATION тетрамино поворачивается
        if self.check_rotate():
            if self.figure_type != 'O':
                rotate = ROTATION[self.figure_type][self.figure_rotation]
                for i in range(4):
                    self.figure[i][0] += rotate[i][0]
                    self.figure[i][1] += rotate[i][1]
                self.figure_rotation += 1
                self.figure_rotation %= 4

    #  проверка на возможность поворота аналогична проверке на смещение
    def check_rotate(self):
        if self.figure_type != 'O':
            rotate = ROTATION[self.figure_type][self.figure_rotation]
            for i in range(4):
                x1 = self.figure[i][0] + rotate[i][0]
                y1 = self.figure[i][1] + rotate[i][1]
                if x1 < 0 or x1 >= self.width or y1 < 0 or y1 >= self.height:
                    return False
                if self.board[y1][x1] != -1 and [x1, y1] not in self.figure:
                    return False
            return True

    # проверка на пересечение фигуры с границами, нужна для корректной работы смещения фигуры
    # без этой проверки тетрамино будет останавливаться при соприкосновении с боковой границей
    def check_borders(self, x, y):
        for cell in self.figure:
            x1, y1 = cell[0] + x, cell[1] + y
            if x1 >= self.width or x1 < 0:
                return True
        return False

    # смещение фигуры
    def move_figure(self, x, y):
        self.check_lose()  # проверка "идёт ли игра?"
        if self.game_over:  # если игра закончилась, не двигать тетрамино
            pass
        elif self.check_move(x, y):  # если смещение возможно, сделать
            for cell in self.figure:
                cell[0] += x
                cell[1] += y
        else:
            if min(self.figure, key=lambda x: x[1])[1] == 0:
                # если фигура касается верхней грани
                # и не может двигаться, игру нужно завершить
                for cell in self.figure:
                    cell[0] += x
                    cell[1] += y
                self.check_lose()
            elif self.check_move(0, 1):
                # необходимо для того, чтобы фигура не останавливалась при боковом касании
                pass
            elif not self.check_borders(x, y) and not self.shadow_mode:
                # если фигура не является "тенью", то она останавливается и запускается новая
                self.new_figure()

    # реакция фигуры на различные нажатия клавиш
    def update(self, event):
        if event.key == pygame.K_LEFT:  # смещение влево
            self.move_figure(-1, 0)
        elif event.key == pygame.K_RIGHT:  # смещение вправо
            self.move_figure(1, 0)
        elif event.key == pygame.K_DOWN:  # смещение вниз
            self.move_figure(0, 1)
        elif event.key == pygame.K_UP:  # поворот
            self.rotate_figure()

    # создание "тени" фигуры
    def make_shadow(self):
        self.shadow_figure = deepcopy(self.figure)  # "тень" исходные запоминает координаты фигуры
        self.shadow_mode = True  # включается "теневой" режим
        while self.check_move(0, 1):  # в цикле смещаем фигуру вниз до тех пор, пока можем
            self.move_down()
        # возвращаем фигуре исходные координаты, тень же ставим на её место
        self.shadow_figure, self.figure = self.figure, self.shadow_figure
        self.shadow_mode = False  # выключаем теневой режим

    # создаём новую фигуру
    def new_figure(self):
        # фиксация клеток текущей фигуры
        for cell in self.figure:
            self.board[cell[1]][cell[0]] = self.color
        self.generate_figure()  # генерация новой

    # смещение фигуры на 1 клетку вниз - "падение"
    def move_down(self):
        # если можем сдвинуть, сдвигаем, иначе создаём новую фигуру
        if self.check_move(0, 1):
            self.move_figure(0, 1)
        else:
            self.new_figure()

    # проверка линии на заполненость
    def check_full_line(self, y):
        is_full = True  # считаем, что линия заполнена, пока не доказано обратное
        for i in range(self.width):
            if self.board[y][i] == -1:
                is_full = False
                break
        return is_full

    # проверка линии на пустоту аналогично
    def check_blank_line(self, y):
        is_blank = True
        for i in range(self.width):
            if self.board[y][i] != -1:
                is_blank = False
                break
        return is_blank

    # удаление полных линий и смещение верхних линий вниз с начислением очков
    def remove_blank(self):
        global record
        blank_lines = 0
        # проходимя в цикле по линиям, проверяя их на заполненность
        for y in range(self.height):
            if self.check_full_line(y):
                # если линия заполнена, проигрываем звук стирания линии,
                # смещаем верхние линии на  клетку в из
                sound1.play()
                blank_lines += 1
                for i in range(self.width):
                    self.board[y][i] = -1
        # начисляем очки согласно таблице, умножая их на коэффициент сложности, равный 6 - скорость
        self.score += SCORE_TABLE[blank_lines] * (6 - self.speed)
        # определяем значение скоррости в зависимости от количества очков
        if self.score < 500:
            self.speed = 5
        elif 500 <= self.score <= 1500:
            self.speed = 4
        elif 1500 < self.score <= 3000:
            self.speed = 3
        elif 3000 < self.score <= 10000:
            self.speed = 2
        else:
            self.speed = 1
        # обновление рекорда с появлением звездочек и проигрыванием соответствующего звука
        if self.score > record:
            record = self.score
            create_particles((self.left + self.cell_size * self.width + 40,
                              preview_display.top +
                              preview_display.cell_size * preview_display.height + 110))
            sound3.play()
        # опускание оставшихся линий на место пустых
        for y in range(self.height - 1, 0, -1):
            if self.check_blank_line(y):
                self.lower_line(y)

    # проверка поражения, если игра окончена проигрывается соответствующий звук,
    # а музыка ставится на паузу
    def check_lose(self):
        if not self.check_blank_line(0):
            self.game_over = True
            pygame.mixer.music.pause()
            sound2.play()
            preview_display.end_game()

    # опускание линии
    def lower_line(self, y):
        for i in range(self.width):
            self.board[y][i] = self.board[y - 1][i]
            self.board[y - 1][i] = -1

    # окончание игры - зеленый экран с белой надписью "Game Over" и количеством очков
    def end_game(self):
        color = (255, 255, 255)
        font = pygame.font.Font(None, self.cell_size * 3)
        text = font.render("GAME OVER!", True, color)
        text_x = WIDTH // 2 - text.get_width() // 2
        text_y = HEIGHT // 2 - text.get_height() // 2
        screen.blit(text, (text_x, text_y))
        new_font = pygame.font.Font(None, self.cell_size)
        new_text = new_font.render("Вы набрали: " + str(self.score) + ' очков', True, color)
        new_text_x = WIDTH // 2 - new_text.get_width() // 2
        new_text_y = HEIGHT // 2 - new_text.get_height() // 2 + 100
        screen.blit(new_text, (new_text_x, new_text_y))

    # отображение игры
    def render(self, screen):
        if self.game_over:  # если игра окончена, вызвать соответствующую функцию
            self.end_game()
        else:
            self.check_lose()  # проверка поражения
            self.make_shadow()  # создание тени
            if not self.game_over:
                # вывести количество очков и рекорд
                color = (255, 255, 255)
                font = pygame.font.Font(None, self.cell_size * 3)
                text = font.render(str(self.score), True, color)
                text_x = self.left + self.cell_size * self.width + 10
                text_y = preview_display.top + \
                         preview_display.cell_size * preview_display.height + 10
                screen.blit(text, (text_x, text_y))
                new_font = pygame.font.Font(None, self.cell_size)
                new_text = new_font.render("Рекорд: " + str(record), True, color)
                new_text_x = text_x
                new_text_y = text_y + 100
                screen.blit(new_text, (new_text_x, new_text_y))
                # поклеточно вывести каждую клетку таблицы
                for i in range(self.height):
                    for j in range(self.width):
                        if [j, i] in self.figure:  # клетки текущей фигуры не хранятся в таблице
                            color = COLORS[self.color]
                        elif [j, i] in self.shadow_figure:  # клеток "тени" там тоже нет
                            color = COLORS[7]
                        else:
                            color = COLORS[self.board[i][j]]
                        # отрисовка клетки
                        pygame.draw.rect(screen, color, ((self.left + j * self.cell_size,
                                                          self.top + i * self.cell_size),
                                                         (self.cell_size, self.cell_size)))
                        pygame.draw.rect(screen, (255, 255, 255), ((self.left + j * self.cell_size,
                                                                    self.top + i * self.cell_size),
                                                                   (self.cell_size, self.cell_size)),
                                         1)
                # смена кадра происходит по модулю скорости,
                # поэтому зациклена с периодом равным значению скорости
                self.frame = (self.frame + 1) % self.speed
                if self.frame == 0:  # если кадр равен 0, двигаем фигуру вниз
                    self.move_down()
                self.remove_blank()  # удаляем пустые линии


# класс дисплея, показывающего следующую фигуру
class Preview_display(Board):
    def __init__(self, *args, **kwargs):
        self.game_over = False
        super().__init__(*args, **kwargs)

    # завершение игры
    def end_game(self):
        self.game_over = True

    def change_figure(self, figure, color):  # смена фигуры
        self.board = [[-1] * self.width for _ in range(self.height)]
        for cell in figure:
            self.board[cell[1]][cell[0]] = color

    # отрисовка фигуры
    def render(self, screen):
        if self.game_over:
            pass
        else:
            for i in range(self.height):
                for j in range(self.width):
                    color = COLORS[self.board[i][j]]
                    pygame.draw.rect(screen, color, ((self.left + j * self.cell_size,
                                                      self.top + i * self.cell_size),
                                                     (self.cell_size, self.cell_size)))
                    pygame.draw.rect(screen, (255, 255, 255), ((self.left + j * self.cell_size,
                                                                self.top + i * self.cell_size),
                                                               (self.cell_size, self.cell_size)), 1)


screen_rect = (0, 0, WIDTH, HEIGHT)  # параметры экрана


# класс частиц - звездочек
class Particle(pygame.sprite.Sprite):
    # сгенерируем частицы разного размера
    fire = [load_image("star.png")]
    for scale in (5, 10, 20):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(all_sprites)
        self.image = choice(self.fire)
        self.rect = self.image.get_rect()

        # у каждой частицы своя скорость — это вектор
        self.velocity = [dx, dy]
        # и свои координаты
        self.rect.x, self.rect.y = pos

        # гравитация будет одинаковой (значение константы)
        self.gravity = GRAVITY

    def update(self):
        # применяем гравитационный эффект:
        # движение с ускорением под действием гравитации
        self.velocity[1] += self.gravity
        # перемещаем частицу
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        # убиваем, если частица ушла за экран
        if not self.rect.colliderect(screen_rect):
            self.kill()


def create_particles(position):
    # количество создаваемых частиц
    particle_count = 100
    # возможные скорости
    numbers = range(-10, 11)
    for _ in range(particle_count):
        dx, dy = choice(numbers), choice(numbers)
        while max(abs(dx), abs(dy)) <= 7:
            dx, dy = choice(numbers), choice(numbers)
        Particle(position, dx, dy)


if __name__ == '__main__':
    record = 0  # рекорд изначально равен 0
    # загрузка звуков и саундтрекка
    pygame.mixer.music.load('data/tetris.mp3')
    pygame.mixer.music.play(-1)  # зациклить проигрывание фоновой музыки
    start_screen()  # начальный экран
    screen.fill('black')
    sound1 = pygame.mixer.Sound('data/full_line.mp3')
    sound2 = pygame.mixer.Sound('data/game_over.mp3')
    sound3 = pygame.mixer.Sound('data/new_record.mp3')
    running = True
    preview_display = Preview_display(4, 4)  # создание экрана предпросмотра следующей фигуры
    preview_display.set_view(330, 10, 30)
    board = Tetris(10, 20)  # создание основной доски игры
    board.set_view(10, 10, 30)
    all_sprites = pygame.sprite.Group()  # создание группы спрайтов
    menu = Pause(330, 400, 'Пауза')
    # игровой цикл
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if not is_pause:  # если игра не на паузе,
                # обновлять данные и реагировать на нажатие стрелок
                if event.type == pygame.KEYDOWN:
                    board.update(event)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if board.game_over:  # если игра закончена, перезапустить все объекты
                        menu = Pause(330, 400, 'Пауза')
                        pygame.mixer.music.unpause()
                        preview_display = Preview_display(4, 4)
                        preview_display.set_view(330, 10, 30)
                        board = Tetris(10, 20)
                        board.set_view(10, 10, 30)
                    menu.update(event)
            else:  # если игра на паузе,
                # реагировать только на закрытие окна или нажатие на кнопку паузы
                if event.type == pygame.MOUSEBUTTONDOWN:
                    menu.update(event)
        if not is_pause:
            # если не на паузе, обновлять игру
            if board.game_over:
                all_sprites = pygame.sprite.Group()
            all_sprites.update()
            screen.fill((51, 202, 102))
            preview_display.render(screen)
            board.render(screen)
            all_sprites.draw(screen)
            pygame.display.flip()
            clock.tick(fps)
    pygame.quit()
