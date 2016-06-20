# Добавление библиотек
import pygame
import sys # Взаимодействует с интерпретатором Python'а
from pygame.locals import * # pygame.locals содержит константы pygame (типа QUIT или K_ESCAPE)
import math
import pyganim # Для анимации
import os # Для работы с файловой системой

pygame.init() # Инициация PyGame, обязательная строчка
CHARACTERS = pygame.sprite.Group()
PLATFORMS = pygame.sprite.Group()

info_object = pygame.display.Info() # Объект с информацией о графической среде компьютера
WIN_WIDTH = info_object.current_w # Ширина главного создаваемого окна
WIN_HEIGHT = info_object.current_h # Высота
WINDOW = (WIN_WIDTH, WIN_HEIGHT) # Заносим ширину и высоту в одну переменную
FPS = 160
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
		self.img = './resources/characters/hero/stand/1.png'
		self.right_standing = pygame.image.load(self.img)
		self.left_standing = pygame.transform.flip(self.right_standing, True, False)
		GameObject.__init__(self, self.img, x, y)
		
		self.running = self.on_ground = self.left = self.right = self.down = self.up = False
		
		self.v_x = 0
		self.v_y = 0
		self.power = 4 # Ускорение при беге
		self.v_lim = 10 # Предельная скорость
		self.direction = 'right'
		
		global CHARACTERS
		CHARACTERS.add(self)
		
		animTypes = 'jump roll right_run'.split()
		self.animObjs = {}
		for animType in animTypes:
			path = './resources/characters/hero/%s/' % animType
			num_files = len(os.listdir(path))
			imagesAndDurations = [(path + '%s.png' % str(num), 200) for num in range(1, num_files + 1)]
			self.animObjs[animType] = pyganim.PygAnimation(imagesAndDurations)
		self.animObjs['left_run'] = self.animObjs['right_run'].getCopy()
		self.animObjs['left_run'].flip(True, False)
		self.animObjs['left_run'].makeTransformsPermanent()
		self.moveConductor = pyganim.PygConductor(self.animObjs)
	
	# Меняет положение согласно действующим силам
	def update(self):
		if self.left:
			self.v_x += -self.power
			if self.v_x < -self.v_lim:
				self.v_x = -self.v_lim
		elif self.right:
			self.v_x += self.power
			if self.v_x > self.v_lim:
				self.v_x = self.v_lim
		elif self.up and self.on_ground:
				self.v_y = -30
		elif not(self.running) and self.on_ground and self.v_x != 0:
			self.v_x += math.copysign(self.power, -self.v_x) # Замедление при остановке
			if abs(self.v_x) <= self.power:
				self.v_x = 0
		
		if not self.on_ground:
			global G
			self.v_y += G
		self.on_ground = False
		self.rect.x += self.v_x
		self.rect.y += self.v_y
	
	# Отвечает за анимацию
	def draw(self, scr):	
		x = self.rect.x
		y = self.rect.y
		if self.running or not(self.on_ground):
			self.moveConductor.play()
			if self.direction == 'up':
				self.animObjs['jump'].blit(scr, (x, y))
			elif self.direction == 'down':
				self.animObjs['roll'].blit(scr, (x, y))
			elif self.direction == 'left':
				self.animObjs['left_run'].blit(scr, (x, y))
			elif self.direction == 'right':
				self.animObjs['right_run'].blit(scr, (x, y))
		else:
			self.moveConductor.stop()
			if self.direction == 'left':
				scr.blit(self.left_standing, (x, y))
			elif self.direction == 'right':
				scr.blit(self.right_standing, (x, y))

def init_window():
	global WINDOW
	pygame.display.set_mode(WINDOW, pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF) # Создаем окно
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

			if event.key == K_LEFT:
				hero.left = True
				hero.right = False
				hero.running = True
				if not (hero.up or hero.down):
					hero.direction = 'left'
					# direction влияет только на анимацию, но не на обсчет положения
					# Поэтому в ином случае спрайт просто не понменяется, например, с верхнего на левый
			elif event.key == K_RIGHT:
				hero.right = True
				hero.left = False
				hero.running = True
				if not (hero.up or hero.down):
					hero.direction = 'right'
			elif event.key == K_DOWN:
				hero.down = True
				hero.up = False
				if not (hero.left or hero.right):
					hero.direction = 'down'
			elif event.key == K_UP:
				hero.up = True
				hero.down = False
				hero.direction = 'up'
				
		
		elif event.type == KEYUP:
			
			if event.key == K_UP:
				hero.up = False
			elif event.key == K_DOWN:
				hero.down = False
				if hero.left:
					hero.direction = 'left'
				if hero.right:
					hero.direction = 'right'
				# Если зажато 2 кнопки, спрайт, возмонжо, был нижний
			elif event.key == K_LEFT:
				hero.left = False
				if hero.down:
					hero.direction = 'down'
			elif event.key == K_RIGHT:
				hero.right = False
				if hero.down:
					hero.direction = 'down'

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
						if char.left:
							char.direction = 'left'
						if char.right:
							char.direction = 'right'
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
	Clock = pygame.time.Clock()
# В бесконечном цикле принимаем и обрабатываем сообщения
	while 1:
		process_events(pygame.event.get(), hero)
		draw_background(screen, background) # Фон перерисовывается поверх устаревших положений персонажей
		hero.update()
		collide(CHARACTERS, PLATFORMS)
		PLATFORMS.draw(screen)
		hero.draw(screen)
		pygame.display.update() # Обновление экрана
		Clock.tick(FPS)

# Если этот файл импортируется в другой, этот __name__ равен имени импортируемого файла 
# без пути и расширения ('main'). Если файл запускается непосредственно, __name__  
# принимает значенние __main__
if __name__ == "__main__":
	init_window() # Инициализируем окно приложения
	main()