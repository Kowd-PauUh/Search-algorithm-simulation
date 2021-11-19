"""
Created by Ivan Danylenko
Date 09.11.21
"""

from copy import deepcopy
from PIL import Image
from random import randint
from math import sqrt


class CubicMetre:
    """ Класс "кубический метр". Экземплярами данного класса наполняется водоем - экземпляр класа Pool().

    По назначению такие наполнители условно делятся на три типа: водный куб, ландшафтный куб, источник звука.
    Кубометр воды может иметь явно определенный параметр sound_intensity.
    Кубометр ландшафта не может иметь явно определенного параметра sound_intensity а также выступает как барьер.
    Источник звука в свою очередь является производной кубометра ландшафта, поскольку является барьером,
    но при этом имеет явно определенный параметр sound_intensity.

    Attributes:
        x_position (int): координата кубометра по оси X
        y_position (int): координата кубометра по оси Y
        z_position (int): координата кубометра по оси Z
        is_water (bool): True if a cube is composed of water, False otherwise
        sound_intensity (None|float|int): интенсивность звука в данном кубометре
        neighbours (list): список соседствующих кубов; состоит из None полностью, если соседей нет, и частично, если есть не все

    """

    def __init__(self, x_position, y_position, z_position, is_water):
        """ Инициализация кубометра

        Args:
            x_position (int): задаваемая координата кубометра по оси X
            y_position (int): задаваемая координата кубометра по оси Y
            z_position (int): задаваемая координата кубометра по оси Z
            is_water (bool): True if a cube is composed of water, False otherwise

        """

        self.x_position = x_position
        self.y_position = y_position
        self.z_position = z_position
        self.is_water = is_water

        self.sound_intensity = None
        self.neighbours = deepcopy([None] * 26)


