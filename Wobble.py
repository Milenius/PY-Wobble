import pygame
from pygame.locals import *
import numpy as np

room_width = 1920
room_height = 1080

input_layer_neurons = 2
hidden_layer_neurons = 4
output_layer_neurons = 2

wobble_amount = 75
food_amount = 50

gameObjects = []
newWobbles = []

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

	health = 300
	speed = 2
	direction = 45
	size = 10				#Radius in Pixel (glaube ich)


	#Initialisierung (create_Event) || Konstruktor
	def __init__(self,x,y,syn0,syn1):
		gameObjects.append(self)
		
		self.syn0 = syn0
		self.syn1 = syn1
		
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
	
	#Draw Event. Grafik darstellung 
	def draw_event(self):
		#Yay Grafik
		pygame.draw.circle(screen,((0,0,255)),(int(self.x),int(self.y)),self.size)

	#Step Event. Der Code in dieser Methode wird in jedem Frame für dieses Objekt ausgeführt
	def step_event(self):
		
		self.direction = self.direction%360
		
		self.shortest_distance = np.inf
		for obj in foods:
			self.cur_distance = np.sqrt(np.square(self.x - obj.x) + np.square(self.y - obj.y))
			if self.cur_distance < self.shortest_distance:
				self.shortest_distance = self.cur_distance
				self.nearest_food = obj
		
		self.nearest_food_dir = int(np.degrees(np.arctan((obj.x - self.x) / ((obj.y - self.y)+0.00001))))%360
		
		if self.nearest_food_dir > self.direction:
			self.senses = np.array([1,1])
			
		if self.nearest_food_dir < self.direction:
			self.senses = np.array([-1,1])

		
		self.l0 = self.senses
		self.l1 = np.tanh(np.dot(self.l0, self.syn0))   
		self.l2 = np.tanh(np.dot(self.l1, self.syn1)) 
	
		
		if self.l2[0] > 0:
			self.direction += 5
		else:
			self.direction -= 5
		
		for obj in foods:
			if ( (self.x >= (obj.x - self.size)) and (self.x <= (obj.x + self.size)) ) and ( (self.y >= (obj.y -self.size)) and (self.y <= (obj.y +self.size)) ):
				self.health += obj.food_points
				obj.instance_destroy()


		self.health -= 1
		self.movement()

		if self.health <= 0:
			self.instance_destroy()
			pass


#Spawnt Wobbles einmalig in bestimmter Menge
def wobble_spawner(amount):
	wobbles = []
	for i in range(amount):
		wobbles.append(wobble(np.random.randint(room_width),np.random.randint(room_height),2*np.random.random((input_layer_neurons,hidden_layer_neurons)) - 1,2*np.random.random((hidden_layer_neurons,output_layer_neurons)) - 1))

	return wobbles

#Spawnt Essen
def food_spawner(amount):
	foods = []
	for i in range(amount):
		foods.append(food(np.random.randint(room_width),np.random.randint(room_height)))
	return foods
	

wobbles = wobble_spawner(wobble_amount)
foods = food_spawner(food_amount)

while True:
	for event in pygame.event.get():
		if event.type == QUIT:
			quit()
	screen.fill((220,220,220))

	if (len(wobbles) < 5) and (len(wobbles) != 0):
		for obj in wobbles:
			for i in range(int(wobble_amount/5)):

				new_syn0 = obj.syn0
				if np.random.randint(10) == 1:
					new_syn0[np.random.randint(new_syn0.shape[0]),np.random.randint(new_syn0.shape[1])] = 2*np.random.random_sample() - 1

				new_syn1 = obj.syn1
				if np.random.randint(10) == 1:
					new_syn1[np.random.randint(new_syn1.shape[0]),np.random.randint(new_syn1.shape[1])] = 2*np.random.random_sample() - 1

				newWobbles.append(wobble(np.random.randint(room_width),np.random.randint(room_height),new_syn0,new_syn1))
		wobbles = wobbles + newWobbles
		newWobbles = []
		

	if len(wobbles) == 0:
		wobble_spawner(wobble_amount)
	
	if len(foods) != food_amount:
		foods.append(food(np.random.randint(room_width),np.random.randint(room_height)))

	for obj in gameObjects:
		obj.step_event()
		obj.draw_event()

	clock.tick(60)
	pygame.display.update()

