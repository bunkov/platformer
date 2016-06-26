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
FPS = 60
G = 1 # Ускорение свободного падения

class GameObject(pygame.sprite.Sprite):
	# img - путь к файлу с изображением объекта
	# x, y - координаты объекта на игровом поле
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load(img) # Загружаем изображение объекта
		self.x = x
		self.y = y
		self.width, self.height = self.image.get_size()
		self.rect = Rect(x, y, self.width, self.height)

class Platform(GameObject):
	def __init__(self, x, y):
		global PLATFORMS
	
		self.img = './resources/platforms/wall.png'
		GameObject.__init__(self, self.img, x, y)
		
		PLATFORMS.add(self)

class Hero(GameObject):
	def __init__(self, x, y):
		global CHARACTERS
		global FPS
		
		self.img = './resources/characters/hero/stand/1.png'
		self.right_standing = pygame.image.load(self.img)
		self.left_standing = pygame.transform.flip(self.right_standing, True, False)
		GameObject.__init__(self, self.img, x, y)
		
		self.on_ground = self.left = self.right = self.down = self.up = self.jumping = False
		
		self.v_x = 0
		self.v_y = 0
		self.power = 2*self.height/FPS # Ускорение при беге. 
		# Из-за него на данный момент прохождение сквозь стены
		self.v_lim = 12*self.height/FPS # Предельная скорость 
		# Скорость [высот/тик] = [высот/с] / [тик/с]
		self.direction = 'right'
		
		CHARACTERS.add(self)
		
		animTypes = 'jump roll run'.split()
		self.animObjs = {}
		
		for animType in animTypes:
			animType_r = 'right_' + animType
			animType_l = 'left_' + animType
			path = './resources/characters/hero/%s/' % animType_r
			files = os.listdir(path)
			num_files = 0
			for file in files:
				if file[-4:] == '.png': # В папке могут содержаться скрытые системные файлы, например, Thumbs.db
					num_files += 1
					
			imagesAndDurations = [(path + str(num) + '.png', 60) for num in range(1, num_files + 1)]
			self.animObjs[animType_r] = pyganim.PygAnimation(imagesAndDurations)
			
			self.animObjs[animType_l] = self.animObjs[animType_r].getCopy()
			self.animObjs[animType_l].flip(True, False) # Отразить по горизонтали
			self.animObjs[animType_l].makeTransformsPermanent()

		self.moveConductor = pyganim.PygConductor(self.animObjs)
	
	# Меняет положение согласно действующим силам
	def update(self):
		global G
		
		if self.left:
			self.v_x += -self.power
			if self.v_x < -self.v_lim:
				self.v_x = -self.v_lim
		elif self.right:
			self.v_x += self.power
			if self.v_x > self.v_lim:
				self.v_x = self.v_lim
		elif not(self.left or self.right) and self.on_ground:  
			self.v_x = 0
			'''and self.v_x != 0:
			self.v_x += math.copysign(self.power, -self.v_x) # Замедление при остановке
			if abs(self.v_x) <= self.power:
				self.v_x = 0'''
			
		
		if self.up and self.on_ground:
			self.v_y = -12*G
		
		if not self.on_ground:
			self.v_y += G
		self.on_ground = False
		self.rect.x += self.v_x
		self.rect.y += self.v_y
	
	# Отвечает за анимацию
	def draw(self, scr):	
		x = self.rect.x
		y = self.rect.y
		coords = (x, y)
		if self.left or self.right or self.jumping:
			self.moveConductor.play()
			if self.direction == 'left':
				if self.jumping:
					self.animObjs['left_jump'].blit(scr, coords)
				else:
					self.animObjs['left_run'].blit(scr, coords)
			else: # self.direction == 'right'
				if self.jumping:
					self.animObjs['right_jump'].blit(scr, coords)
				else:
					self.animObjs['right_run'].blit(scr, coords)
		else: # standing
			self.moveConductor.stop()
			if self.direction == 'left':
				scr.blit(self.left_standing, coords)
			elif self.direction == 'right':
				scr.blit(self.right_standing, coords)

def init_window():
	global WINDOW
	
	pygame.display.set_mode(WINDOW, pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF) # Создаем окно
	pygame.display.set_caption("Platformer") # Задаем заголовок окна

