# Добавление библиотек
import pygame
import sys # Взаимодействует с интерпретатором Python'а
from pygame.locals import * # pygame.locals содержит константы pygame (типа QUIT или K_ESCAPE)
import math

pygame.init() # Инициация PyGame, обязательная строчка

info_object = pygame.display.Info() # Объект с информацией о графической среде компьютера
WIN_WIDTH = info_object.current_w # Ширина главного создаваемого окна
WIN_HEIGHT = info_object.current_h # Высота
WINDOW = (WIN_WIDTH, WIN_HEIGHT) # Заносим ширину и высоту в одну переменную

class hero():
	pass

def init_window():
	global WINDOW
	pygame.display.set_mode(WINDOW, pygame.FULLSCREEN) # Создаем окно
	pygame.display.set_caption("Platformer") # Задаем заголовок окна

# Рисует фон
# scr - экран, на котором требуется отрисовать
# img - фоновая картинка. Если отсутствует, осуществляется заливка серым фоном
def draw_background(scr, img = None):
	if img:
		img_width, img_height = img.get_size() # get_size() - метод Surface
		global WINDOW
		ratio_width = math.ceil(WINDOW[0]/img_width)
		ratio_height = math.ceil(WINDOW[1]/img_height)
		for h in range(ratio_height):
			for w in range(ratio_width):
				# Второй аргумент blit() - координаты левого верхнего края изображения
				# относительно того же края экрана
				scr.blit(img, (img_width*w, img_height*h))
	else:
		background = pygame.Surface(scr.get_size())
		background.fill((128, 128, 128))
		scr.blit(background, (0, 0))

# Обрабатывает события
def process_events(events, hero):
	for event in events:
		# Если была нажата кнопка закрытия окна или клавиша Esc, то процесс завершается
		if (event.type == QUIT) or (event.type == KEYDOWN and event.key == K_ESCAPE):
			sys.exit(0) # 0 - не кидать исключение SystemExit

		elif event.type == KEYDOWN:

			# Выставляем значение поля direction у персонажа в зависимости от нажатой клавиши
			if event.key == K_LEFT:
				hero.direction = 3
			elif event.key == K_RIGHT:
				hero.direction = 1
			elif event.key == K_UP:
				hero.direction = 4
			elif event.key == K_DOWN:
				hero.direction = 2
			elif event.key == K_SPACE:
				hero.direction = 0

			# Запуск тестового режима
			elif event.key == K_t:
				test()
		
def main():
	background = pygame.image.load("./resources/backgrounds/background.png") # Загружаем изображение
	screen = pygame.display.get_surface()
	# Засовывать это в init_window() нельзя: screen требуется для draw() персонажей,
	# и сделать screen глобальным параметром, определив до создания окна, тоже невозможно

# В бесконечном цикле принимаем и обрабатываем сообщения
	while 1: 
		process_events(pygame.event.get(), hero)
		draw_background(screen, background) # Фон перерисовывается поверх устаревших положений персонажей
		pygame.display.update() # Обновление экрана
		
# Если этот файл импортируется в другой, этот __name__ равен имени импортируемого файла 
# без пути и расширения ('main'). Если файл запускается непосредственно, __name__  
# принимает значенние __main__
if __name__ == "__main__":
	init_window() # Инициализируем окно приложения
	main()