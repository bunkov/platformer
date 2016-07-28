# Добавление библиотек
import pygame
import sys # Взаимодействует с интерпретатором Python'а
from pygame.locals import * # pygame.locals содержит константы pygame (типа QUIT или K_ESCAPE)
import math
import pyganim # Для анимации
import os # Для работы с файловой системой
import pytmx # Загружает карты из Tiled Map Editor и переводит в понятный pygame формат

pygame.init() # Инициация PyGame, обязательная строчка
CHARACTERS = pygame.sprite.Group()
PLATFORMS = pygame.sprite.Group()
BACKS = pygame.sprite.Group()

info_object = pygame.display.Info() # Объект с информацией о графической среде компьютера
WIN_WIDTH = info_object.current_w # Ширина главного создаваемого окна
WIN_HEIGHT = info_object.current_h # Высота
WINDOW = (WIN_WIDTH, WIN_HEIGHT) # Заносим ширину и высоту в одну переменную
HALF_WINDOW = (WIN_WIDTH//2, WIN_HEIGHT//2)

FPS = 60
G = 1 # Ускорение свободного падения

# Базовый класс, используемый подвижными и неподвижными, проходимыми и непроходимыми объектами
class GameObject(pygame.sprite.Sprite):
	# img - путь к файлу с изображением объекта
	# x, y - координаты объекта на игровом поле
	# stable - устойчивый ли объект
	def __init__(self, img, x, y, stable):
		pygame.sprite.Sprite.__init__(self)
		self.image = img.convert() # pytmx передает Surface при считывании карты
		self.x = x
		self.y = y
		self.width, self.height = self.image.get_size()
		self.rect = Rect(x, y, self.width, self.height)
	
	# scr - поверхность для отрисовки
	# dx, dy - смещение рисунка от действительного положения
	def draw(self, scr, dx = 0, dy = 0):
		x = self.x + dx
		y = self.y + dy
		coords = (x, y)
		scr.blit(self.image, coords)

# Платформы
class Platform(GameObject):
	# x, y - координаты объекта на игровом поле
	# stable - устойчивый ли объект
	def __init__(self, img, x, y, stable = True):
		global PLATFORMS
		
		super().__init__(img, x, y, stable)
		
		if stable:
			PLATFORMS.add(self)
		else:
			BACKS.add(self)

# Персонаж
class Character(GameObject):
	# x, y - координаты объекта на игровом поле
	# folder - папка с картинками для анимации
	def __init__(self, img, x, y, folder, power, v_lim, jump_power, stable = True):
		global CHARACTERS
		global FPS
		
		self.right_standing = img.convert_alpha()
		self.left_standing = pygame.transform.flip(self.right_standing, True, False)
		# FIXME: Стойку тоже нужно анимировать
		super().__init__(img, x, y, stable)
		
		self.on_ground = self.left = self.right = self.down = self.up = self.jumping = False
		
		self.v_x = 0
		self.v_y = 0
		
		self.power = power # Ускорение при беге 
		self.v_lim = v_lim # Предельная скорость
		self.jump_power = jump_power # Сила прыжка (в единицах G)
		
		self.direction = 'right'
		
		CHARACTERS.add(self)
		
		animTypes = 'jump roll run'.split()
		self.animObjs = {}
		
		for animType in animTypes:
			animType_r = 'right_' + animType
			animType_l = 'left_' + animType
			path = './resources/characters/%s/%s/' % (folder, animType_r)
			files = os.listdir(path)
			num_files = 0
			for file in files:
				if file[-4:] == '.png': # В папке могут содержаться скрытые системные файлы, например, Thumbs.db
					num_files += 1
					
			imagesAndDurations = [(path + str(num) + '.png', 60) for num in range(1, num_files + 1)]
			# FIXME: Какое нужно время между кадрами?
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
		elif not(self.left or self.right):
			self.v_x = 0
			'''and self.v_x != 0:
			self.v_x += math.copysign(self.power, -self.v_x) # Замедление при остановке
			if abs(self.v_x) <= self.power:
				self.v_x = 0'''
			
		
		if self.up and self.on_ground:
			self.v_y = -self.jump_power*G
		
		if not self.on_ground:
			self.v_y += G
		self.on_ground = False
		self.rect.x += self.v_x
		self.rect.y += self.v_y
	
	# Отвечает за анимацию
	# scr - поверхность для отрисовки
	# dx, dy - смещение рисунка от действительного положения
	def draw(self, scr, dx, dy):	
		x = self.rect.x + dx
		y = self.rect.y + dy
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

class Hero(Character):
	def __init__(self, x, y, folder = 'hero'):
		img_path = './resources/characters/hero/stand/1.png'
		img = pygame.image.load(img_path)
		self.width, self.height = img.get_size()
		self.power = 2*self.height/FPS # Ускорение при беге. 
		self.v_lim = 12*self.height/FPS # Предельная скорость 
		# Скорость [высот/тик] = [высот/с] / [тик/с]
		super().__init__(img, x, y, folder)
		
# Реализация скроллинга
class Camera():
	# level_width, level_height - размеры игрового поля
	def __init__(self, level_width, level_height):
		global WINDOW
		
		self.max_dx = level_width - WINDOW[0]
		self.max_dy = level_height - WINDOW[1]

	# Возвращает смещение для методов draw
	# target - за кем следует камера
	def update(self, target):
		global HALF_WINDOW
		
		x, y, _, _ = target.rect
		dx, dy = x - HALF_WINDOW[0], y - HALF_WINDOW[1] 
		# Куда и в каком направлении сместилась цель относительно точки (HALF_WIDTH, HALF_HEIGHT)

		if dx < 0:
			dx = 0
			# Когда смещение цели отрицательно, в сторону левой границы, не смещать поле
		elif dx > self.max_dx:
			dx = self.max_dx
			# Когда в сторону правой границы
		if dy < 0:
			dy = 0
			# В сторону верхней
		elif dy > self.max_dy:
			dy = self.max_dy
			# К нижней
		
		# Вернуть смещение объектов для отрисовки (оно противоположно по направлению смещению героя)
		return -dx, -dy
		# Сами объекты не смещаются
		# TODO: отдаление камеры при ускорении для повышения реакции

# Создает фон по размерам поверхности, используя за основу изображение меньшего размера
# scr - поверхность для отрисовки
# base_back_path - путь к используемому изображению
def create_background(scr, base_back_path):
	base_back = pygame.image.load(base_back_path) # Загружаем изображение
	base_back = base_back.convert() # Для ускорения отрисовки
	
	base_img_width, base_img_height = base_back.get_size() # get_size() - метод Surface
	img_width, img_height = scr.get_size()
	ratio_width = math.ceil(img_width/base_img_width)
	ratio_height = math.ceil(img_height/base_img_height)
	for h in range(ratio_height):
		for w in range(ratio_width):
			# Второй аргумент blit() - координаты левого верхнего края изображения
			# относительно того же края экрана
			scr.blit(base_back, (base_img_width*w, base_img_height*h))
	return scr.copy()

# Рисует фон
# scr - поверхность для отрисовки
# img - фоновая картинка. Если отсутствует, осуществляется заливка серым фоном
def draw_background(scr, img = None):
	if img:
		scr.blit(img, (0, 0))
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
					else: #	Если влево (0 быть не может, иначе столкновение произошло 
						# не из-за горизонтального движения)
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

# Загружает уровень, возвращает объект под управление и размеры уровня
def load_level(name):
	tiled_map = pytmx.util_pygame.load_pygame('./maps/%s.tmx' % name)
	lvl_width = tiled_map.tilewidth * tiled_map.width
	lvl_height = tiled_map.tileheight * tiled_map.height
	
	back_lay = tiled_map.layers[0]
	plate_lay = tiled_map.layers[1]
	char_lay = tiled_map.layers[2]
	
	# Создаем устойчивые платформы
	for x, y, img in plate_lay.tiles():
		x_pix = x * tiled_map.tilewidth
		y_pix = y *	tiled_map.tileheight
		Platform(img, x_pix, y_pix)
	# Создаем неустойчивые платформы
	for x, y, img in back_lay.tiles():
		x_pix = x *	tiled_map.tilewidth
		y_pix = y *	tiled_map.tileheight
		Platform(img, x_pix, y_pix, False)
	# Заселяем персонажами
	for char in char_lay:
		power = float(char.power)
		v_lim = float(char.v_lim)
		jump_power = float(char.jump_power)
		character = Character(char.image, char.x, char.y, char.name, power, v_lim, jump_power)
		if char.name == 'hero':
			hero = character
	return hero, lvl_width, lvl_height
	
def main():
	global FPS
	global CHARACTERS
	global PLATFORMS
	global BACKS
	global WINDOW
	
	# Создаем окно
	screen = pygame.display.set_mode(WINDOW, pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF) 
	pygame.display.set_caption("Platformer") # Задаем заголовок окна
	# Создаем фон
	base_background = "./resources/backgrounds/background.png"
	background = create_background(screen, base_background) # return Surface
	# Загружаем карту
	hero, lvl_width, lvl_height = load_level('test3')
	
	camera = Camera(lvl_width, lvl_height)
	
	'''objects = pygame.sprite.Group()
	objects.add(CHARACTERS)
	objects.add(PLATFORMS)
	objects.add(BACKS)
	sprites = objects.sprites()'''
	
	Clock = pygame.time.Clock()
	
	text_font = pygame.font.Font('freesansbold.ttf', 16)

# В бесконечном цикле принимаем и обрабатываем сообщения
	while 1:
		process_events(pygame.event.get(), hero)
		
		hero.update()
		collide(CHARACTERS, PLATFORMS)
		dx, dy = camera.update(hero)
		
		draw_background(screen, background) # Фон перерисовывается поверх устаревших положений персонажей
		for back in BACKS.sprites():
			back.draw(screen, dx, dy)
		for plate in PLATFORMS.sprites():
			plate.draw(screen, dx, dy)
		for char in CHARACTERS.sprites():
			char.draw(screen, dx, dy)
		
		tick = Clock.tick(FPS)
		print_info(screen, text_font, tick/1000, 1, hero)
		
		pygame.display.update() # Обновление экрана

# Если этот файл импортируется в другой, этот __name__ равен имени импортируемого файла 
# без пути и расширения ('main'). Если файл запускается непосредственно, __name__  
# принимает значенние __main__
if __name__ == "__main__":
	main()