# Рисует фон
# scr - экран, на котором требуется отрисовать
# img - фоновая картинка. Если отсутствует, осуществляется заливка серым фоном
def draw_background(scr, img = None):
	'''if img:
		img_width, img_height = img.get_size() # get_size() - метод Surface
		global WINDOW
		ratio_width = math.ceil(WINDOW[0]/img_width)
		ratio_height = math.ceil(WINDOW[1]/img_height)
		for h in range(ratio_height):
			for w in range(ratio_width):
				# Второй аргумент blit() - координаты левого верхнего края изображения
				# относительно того же края экрана
				scr.blit(img, (img_width*w, img_height*h))
	else:''' # Жрет много FPS
	background = pygame.Surface(scr.get_size())
	background.fill((0, 0, 0))
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
				hero.direction = 'left'
			elif event.key == K_RIGHT:
				hero.right = True
				hero.left = False
				hero.direction = 'right'
			elif event.key == K_DOWN:
				hero.down = True
				hero.up = False
			elif event.key == K_UP:
				hero.up = True
				hero.down = False
				hero.jumping = True
				
		
		elif event.type == KEYUP:
			
			if event.key == K_UP:
				hero.up = False
			elif event.key == K_DOWN:
				hero.down = False
			elif event.key == K_LEFT:
				hero.left = False
			elif event.key == K_RIGHT:
				hero.right = False

# Обрабатывает столкновения
def collide(characters, platforms):
	global G
	
	for char in characters.sprites():
		for plate in platforms.sprites():
			if pygame.sprite.collide_rect(char, plate): # Если персонаж столкнулся с платформой
				# Если бы персонаж не двигался по x
				char.rect.x -= math.copysign(math.ceil(abs(char.v_x)), char.v_x) 
				# (Из-за дробей смещение происходит на величину, большую скорости,
				# что приводит к прохождению стен при использовании char.rect.x -= char.v_x)
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
						if not(char.up):
							char.jumping = False
					if char.v_y < 0: # Если вверх
						char.rect.top = plate.rect.bottom
						char.v_y = 0
			else:
				char.rect.y += G
				if pygame.sprite.collide_rect(char, plate): # Если под ногами что-то есть
					char.on_ground = True
				char.rect.y -= G

# Отображает FPS на экране
def print_info(scr, font, seconds, frames, hero):
	global WINDOW
	
	fps = int(frames/seconds*10)/10
	
	infoParams = 'fps hero.direction hero.on_ground hero.jumping hero.rect.x hero.rect.y'.split()
	i = 1
	for param in infoParams:
		infStr = '%s = %s' % (param, eval(param))
		infSurf = font.render(infStr, False, (255, 255, 255))
		infRect = infSurf.get_rect()
		infRect.topright = (WINDOW[0] - 20, 20*i)
		scr.blit(infSurf, infRect)
		i += 1
				
def main():
	global FPS
	global CHARACTERS
	global PLATFORMS
	
	background = pygame.image.load("./resources/backgrounds/background.png") # Загружаем изображение
	screen = pygame.display.get_surface()
	# Засовывать это в init_window() нельзя: screen требуется для draw() персонажей,
	# и сделать screen глобальным параметром, определив до создания окна, тоже невозможно
	
	hero = Hero(100, 100)
	for i in range(36):
		Platform(100+32*i,600)
	for i in range(10):
		Platform(300+32*i,536)
	
	'''objects = pygame.sprite.Group()
	objects.add(CHARACTERS)
	objects.add(PLATFORMS)'''
	
	play_time = 0
	
	Clock = pygame.time.Clock()
	
	text_font = pygame.font.Font('freesansbold.ttf', 16)

# В бесконечном цикле принимаем и обрабатываем сообщения
	while 1:
		process_events(pygame.event.get(), hero)
		draw_background(screen, background) # Фон перерисовывается поверх устаревших положений персонажей
		hero.update()
		collide(CHARACTERS, PLATFORMS)
		PLATFORMS.draw(screen)
		hero.draw(screen)
		
		tick = Clock.tick(FPS)
		print_info(screen, text_font, tick/1000, 1, hero)
		
		pygame.display.update() # Обновление экрана

# Если этот файл импортируется в другой, этот __name__ равен имени импортируемого файла 
# без пути и расширения ('main'). Если файл запускается непосредственно, __name__  
# принимает значенние __main__
if __name__ == "__main__":
	init_window() # Инициализируем окно приложения
	main()