class Pool:
    """ Класс "водоем". В экземпляре такого класса проводится симуляция водной среды и работы подводного аппарата.

    Состоит из экземпляров класса CubicMetre() и содержит в себе экземпляры классов CubicMetre() и Submarine().
    Почти полностью зависит от загруженной карты высот.

    Args:
        heightmap (str): путь к карте высот (расположение файла)

    Attributes:
        length (int): длина водоема (значение по X)
        width (int): ширина водоема (значение по Y)
        height (int): высота водоема (значение по Z)
        filling (list): наполнение водоема - трехмерный массив из экземпляров класса CubicMetre()
        sound_source (CubicMetre): источник звука - экземпляр класса CubicMetre()
        submarine (Submarine): субмарина, подводный аппарат - экземпляр класса Submarine()

    Methods:
        add_sound_source: добавляет источник звука в водоем и для каждого куба воды определяет параметр sound_intensity
        add_submarine: добавляет субмарину (подводный аппарат) в водоем

    """

    def __init__(self, height, heightmap):
        """ Инициализация водоема: заполнение кубами, создание соседских связей, добавление ландшафта

        Args:
            height (int): высота водоема
            heightmap (str): расположение карты высот, как файла .jpg

        Raises:
            ValueError: если заданная высота бассейна ниже или равняется максимальной высоте ландшафта

        """

        im = Image.open(heightmap, 'r')  # читаю карту высот как изображение
        assert height > max(round(pixel[0]) for pixel in list(im.getdata())), \
            ValueError('The height parameter must be greater than ' + str(max(round(pixel[0]) for pixel in list(im.getdata()))))

        length, width = im.size  # вытягиваю параметры карты по которым построю бассейн

        # задаю основные параметры бассейна
        self.height = height  # z
        self.width = width  # y
        self.length = length  # x

        # создаю водные кубы в бассейне
        print('Создаю водные кубы в бассейне:')
        self.filling = []
        for z_position in range(height):
            layer = []
            for y_position in range(width):
                layer.append(deepcopy([None] * length))
            self.filling.append(deepcopy(layer))

        for z_position in range(height):
            for y_position in range(width):
                for x_position in range(length):
                    self.filling[z_position][y_position][x_position] = CubicMetre(x_position, y_position, z_position, True)
            print('\tLayer', z_position, 'completed.')

        # создаю связи между соседними кубами
        print('Создаю связи между соседними кубами:')
        change = [(1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1), (0, 1, 0), (0, -1, 0),
                  (1, 0, -1), (1, 0, 1), (1, 1, 0), (1, -1, 0),
                  (-1, 0, -1), (-1, 0, 1), (-1, 1, 0), (-1, -1, 0),
                  (0, 1, -1), (0, 1, 1), (0, -1, 1), (0, -1, -1),
                  (1, 1, -1), (1, 1, 1), (1, -1, 1), (1, -1, -1),
                  (-1, 1, -1), (-1, 1, 1), (-1, -1, 1), (-1, -1, -1)]
        for z_position in range(self.height):
            for y_position in range(self.width):
                for x_position in range(self.length):
                    for i in range(26):
                        if x_position + change[i][0] < 0 or x_position + change[i][0] > self.length - 1:
                            continue
                        if y_position + change[i][1] < 0 or y_position + change[i][1] > self.width - 1:
                            continue
                        if z_position + change[i][2] < 0 or z_position + change[i][2] > self.height - 1:
                            continue
                        self.filling[z_position][y_position][x_position].neighbours[i] = \
                        self.filling[z_position + change[i][2]][y_position + change[i][1]][x_position + change[i][0]]
            print('\tLayer', z_position, 'completed.')

        # заменяю водные кубы на кубы ландшафта по карте высот
        print('Заменяю водные кубы на кубы ландшафта по карте высот...')
        pixel_values = list(im.getdata())
        pixel_alpha = []
        z = []

        for pixel in pixel_values:
            pixel_alpha.append(round(pixel[0]))

        # создаю двухмерный массив значений высоты ландшафта h от положения по XY
        for i in range(0, len(pixel_alpha), width):
            z.append(pixel_alpha[i:i + width])

        for x_position in range(length):
            for y_position in range(width):
                # по всей высоте h ландшафта в точке (x; y) водные кубы заменяются на кубы ландшафта
                h = z[y_position][x_position]
                for z_position in range(h):
                    self.filling[z_position][y_position][x_position].is_water = False

    def add_sound_source(self, sound_intensity=1000, x_position=None, y_position=None, z_position=None, enhanced_realism=True):
        """ Метод добавляет источник звука в водоем и для каждого куба воды определяет параметр sound_intensity
        (силу звука в нем)

        Args:
            sound_intensity (float|int): сила (интенсивность) звука издаваемого источником необязательный параметр
            x_position (int|None): координата источника звука по оси X
            y_position (int|None): координата источника звука по оси Y
            z_position (int|None): координата источника звука по оси Z
            enhanced_realism (bool): если True - более реалистичное огибание препятствий звуковыми волнами, но огромная
                вычислительная сложность. В ином случае - низкореалистичное распространение кривых, но очень низкая
                вычислительная сложность

        """

        print('Добавляю источник звука...')
        # задаю координаты источника звука (если параметры не заданы, координаты определяются случайным образом)
        if x_position is not None and 0 <= x_position < self.length:  # для иксов
            x_position = x_position
        else:
            x_position = randint(0, self.length - 1)

        if y_position is not None and 0 <= y_position < self.width:  # для игреков
            y_position = y_position
        else:
            y_position = randint(0, self.width - 1)

        # определяю минимально возможное положение по вертикальной оси
        z_min = 1
        while self.filling[z_min][y_position][x_position].is_water is False:
            z_min += 1
        # "ложу" источник звука на дно, либо на заданную высоту
        if z_position is not None and z_min <= z_position < self.height:
            z_position = z_position
        else:
            z_position = z_min

        # добавляю в водоем источник звука, заменяя им куб воды
        self.filling[z_position][y_position][x_position].sound_intensity = sound_intensity
        self.filling[z_position][y_position][x_position].is_water = False
        self.sound_source = self.filling[z_position][y_position][x_position]

        # сканирую весь бассейн и определяю размеры паралелепипеда допущений
        parallelepiped_length = self.length  # x
        parallelepiped_width = self.width  # y

        for z_position in range(self.height):
            # вдоль иксов
            for y_position in range(self.width):
                x_count = 0
                for x_position in range(self.length):
                    if self.filling[z_position][y_position][x_position].is_water is False:
                        x_count += 1
                    elif x_count < parallelepiped_length and x_count != 0:
                        parallelepiped_length = x_count
                        x_count = 0
                if x_count < parallelepiped_length and x_count != 0:
                    parallelepiped_length = x_count

            # вдоль игреков
            for x_position in range(self.width):
                y_count = 0
                for y_position in range(self.length):
                    if self.filling[z_position][y_position][x_position].is_water is False:
                        y_count += 1
                    elif y_count < parallelepiped_width and y_count != 0:
                        parallelepiped_width = y_count
                        y_count = 0
                if y_count < parallelepiped_width and y_count != 0:
                    parallelepiped_width = y_count

        # определяю звуковое давление для каждого кубометра
        print('Определяю звуковое давление для каждого кубометра...')
        for z_position in range(self.height):
            for y_position in range(self.width):
                for x_position in range(self.length):
                    if self.filling[z_position][y_position][x_position].is_water is True:
                        curve_length = shortest_curve(self, (self.sound_source.x_position, self.sound_source.y_position, self.sound_source.z_position),
                                                      (x_position, y_position, z_position),
                                                      (parallelepiped_length, parallelepiped_width),
                                                      enhanced_realism)
                        self.filling[z_position][y_position][x_position].sound_intensity = self.sound_source.sound_intensity / (curve_length ** 2)
            print('\tLayer', z_position, 'completed.')

    def add_submarine(self, x_position=None, y_position=None, z_position=None):
        """ Метод, добавляющий субмарину в водоем

        Args:
            x_position (int|None): координата субмарины по оси X
            y_position (int|None): координата субмарины по оси Y
            z_position (int|None): координата субмарины по оси Z

        """

        self.submarine = Submarine(self, x_position, y_position, z_position)


