"""
Created by Ivan Danylenko
Date 18.11.21
"""

from PIL import Image
from time import time
from functools import wraps
from ursina import Entity, camera, held_keys

# первоопределяю время последнего использования функций с огрниченной частотой использования
lastNewSubmarinePosUse = [time()]
lastAddNewSubmarineUse = [time()]


def execution_frequency(cooldown, last_use):
    """ Декоратор, ограничивающий частоту выполнения декорируемой функции до 1 раза в заданный временной период. """

    def _execution_frequency(f):

        @wraps(f)
        def inner(*args, **kwargs):
            if time() - last_use[0] >= cooldown:
                last_use[0] = time()
                f(*args, **kwargs)
        return inner

    return _execution_frequency


def get_max_height(heightmap):
    """ Возвращает значение высоты самой высокой точки ландшафта. """

    pixel_alpha = []
    for pixel in list(Image.open(heightmap, 'r').getdata()):
        pixel_alpha.append(round(pixel[0]))
    return max(pixel_alpha)


@execution_frequency(cooldown=0.15, last_use=lastNewSubmarinePosUse)
def new_submarine_pos(submarine: Entity, positions, pool, z_scale):
    """ Задает отображаемому объекту первую позицию из списка и затем удаляет ее из списка.

    Args:
        submarine (Entity): отображаемый объект, выступающий в роли субмарины
        positions (list): последовательность позиций, в которых побывала субмарина
        pool (Pool): водоем в котором находится субмарина. Нужен для определения положения лодки по его длине и ширине
        z_scale (float|int): коэффициент масштабирования вертикальной оси

    """

    if positions:
        if held_keys['q'] != 0:
            submarine.position = (positions[0][0] - pool.length / 2,
                                  (positions[0][2] + 0.5) * z_scale,
                                  pool.width - 1 - positions[0][1] - pool.width / 2)
            positions.pop(0)


@execution_frequency(cooldown=0.5, last_use=lastAddNewSubmarineUse)
def add_new_submarine(pool, positions):
    if held_keys['n'] != 0:
        pool.add_submarine()
        new_positions = pool.submarine.move(True)
        while positions:
            positions.pop()
        for pos in new_positions:
            positions.append(pos)
        return positions


def change_camera_pos():
    """ В зависимасти от нажатой клавиши W|A|S|D, меняет положение камеры в плоскости XZ. """

    if held_keys['w'] != 0:
        camera.position = camera.position[0], camera.position[1] + 1, camera.position[2]
    if held_keys['s'] != 0:
        camera.position = camera.position[0], camera.position[1] - 1, camera.position[2]
    if held_keys['a'] != 0:
        camera.position = camera.position[0] - 1, camera.position[1], camera.position[2]
    if held_keys['d'] != 0:
        camera.position = camera.position[0] + 1, camera.position[1], camera.position[2]
