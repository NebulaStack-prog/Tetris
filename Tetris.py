# Добавляем нужные библиотеки
import pygame
import random
import copy
import json

pygame.init()

# Создаем переменные количества столбцов и строк
columns = 11  # Количество столбцов игрового поля (ширина)
strings = 21  # Количество строк игрового поля (высота)

# Обозначаем размеры игрового экрана в пикселях
screen_x = 300  # Ширина окна
screen_y = 650  # Высота окна

# Создаем переменные текущего и лучшего счета
score = 0  # Текущие очки
best_score = 0  # Рекорд за все игры

# Создаем размеры кнопок в главном меню
font = pygame.font.Font(None, 32)  # Основной шрифт
menu_font = pygame.font.Font(None, 48)  # Шрифт для заголовка
help_font = pygame.font.Font(None, 24)  # Шрифт для справки

# Создаем игровое окно и называем его "Tetris"
screen = pygame.display.set_mode((screen_x, screen_y))
pygame.display.set_caption("Tetris")
clock = pygame.time.Clock()  # Часы для контроля fps

# Создаем переменную состояния игрового экрана ("menu", "help", "game")
state = "menu"  # Начинаем с главного меню

# Создаем переменную выбора следующей фигуры для функции предпросмотра
next_det_choice = None  # Здесь будет храниться следующая фигура

