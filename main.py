# Добавление библиотек
import pygame
import sys # Взаимодействует с интерпретатором Python'а
from pygame.locals import * # pygame.locals содержит константы pygame (типа QUIT или K_ESCAPE)
import math

pygame.init() # Инициация PyGame, обязательная строчка
CHARACTERS = pygame.sprite.Group()
PLATFORMS = pygame.sprite.Group()

info_object = pygame.display.Info() # Объект с информацией о графической среде компьютера
WIN_WIDTH = info_object.current_w # Ширина главного создаваемого окна
WIN_HEIGHT = info_object.current_h # Высота
WINDOW = (WIN_WIDTH, WIN_HEIGHT) # Заносим ширину и высоту в одну переменную
FPS = 40
G = 10 # Ускорение свободного падения

class GameObject(pygame.sprite.Sprite):
	# img - путь к файлу с изображением объекта
	# x, y - координаты объекта на игровом поле
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load(img) # Загружаем изображение объекта
		self.x = x
		self.y = y
		img_width, img_height = self.image.get_size()
		self.rect = Rect(x, y, img_width, img_height)

class Platform(GameObject):
	def __init__(self, x, y):
		self.img = './resources/platforms/wall.png'
		GameObject.__init__(self, self.img, x, y)
		global PLATFORMS
		PLATFORMS.add(self)

class Hero(GameObject):
	def __init__(self, x, y):
		self.img = './resources/characters/stand.png'
		GameObject.__init__(self, self.img, x, y)
		self.action = 'stand'
		self.v_x = 0
		self.v_y = 0
		self.power = 1 # Ускорение при беге
		self.v_lim = 8 # Предельная скорость
		self.on_ground = False
		global CHARACTERS
		CHARACTERS.add(self)
		
		self.sprites = list()
		self.all_frames = pygame.image.load('./resources/characters/run.png')
		self.sprites.append(self.all_frames.subsurface((36, 38 , 239, 293)))
		self.sprites.append(self.all_frames.subsurface((287, 62, 239, 293)))
		self.sprites.append(self.all_frames.subsurface((565, 72, 239, 293)))
		self.sprites.append(self.all_frames.subsurface((851, 80, 239, 293)))
		self.sprites.append(self.all_frames.subsurface((1114, 90, 239, 293)))
		self.sprites.append(self.all_frames.subsurface((12, 404, 239, 293)))
		self.sprites.append(self.all_frames.subsurface((291, 410, 239, 293)))
		self.sprites.append(self.all_frames.subsurface((567, 406, 239, 293)))
		self.sprites.append(self.all_frames.subsurface((835, 426, 239, 293)))
		self.sprites.append(self.all_frames.subsurface((1115, 414, 239, 293)))
		len_spr = len(self.sprites)
		for i in range(len_spr):
			self.sprites[i] = pygame.transform.scale(self.sprites[i], (64, 78))
		
		self.step_frames = len_spr/2 # Кол-во кадров на шаг
		self.step_pixels = self.power # Кол-во пикселей на шаг
		self.time = 0 # Время, уделяемое одному кадру в анимации (миллисекунды)
		self.work_time = 0 # Прошло времени с первого кадра
		self.skip_frame = 0 # Кол-во кадров, которые следует пропустить
		self.frame = 0 # Номер текущего кадра относительно первого
	
	# Меняет положение согласно действующим силам, вызывает обновление изображения спрайта
	def update(self, dt):
		if self.action == 'left':
			self.v_x += -self.power
			if self.v_x < -self.v_lim:
				self.v_x = -self.v_lim
		elif self.action == 'right':
			self.v_x += self.power
			if self.v_x > self.v_lim:
				self.v_x = self.v_lim
		elif self.action == 'up' and self.on_ground:
				self.v_y = -30
		elif self.action == 'stand' and self.on_ground:
			self.v_x += math.copysign(self.power, -self.v_x) # Замедление при остановке
			if abs(self.v_x) <= self.power:
				self.v_x = 0
		
		if not self.on_ground:
			global G
			self.v_y += G
		self.on_ground = False
		self.rect.x += self.v_x
		self.rect.y += self.v_y
		
		if self.v_x == 0:
			self.time = 0
			self.image = pygame.image.load('./resources/characters/stand.png')
		else:
			self.time = self.step_pixels/(self.step_frames * abs(self.v_x))
		self.update_img(dt)
	
	# Обновляет изображение спрайта
	def update_img(self, dt):
		self.work_time += dt
		time = int(self.time * 1000) # В миллисекунды
		if self.time != 0:
			print(self.work_time)
			self.skip_frame = self.work_time // time
			self.work_time = self.work_time % time
			self.frame += self.skip_frame
			print(self.work_time, self.skip_frame)
			if self.frame >= len(self.sprites):
				self.frame = 0
			print(self.frame, 1/self.time)
			self.image = self.sprites[self.frame]

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

			# Выставляем значение поля action у персонажа в зависимости от нажатой клавиши
			if event.key == K_LEFT:
				hero.action = 'left'
			elif event.key == K_RIGHT:
				hero.action = 'right'
			elif event.key == K_DOWN:
				hero.action = 'down'
			elif event.key == K_UP:
				hero.action = 'up'
		
		elif event.type == KEYUP:
			hero.action = 'stand'

# Обрабатывает столкновения
def collide(characters, platforms):
	for char in characters.sprites():
		for plate in platforms.sprites():
			if pygame.sprite.collide_rect(char, plate): # Если персонаж столкнулся с платформой
				char.rect.x -= char.v_x # Если бы персонаж не двигался по x
				if not pygame.sprite.collide_rect(char, plate): # и столкновения бы не произошло
					if char.v_x > 0: # Если движется вправо
						char.rect.right = plate.rect.left
					if char.v_x < 0: #	Если влево
						char.rect.left = plate.rect.right
				else:
					char.rect.x += char.v_x
					if char.v_y > 0: # Если падает
						char.rect.bottom = plate.rect.top
						char.on_ground = True # Столкнулся - находится на земле
						char.v_y = 0
					if char.v_y < 0: # Если вверх
						char.rect.top = plate.rect.bottom
						char.v_y = 0
			else:
				global G
				char.rect.y += G
				if pygame.sprite.collide_rect(char, plate): # Если под ногами что-то есть
					char.on_ground = True
				char.rect.y -= G
def main():
	background = pygame.image.load("./resources/backgrounds/background.png") # Загружаем изображение
	screen = pygame.display.get_surface()
	# Засовывать это в init_window() нельзя: screen требуется для draw() персонажей,
	# и сделать screen глобальным параметром, определив до создания окна, тоже невозможно
	hero = Hero(100, 100)
	for i in range(36):
		Platform(100+32*i,200)
	
	global CHARACTERS
	global PLATFORMS
	objects = pygame.sprite.Group()
	objects.add(CHARACTERS)
	objects.add(PLATFORMS)
	
	global FPS
	dt = 0
	Clock = pygame.time.Clock()
# В бесконечном цикле принимаем и обрабатываем сообщения
	while 1:
		process_events(pygame.event.get(), hero)
		draw_background(screen, background) # Фон перерисовывается поверх устаревших положений персонажей
		hero.update(dt)
		collide(CHARACTERS, PLATFORMS)
		objects.draw(screen)
		pygame.display.update() # Обновление экрана
		dt = Clock.tick(60)
# Если этот файл импортируется в другой, этот __name__ равен имени импортируемого файла 
# без пути и расширения ('main'). Если файл запускается непосредственно, __name__  
# принимает значенние __main__
if __name__ == "__main__":
	init_window() # Инициализируем окно приложения
	main()