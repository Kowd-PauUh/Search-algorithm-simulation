"""
Created by Ivan Danylenko
Date 09.11.21
"""

#  Управление симуляцией:
#       Управление положением камеры в плоскости XZ:    Press W|A|S|D
#       Управление углом камеры:                        Hold RMB and drag
#       ZOOM:                                           Scroll
#       Перемещение субмарины:                          Press Q (delay 0.15s)
#       Создание новой субмарины:                       Hold N for 0.5s (delay 0.5s) then press Q 1 time
#  Примечание: новая субмарина генерируется на случайных координатах

from ursina import *
from classes import Pool
from functions_for_visualisation import *


def update():
    # определение новой субмаринны и всех ее позиций по пути к источнику звука
    add_new_submarine(pool, submarine_positions)
    new_submarine_pos(submarine, submarine_positions, pool, z_scale)  # определение позиции субмарины для отображения
    change_camera_pos()  # управление камерой


heightmap = 'Heightmaps/heightmap_demonstration.jpg'  # задать путь к файлу
z_scale = 1  # коэффициент масштабирования отображаемой высоты

# создание водной среды, источника звука и субмарины
pool = Pool(get_max_height(heightmap) + 1, heightmap)  # бассейн высотой на 1 больше чем высота ландшафта
pool.add_sound_source(enhanced_realism=False)
pool.add_submarine()

# вытягиваю параметры длины и ширины водоема
length = pool.length
width = pool.width

# определение отображаемого положения источника звука и субмарины
sound_source_pos = (pool.sound_source.x_position - length / 2,
                    (pool.sound_source.z_position + 0.5) * z_scale,
                    width - 1 - pool.sound_source.y_position - width / 2)
submarine_pos = (pool.submarine.x_position - length / 2,
                 (pool.submarine.z_position + 0.5) * z_scale,
                 width - 1 - pool.submarine.y_position - width / 2)

# создаю сцену
app = Ursina()
window.color = color.white
window.fullscreen = True
camera.position = (get_max_height(heightmap) * 6 / 108 * z_scale,
                   get_max_height(heightmap) * 33 / 108 * z_scale,
                   - get_max_height(heightmap) * 207 / 108 * z_scale)  # начальное положение зависит от высоты бассейна

# добавляю освещение
AmbientLight(color=(0.5, 0.5, 0.5, 1))
DirectionalLight(color=(0.5, 0.5, 0.5, 1), direction=(1, 1, 0))

# добавление ландшафта и двух шаров, имитирующих источник звука и субмарину
landschaft = Entity(model=Terrain(heightmap, skip=1, pool_terrain=True),
                    scale=(length, z_scale, width),
                    # если есть соответствующий файл с текстурами должна быть откомментирована строка ниже
                    # texture=heightmap[:len(heightmap)-4]+'_texture.jpg',
                    # в противном случае закомментировать строку выше и откомментировать строку ниже
                    texture=heightmap
                    )
sound_source = Entity(model='sphere', position=sound_source_pos, color=color.red)
# плавное перемещение субмарины: объект Entity следует за положением submarine
submarine = Entity(position=submarine_pos)
Entity(model='sphere', position=submarine_pos, color=color.green).add_script(SmoothFollow(speed=5,
                                                                                          target=submarine,
                                                                                          offset=(0, 0, 0)))
# имитация воды - полупрозрачный голубой куб
Entity(model='cube', scale=(landschaft.scale[0],
                            get_max_height(heightmap) * landschaft.scale[1] + 2,
                            landschaft.scale[2]),
       color=color.blue, alpha=0.15, position=(0, get_max_height(heightmap) * landschaft.scale[1] / 2, 0))

# определение всех позиций первой субмарины по пути к источнику звука
submarine_positions = pool.submarine.move(True)

# mouse.visible = False
EditorCamera()  # возможность управлять камерой
app.run()