# Создаем кнопки на главном меню и в окне "Help"
play_button = pygame.Rect(screen_x // 2 - 50, screen_y // 2 - 40, 100, 40)
help_button = pygame.Rect(screen_x // 2 - 50, screen_y // 2 + 10, 100, 40)
back_button = pygame.Rect(screen_x // 2 - 50, screen_y // 2 + 60, 100, 40)

# Задаем размер именно игровой части всего окна (для падения фигур)
game_height = 600

# Задаем размеры клеток игрового поля (игровой части окна)
# cell_x и cell_y - ширина и высота одной клетки в пикселях
cell_x = screen_x / (columns - 1)
cell_y = game_height / (strings - 1)

# Функция для создания панели вне игровой части окна для вывода счетов и предпросмотра
def draw_panel(score, best_score):

    # Создаем саму панель (серый прямоугольник в верхней части экрана)
    pygame.draw.rect(screen, (50, 50, 50), (0, 0, screen_x, 50))
    pygame.draw.rect(screen, (100, 100, 100), (0, 0, screen_x, 50), 2)

    # Создаем на панели текущий счет и красим текст в белый
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 3))

    # Создаем на панели лучший счет и красим текст в желто-золотой цвет
    best_text = font.render(f"Best: {best_score}", True, (255, 215, 0))
    screen.blit(best_text, (10, 25))

    # Создаем на панели надпись для окна предпросмотра и красим ее в белый
    next_text = font.render("Next:", True, (255, 255, 255))
    screen.blit(next_text, (screen_x - 150, 15))

    # Создаем окно для предпросмотра следующей фигуры (рамка)
    preview_rect = pygame.Rect(screen_x - 90, 8, 80, 35)
    pygame.draw.rect(screen, (30, 30, 30), preview_rect)
    pygame.draw.rect(screen, (100, 100, 100), preview_rect, 1)

    # Блок для демонстрации следующей фигуры внутри окна в его центре
    if next_det_choice:

        # Находим минимальные координаты фигуры для правильного позиционирования
        min_x = min(rect.x for rect in next_det_choice)
        min_y = min(rect.y for rect in next_det_choice)

        preview_start_x = screen_x - 70  # Стартовая X позиция для предпросмотра
        preview_start_y = 15  # Стартовая Y позиция для предпросмотра

        # Создаем переменную для размера клетки фигуры внутри окна предпросмотра в пикселях
        size = 11

        for rect in next_det_choice:

            # Вычисляем относительные координаты клетки фигуры
            rel_x = (rect.x - min_x) // cell_x
            rel_y = (rect.y - min_y) // cell_y

            # Создаем прямоугольник для отрисовки клетки в окне предпросмотра
            cell_rect = pygame.Rect(preview_start_x + rel_x * size, preview_start_y + rel_y * size, size - 1, size - 1)

            pygame.draw.rect(screen, next_color, cell_rect)
            pygame.draw.rect(screen, (200, 200, 200), cell_rect, 1)

# Функция для сохранения лучшего счета после окончания игры через создание файла
# Благодаря данной функции лучший счет сохраняется не только после каждой игры но и после каждого запуска кода
def save_best_score(score):
    data = {"best_score": score} # Сохраняем лучший счет в json файл

    # Поверка во избежание ошибок с поиском файла
    try:
        with open("tetris_data.json", "w") as f:
            json.dump(data, f)
    except:
        pass

# Функция для показа лучшего счета в главном меню (его загрузки из сохраненного после игры файла)
# Благодаря данной функции лучший счет загружается не только после каждой игры но и после каждого запуска кода
def load_best_score():

    # Поверка во избежание ошибок с поиском файла
    try:
        with open("tetris_data.json", "r") as f: # Загружаем лучший счет из json файла
            data = json.load(f)
            return data.get("best_score", 0)
    except:
        return 0  # Если файла нет, возвращаем 0


# Функция для создания главного меню
def draw_menu():
    screen.fill(pygame.Color(222, 248, 116, 100))  # Светло-зеленый фон

    # Отрисовка рамки экрана черного цвета
    pygame.draw.rect(screen, (0, 0, 0), (0, 0, screen_x, screen_y), 10)

    # Создание титульного текста (название игры)
    title_text = menu_font.render("TETRIS", True, (0, 0, 0))
    title_rect = title_text.get_rect(center=(screen_x // 2, screen_y // 2 - 100))
    screen.blit(title_text, title_rect)

    # Создание кнопки для начала игры (зеленая кнопка)
    pygame.draw.rect(screen, (100, 150, 50), play_button)
    pygame.draw.rect(screen, (0, 0, 0), play_button, 2)
    play_text = font.render("Play", True, (255, 255, 255))
    play_text_rect = play_text.get_rect(center=play_button.center)
    screen.blit(play_text, play_text_rect)

    # Создание кнопки для ознакомления с правилами игры
    pygame.draw.rect(screen, (100, 150, 50), help_button)
    pygame.draw.rect(screen, (0, 0, 0), help_button, 2)
    help_text = font.render("Help", True, (255, 255, 255))
    help_text_rect = help_text.get_rect(center=help_button.center)
    screen.blit(help_text, help_text_rect)

    # Создание лучшего счета в нижней части главного меню
    best_text = font.render(f"Best: {best_score}", True, (0, 0, 0))
    best_rect = best_text.get_rect(center=(screen_x // 2, screen_y - 50))
    screen.blit(best_text, best_rect)


# Функция для обводки квадратов, из которых состоят тетрамино, белым и черным цветом
def draw_cell(x, y, cell_color):
    rect = pygame.Rect(x, y + 50, cell_x, cell_y)
    pygame.draw.rect(screen, cell_color, rect)
    pygame.draw.rect(screen, (255, 255, 255), rect, 3)
    pygame.draw.rect(screen, (0, 0, 0), rect, 1)


# Функция для отрисовки окна "Help" после перехода в него из главного меню
def draw_help():
    screen.fill(pygame.Color(222, 248, 116, 100))

    # Отрисовка рамки экрана черного цвета
    pygame.draw.rect(screen, (0, 0, 0), (0, 0, screen_x, screen_y), 10)

    # Создание титульного текста
    title_text = menu_font.render("HOW TO PLAY", True, (0, 0, 0))
    title_rect = title_text.get_rect(center=(screen_x // 2, 50))
    screen.blit(title_text, title_rect)

    # Создание краткого текста-подсказки как играть в виде списка
    instructions = [
        "LEFT/RIGHT arrows to move",  # Движение влево/вправо
        "DOWN arrow to speed up",  # Ускорение падения
        "ESC to leave game",  # Выход из игры
        "UP arrow to rotate",  # Поворот фигуры
        "",
        "1. Fill in the lines",  # Заполняй линии
        "2. Get Points",  # Получай очки
        "3. Don't give up"  # Не сдавайся
    ]

    # Вывод всех строк списка на экран
    y_offset = 120  # Начальная вертикальная позиция
    for line in instructions:
        text = help_font.render(line, True, (0, 0, 0))
        text_rect = text.get_rect(center=(screen_x // 2, y_offset))
        screen.blit(text, text_rect)
        y_offset += 25  # Отступ между строками

    # Создание кнопки для возвращения в главное меню
    pygame.draw.rect(screen, (100, 150, 50), back_button)
    pygame.draw.rect(screen, (0, 0, 0), back_button, 2)
    back_text = font.render("Back", True, (255, 255, 255))
    back_text_rect = back_text.get_rect(center=back_button.center)
    screen.blit(back_text, back_text_rect)


# Функция для определения цветов для фигур тетрамино
def get_color(figure_index):
    figure_colors = [
        pygame.Color(255, 0, 0),  # Красный
        pygame.Color(255, 255, 0),  # Желтый
        pygame.Color(255, 128, 0),  # Оранжевый
        pygame.Color(0, 255, 0),  # Зеленый
        pygame.Color(0, 255, 255),  # Голубой
        pygame.Color(255, 0, 255),  # Пурпурный (Фиолетовый)
        pygame.Color(0, 0, 255)  # Синий
    ]
    return figure_colors[figure_index % len(figure_colors)]

# Функция для определения следующей выпадающей фигуры
def get_next_figure():
    figure_index = random.randint(0, len(det) - 1)
    figure = copy.deepcopy(det[figure_index])
    color = get_color(figure_index)
    return figure, color, figure_index


# Функция для перезапуска игры при проигрыше
def reset_game():
    global grid, score, det_choice, color, count, best_score, next_det_choice, next_color, next_figure_index, figure_index, is_landed, can_move

    # Очищаем игровое поле (заполняем серыми клетками)
    for i in range(columns):
        for j in range(strings):
            grid[i][j][0] = 1  # 1 означает "пусто" (можно поставить фигуру)
            grid[i][j][2] = pygame.Color(0, 0, 0)

    score = 0  # Обнуляем счет

    # Создаем текущую и следующую фигуры
    det_choice, color, figure_index = get_next_figure()
    next_det_choice, next_color, next_figure_index = get_next_figure()
    count = 0  # Счетчик для управления скоростью падения
    is_landed = False # Новая фигура не касалась дна или другой фигуры
    can_move = True # Новая фигура может двигаться

# Задаем частоту кадров для скорости падения фигур (60 FPS)
fps = 60

# Создаем двумерный массив (сетку) для хранения состояния игрового поля
# grid[x][y][0] - 1 если пусто, 0 если занято
# grid[x][y][1] - прямоугольник клетки для отрисовки
# grid[x][y][2] - цвет клетки
grid = []

for i in range(columns):
    grid.append([])
    for j in range(strings):
        grid[i].append([1])  # Начинаем с пустых клеток

for i in range(columns):
    for j in range(strings):
        grid[i][j].append(pygame.Rect(i * cell_x, j * cell_y, cell_x, cell_y))
        grid[i][j].append(pygame.Color(0, 0, 0))

# Создаем список фигур, где каждая фигура - набор координат относительно центра (координаты (0, 0))
# Каждая фигура состоит из 4 квадратов (клеток)
details = [
    [[-2, 0], [-1, 0], [0, 0], [1, 0]],  # Горизонтальная линия
    [[-1, 1], [-1, 0], [0, 0], [1, 0]],  # L-образная
    [[1, 1], [-1, 0], [0, 0], [1, 0]],  # J-образная
    [[-1, 1], [0, 1], [0, 0], [-1, 0]], # Квадрат
    [[-1, 0], [0, 0], [0, 1], [1, 1]],  # Z-образная
    [[0, 1], [-1, 0], [0, 0], [1, 0]],  # T-образная
    [[-1, 1], [0, 1], [0, 0], [1, 0]],  # S-образная
]

# Добавляем созданные фигуры, преобразуя координаты в прямоугольники Pygame
det = [[], [], [], [], [], [], []]

for i in range(len(details)):
    for j in range(4):
        det[i].append(
            pygame.Rect(details[i][j][0] * cell_x + cell_x * (columns // 2), details[i][j][1] * cell_y, cell_x, cell_y))

detail = pygame.Rect(0, 0, cell_x, cell_y)
det_choice = copy.deepcopy(random.choice(det))  # Текущая фигура
color = random.choice([pygame.Color(255, 0, 0)])  # Цвет текущей фигуры

next_color = None  # Цвет следующей фигуры
figure_index = 0  # Индекс текущей фигуры
next_figure_index = 0  # Индекс следующей фигуры
count = 0  # Счетчик для управления скоростью падения
landing_time = 0 # Хранит момент времени касания дна поля или фигуры (в миллисекундах)
is_landed = False # Флаг "Коснулась ли фигура дна или другой фигуры?"
can_move = True # Флаг "Можно ли сейчас сдвинуть фигуру?"

# Задаем переменную для начала игры
game = True

# Задаем переменную для поворотов
rotate = False

# Загружаем лучший счет из файла при запуске
best_score = load_best_score()

# Функция для проверки возможности движения для избежания выхода за пределы окна и входа в другие фигуры при поворотах и сдвигах
def CanMove(det_choice, dx, dy):
    for i in range(4):

        # Вычисляем новые координаты клетки
        x = int((det_choice[i].x + dx * cell_x) // cell_x)
        y = int((det_choice[i].y + dy * cell_y) // cell_y)

        # Проверяем выход за границы поля
        if x < 0 or x > columns or y > strings:
            return False

        # Проверяем столкновение с другими фигурами
        if y >= 0 and grid[x][y][0] == 0:
            return False
    return True

# Основной игровой цикл
while game:
    # Проверка соответствия состоянию игры
    if state == "menu":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    mouse_pos = pygame.mouse.get_pos()
                    if play_button.collidepoint(mouse_pos):
                        reset_game()  # Сбрасываем игру
                        state = "game"  # Переключаемся в игровой режим
                    elif help_button.collidepoint(mouse_pos):
                        state = "help"  # Переключаемся в режим справки

        draw_menu()
        pygame.display.flip()
        clock.tick(fps)
        continue

    # Проверка соответствия состоянию игры
    elif state == "help":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    if back_button.collidepoint(mouse_pos):
                        state = "menu"  # Возврат в меню
        draw_help()
        pygame.display.flip()
        clock.tick(fps)
        continue

    # Проверка соответствия состоянию игры
    elif state == "game":
        delta_x = 0  # Смещение по X (влево/вправо)
        delta_y = 1  # Смещение по Y (вниз)

        # Обработка событий клавиатуры
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and can_move:
                    delta_x = -1  # Движение влево
                elif event.key == pygame.K_RIGHT and can_move:
                    delta_x = 1  # Движение вправо
                elif event.key == pygame.K_UP and can_move :
                    rotate = True  # Флаг для поворота
                elif event.key == pygame.K_ESCAPE:
                    state = "menu"  # Выход в меню
                    continue

        key = pygame.key.get_pressed()

        # Увеличение скорости падения фигуры при зажатии клавиши DOWN
        if key[pygame.K_DOWN]:
            count = 31 * fps  # Быстрое падение

        # Отрисовка фона игрового поля (черный цвет)
        screen.fill((0, 0, 0))

        # Отрисовка маленьких квадратиков в клетках
        small_size = cell_x // 3
        offset = (cell_x - small_size) // 2

        # Отрисовка сетки игрового поля
        for i in range(columns):
            for j in range(strings):
                if grid[i][j][0] == 0: # Если клетка занята
                    rect = pygame.Rect(grid[i][j][1].x, grid[i][j][1].y + 50, cell_x, cell_y)
                    pygame.draw.rect(screen, grid[i][j][2], rect)
                    pygame.draw.rect(screen, (255, 255, 255), rect, 3)
                    pygame.draw.rect(screen, (0, 0, 0), rect, 1)
                else:  # Если клетка пустая, рисуем только контур
                    small_rect = pygame.Rect(grid[i][j][1].x + offset, grid[i][j][1].y + offset + 50, small_size, small_size)
                    pygame.draw.rect(screen, (80, 80, 80), small_rect)

        # Проверка столкновений при движении
        for i in range(4):

            # Проверка выхода за левую или правую границу
            if ((det_choice[i].x + delta_x * cell_x < 0) or (det_choice[i].x + delta_x * cell_x >= screen_x)):
                delta_x = 0

            # Проверка достижения дна или столкновения с другой фигурой
            if ((det_choice[i].y + cell_y >= game_height) or (grid[int(det_choice[i].x // cell_x)][int(det_choice[i].y // cell_y) + 1][0] == 0)):
                delta_y = 0

                if not is_landed: # Фигура только что коснулась дна
                    is_landed = True
                    landing_time = pygame.time.get_ticks() # Запоминаем время
                    can_move = True # Разрешаем движение на 200 миллисекунд

                    # При этом сразу фигуру не фиксируем

        # Перемещение фигуры при возможном движении
        if CanMove(det_choice, delta_x, 0):
            for i in range(4):
                det_choice[i].x += delta_x * cell_x

        # Проверяем истекла ли задержка после касания дна поля или фигуры
        if is_landed:
            current_time = pygame.time.get_ticks() # Запоминаем время
            if current_time - landing_time >= 200: # 200 миллисекунд
                # Фиксируем фигуру на поле после истечения времени задержки
                for i in range(4):
                    x = int(det_choice[i].x // cell_x)
                    y = int(det_choice[i].y // cell_y)
                    if 0 <= y < strings:
                        grid[x][y][0] = 0  # Помечаем клетку как занятую
                        grid[x][y][2] = color  # Запоминаем цвет

                # Переключаемся на следующую фигуру
                det_choice = copy.deepcopy(next_det_choice)
                color = next_color
                figure_index = next_figure_index

                # Сбрасываем флаги
                is_landed = False
                can_move = True

                # Генерируем новую следующую фигуру
                next_det_choice, next_color, next_figure_index = get_next_figure()

                # Проверяем, не закончилась ли игра (столкновение новой фигуры с занятыми клетками)
                top = False
                for i in range(4):
                    x = int(det_choice[i].x // cell_x)
                    y = int(det_choice[i].y // cell_y)
                    if 0 <= x and 0 <= y < strings and grid[x][y][0] == 0:
                        top = True
                        break
                    if y < 0:
                        top = True
                        break

                if top:
                    state = "menu"  # Игра окончена, возврат в меню
                    continue

        # Управление падением
        count += fps

        if count > 30 * fps:  # Падение каждые 30 кадров (0.5 секунды при 60 FPS)
            if CanMove(det_choice, 0, 1):
                for i in range(4):
                    det_choice[i].y += delta_y * cell_y
            else:
                delta_y = 0
            count = 0

        # Отрисовка текущей фигуры
        for i in range(4):
            draw_cell(det_choice[i].x, det_choice[i].y, color)

        # Поворот фигуры
        C = det_choice[2]  # Центральная клетка фигуры (опорная точка/центр вращения)
        if rotate and can_move:
            temp = copy.deepcopy(det_choice)

            # Математика поворота на 90 градусов по часовой стрелке
            for i in range(4):
                x = temp[i].y - C.y
                y = temp[i].x - C.x
                temp[i].x = C.x - x
                temp[i].y = C.y + y

            # Проверяем различные варианты смещения при повороте
            shifts = [0, -1, 1, -2, 2]
            rotated = False

            for shift in shifts:
                if CanMove(temp, shift, 0):
                    for i in range(4):
                        temp[i].x += shift * cell_x
                    det_choice = temp
                    rotated = True
                    break

            rotate = False  # Сбрасываем флаг поворота

        # Проверка и удаление заполненных линий
        for j in range(strings - 1, -1, -1):
            count_cells = 0  # Счетчик занятых клеток в строке
            for i in range(columns):
                if grid[i][j][0] == 0:  # Если клетка занята
                    count_cells += 1
                elif grid[i][j][0] == 1:
                    break

            # Если строка заполнена
            if count_cells == (columns - 1):
                score += 10  # Добавляем очки
                if score > best_score:
                    best_score = score
                    save_best_score(score) # Сразу сохраняем рекорд

                # Сдвигаем все строки вниз
                for l in range(columns):
                    grid[l][0][0] = 1
                for k in range(j, 0, -1):
                    for l in range(columns):
                        grid[l][k][0] = grid[l][k - 1][0]
                        grid[l][k][2] = grid[l][k - 1][2]

        # Вызываем функцию для создания панели (счет, рекорд, предпросмотр)
        draw_panel(score, best_score)

    # Обновляем экран и ждем следующий кадр
    pygame.display.flip()
    clock.tick(fps)