class Submarine:
    """ Субмарина или подводный аппарат. Экземпляр этого класса призван перемещаться в сторону источника звука в
    водоеме, для чего требует приписки к конкретному водоему класса Pool().

    Note:
        Для корректной работы экземпляра, в приписанном водоеме класса Pool() должен быть определен атрибут sound_source

    Attributes:
        x_position (int): координата субмарины по оси X
        y_position (int): координата субмарины по оси Y
        z_position (int): координата субмарины по оси Z
        pool (Pool): водоем - экземпляр класса Pool(), к которому приписана данная субмарина

    Methods:
        move: перемещает субмарину по координатам в сторону источника звука и по окончании возвращает список координат
        всех посещенных кубометров

    """

    def __init__(self, pool: Pool, x_position=None, y_position=None, z_position=None):
        """ Инициализация субмарины

        Args:
            pool (Pool): водоем в котором размещается субмарина
            x_position (int|None): координата субмарины по оси X
            y_position (int|None): координата субмарины по оси Y
            z_position (int|None): координата субмарины по оси Z

        """

        # задаю координаты субмарины (если параметры не заданы, координаты определяются случайным образом)
        if x_position is not None and 0 <= x_position < pool.length:  # для иксов
            x_position = x_position
        else:
            x_position = randint(0, pool.length - 1)

        if y_position is not None and 0 <= y_position < pool.width:  # для игреков
            y_position = y_position
        else:
            y_position = randint(0, pool.width - 1)

        # определяю минимально возможное положение по вертикальной оси
        z_min = 1
        while pool.filling[z_min][y_position][x_position].is_water is False:
            z_min += 1
        # размещаю субмарину случайным образом в интервале [z_min; pool.height), либо на заданную высоту
        if z_position is not None and z_min <= z_position < pool.height:
            z_position = z_position
        else:
            z_position = randint(z_min, pool.height - 1)

        self.x_position = x_position
        self.y_position = y_position
        self.z_position = z_position
        self.pool = pool

    def move(self, metres=1):
        """ Метод перемещает субмарину по координатам в сторону источника звука и по окончании возвращает список
        координат всех посещенных кубометров.

        Args:
            metres (int|bool): метры для преодоления. Если True, то плывем до источника звука

        Returns:
            list: список координат всех кубов, в которых побывала субмарина во время выполнения функции

        Raises:
            ValueError: если неверно задан параметр metres

        """

        assert (metres >= 1) or (metres is True), ValueError('Parameter "metres" must be greater integer than 0 or boolean True.')

        xyz_to_move = (self.x_position, self.y_position, self.z_position)  # стартовая точка

        positions = []  # все пройденные точки, начиная от стартовой
        while metres:

            positions.append(xyz_to_move)  # добавляю пройденную точку
            comparison = []  # список с силами звукамы в каждом из соседей

            for neighbour in self.pool.filling[self.z_position][self.y_position][self.x_position].neighbours:  # прохожу по всем соседям
                if (neighbour is not None) and (neighbour.sound_intensity is not None):  # если сосед существует и имеет определенную силу звука
                    sound_intensity = neighbour.sound_intensity
                    xyz_to_move = (neighbour.x_position, neighbour.y_position, neighbour.z_position)
                    comparison.append([sound_intensity, xyz_to_move])
            comparison.sort(key=lambda x: x[0])  # сортирую по возрастанию силы звука

            xyz_to_move = comparison[-1][1]  # выбираю соседа с самой большой силой звука
            # если в соседе с самой большой силой звука сила звука такая же как в текущем кубометре, значит дошли до источника звука
            if comparison[-1][0] == self.pool.filling[self.z_position][self.y_position][self.x_position].sound_intensity:
                return positions
            if metres is not True:
                metres -= 1

            # если еще не дошли до источника звука, перемещаемся в соседа с самой большой силой звука
            self.x_position = xyz_to_move[0]
            self.y_position = xyz_to_move[1]
            self.z_position = xyz_to_move[2]

        return positions


