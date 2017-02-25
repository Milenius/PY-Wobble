import pygame
from pygame.locals import *
import numpy as np

room_width = 1600
room_height = 900

gameObjects = []

pygame.init()
screen=pygame.display.set_mode((room_width,room_height))

clock = pygame.time.Clock()

class food:
	obj_list_index = None

	size = 5
	food_points = 100

	#Initialisierung (create_Event) || Konstruktor
	def __init__(self,x,y):
		gameObjects.append(self)
		self.x = x
		self.y = y

	def instance_destroy(self):
		gameObjects.remove(self)
		foods.remove(self)

	#Draw Event. Grafik darstellung 
	def draw_event(self):
		#Yay Grafik
		pygame.draw.circle(screen,((0,255,0)),(int(self.x),int(self.y)),self.size)

	#Step Event. Der Code in dieser Methode wird in jedem Frame für dieses Objekt ausgeführt (LEER)
	def step_event(self):
		#
		pass

#Wobble Class
class wobble:
	obj_list_index = None

	lifespan = 150
	speed = 2
	direction = 45
	size = 10				#Radius in Pixel (glaube ich)

	#Initialisierung (create_Event) || Konstruktor
	def __init__(self,x,y):
		gameObjects.append(self)
		self.x = x
		self.y = y		

	#Bewegungsberechnung anhand Geschwindigkeit und Rotation
	def movement(self):
		self.x += np.cos(np.radians(self.direction))*self.speed
		self.y += np.sin(np.radians(self.direction))*self.speed

		if self.x > room_width:
			self.x = 0
		if self.y > room_height:
			self.y = 0
		if self.x < 0:
			self.x = room_width
		if self.y < 0:
			self.y = room_height

	def instance_destroy(self):
		gameObjects.remove(self)
		wobbles.remove(self)
		print(gameObjects)
		print(wobbles)
	
	#Draw Event. Grafik darstellung 
	def draw_event(self):
		#Yay Grafik
		pygame.draw.circle(screen,((0,0,255)),(int(self.x),int(self.y)),self.size)

	#Step Event. Der Code in dieser Methode wird in jedem Frame für dieses Objekt ausgeführt
	def step_event(self):

		if np.random.randint(2) > 0:
			self.direction += 5
		else:
			self.direction -= 5
		

		self.lifespan -= 1
		self.movement()

		if self.lifespan <= 0:
			self.instance_destroy()
			pass

#Spawnt Wobbles einmalig in bestimmter Menge
def wobble_spawner(amount):
	wobbles = []
	for i in range(amount):
		wobbles.append(wobble(np.random.randint(room_width),np.random.randint(room_height)))

	return wobbles

#Spawnt Essen
def food_spawner(amount):
	foods = []
	for i in range(amount):
		foods.append(food(np.random.randint(room_width),np.random.randint(room_height)))
	return foods

wobbles = wobble_spawner(2)
foods = food_spawner(0)

while True:
	for event in pygame.event.get():
		if event.type == QUIT:
			quit()
	screen.fill((220,220,220))

	for obj in gameObjects:
		obj.step_event()
		obj.draw_event()

	clock.tick(60)
	pygame.display.update()