def shortest_curve(pool: Pool, ss_xyz, cube_xyz, prl_lw, enhanced_realism=True):
    """ Функция возвращает длину кратчайшей кривой, по которой должен пройти звук, чтобы достиь определенного кубометра.

    Args:
        pool (Pool): водоем
        ss_xyz (tuple|list): координаты источника звука (sound source XYZ)
        cube_xyz (tuple|list): координаты кубометра до которого рассчитывается расстояние
        prl_lw (tuple|list): размеры параллелепипеда допущений (parallelepiped length, width)
        enhanced_realism (bool): если True - более реалистичное огибание препятствий, но огромная вычислительная сложность.
            В ином случае - низкореалистичное распространение кривых, но очень низкая вычислительная сложность

    Returns:
        float|int: curve_len - длина кривой от источника звука до кубометра

    Raises:
        ValueError: если куб-цель на координатах cube_xyz не является водой

    """

    # проверяю является ли выбранный кубометр водой
    assert pool.filling[cube_xyz[2]][cube_xyz[1]][cube_xyz[0]].is_water is True, \
        ValueError('To determine the intensity of the sound, the cube must be composed of water')
    # если кубометр уже имеет заданную интенсивность звука, функция вернет текущее значение интенсивности звука
    if pool.filling[cube_xyz[2]][cube_xyz[1]][cube_xyz[0]].sound_intensity is not None:
        return pool.filling[cube_xyz[2]][cube_xyz[1]][cube_xyz[0]].sound_intensity

    # определяю значения для первой проверки в цикле
    x_dto = abs(cube_xyz[0] - ss_xyz[0])  # distance to overcome
    y_dto = abs(cube_xyz[1] - ss_xyz[1])
    z_dto = abs(cube_xyz[2] - ss_xyz[2])

    # определяю самые выгодные позиции по Z по убыванию
    z_poss = []
    for z_pos in range(pool.height):
        z_poss.append([abs(cube_xyz[2] - z_pos), z_pos])
    z_poss.sort(key=lambda x: x[0])

    curve_len = 0

    while x_dto + y_dto + z_dto != 0:
        np_xyz = ss_xyz  # new point XYZ

        if enhanced_realism is True:
            xyz_poss = []
            for z_pos in range(pool.height):  # по всей высоте бассейна

                for y_pos in range(ss_xyz[1] - prl_lw[1], ss_xyz[1] + prl_lw[1] + 1):  # Y в диапазоне параллелепипеда допущений
                    if 0 <= y_pos < pool.width:  # если нахожусь внутри бассейна

                        for x_pos in range(ss_xyz[0] - prl_lw[0], ss_xyz[0] + prl_lw[0] + 1):  # X в диапазоне параллелепипеда допущений
                            if 0 <= x_pos < pool.length:  # если нахожусь внутри бассейна

                                # определяю расстояния от новых координат до цели
                                x_dto = abs(cube_xyz[0] - x_pos)
                                y_dto = abs(cube_xyz[1] - y_pos)
                                z_dto = abs(cube_xyz[2] - z_pos)

                                # добавляю в список сумму остатков и новые координаты, чтобы потом выбрать самую выгодную
                                xyz_poss.append([x_dto + y_dto + z_dto, x_dto + y_dto, (x_pos, y_pos, z_pos)])

            xyz_poss.sort(key=lambda x: x[0])  # сортирую самые выгодные позиции по убыванию (возрастает сумма расстояний)

            for i in range(len(xyz_poss)):
                # если приближаемся (т.е. не отдаляемся и не стоим на месте) к кубу-цели по трем осям
                if xyz_poss[i][0] < abs(cube_xyz[0] - ss_xyz[0]) + abs(cube_xyz[1] - ss_xyz[1]) + abs(cube_xyz[2] - ss_xyz[2]):
                    # если не отдаляемся от куба цели по осям X и Y
                    if xyz_poss[i][1] <= abs(cube_xyz[0] - ss_xyz[0]) + abs(cube_xyz[1] - ss_xyz[1]):  # можно поэкспериментировать со строгостью знака
                        x_pos = xyz_poss[i][2][0]
                        y_pos = xyz_poss[i][2][1]
                        z_pos = xyz_poss[i][2][2]
                        if pool.filling[z_pos][y_pos][x_pos].is_water is True:
                            # если по координатам попадаю в водный куб, то выбираю его как новый опорный т.к. он самый оптимальный
                            np_xyz = (x_pos, y_pos, z_pos)
                            break

        # если не удалось выбрать выгодный куб для перемещения, или изначально не был выбран режим повышенной реалистичности
        if np_xyz == ss_xyz:
            xy_poss = []
            for y_pos in range(ss_xyz[1] - prl_lw[1], ss_xyz[1] + prl_lw[1] + 1):  # Y в диапазоне параллелепипеда допущений
                if 0 <= y_pos < pool.width:  # если нахожусь внутри бассейна

                    for x_pos in range(ss_xyz[0] - prl_lw[0], ss_xyz[0] + prl_lw[0] + 1):  # X в диапазоне параллелепипеда допущений
                        if 0 <= x_pos < pool.length:  # если нахожусь внутри бассейна

                            # определяю расстояния от новых координат до цели
                            x_dto = abs(cube_xyz[0] - x_pos)
                            y_dto = abs(cube_xyz[1] - y_pos)

                            # добавляю в список сумму остатков и новые координаты, чтобы потом выбрать самую выгодную
                            xy_poss.append([x_dto + y_dto, (x_pos, y_pos)])

            xy_poss.sort(key=lambda x: x[0])  # сортирую самые выгодные позиции по убыванию (возрастает сумма расстояний)

            for i in range(len(xy_poss)):
                # выбираю лучшие координаты по XY
                x_pos = xy_poss[i][1][0]
                y_pos = xy_poss[i][1][1]
                for j in range(len(z_poss)):
                    # выбираю лучшую координату по Z
                    z_pos = z_poss[j][1]
                    if pool.filling[z_pos][y_pos][x_pos].is_water is True:
                        # если по координатам попадаю в водный куб, то выбираю его как новый опорный т.к. он самый оптимальный
                        np_xyz = (x_pos, y_pos, z_pos)
                        break
                if np_xyz != ss_xyz:
                    break

        # после того как выбрал новую опорную точку отсчитываю расстояние от старой точки до новой
        curve_len += sqrt((np_xyz[0] - ss_xyz[0]) ** 2 + (np_xyz[1] - ss_xyz[1]) ** 2 + (np_xyz[2] - ss_xyz[2]) ** 2)
        ss_xyz = np_xyz  # и переопределяю старую точку как новую, т.е. двигаюсь вперед по цепи

        # считаю оставшиеся расстояния чтобы в новой итерации проверить не дошел ли уже до нужного кубометра
        x_dto = abs(cube_xyz[0] - ss_xyz[0])
        y_dto = abs(cube_xyz[1] - ss_xyz[1])
        z_dto = abs(cube_xyz[2] - ss_xyz[2])

    return curve_len
