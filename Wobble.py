﻿import pygame
from pygame.locals import *
import numpy as np
import sys
import time
import matplotlib.pyplot as plt

if len(sys.argv) > 1:
	if sys.argv[1] == 'nogui':	
		print("Gui Dissabled.")
		build_gui = False
else:
	print("No Valid Args passed.")
	build_gui = True

room_width = int(1920)
room_height = int(1080)

input_layer_neurons = 2
hidden_layer_neurons = 2
output_layer_neurons = 1

wobble_amount = 200	
food_amount = 150

gameObjects = []
newWobbles = []

plt.ion()

pygame.init()
if build_gui == True: screen=pygame.display.set_mode((room_width,room_height))	#Turn this off for no GUI

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

		self.pos = np.array([self.x,self.y])

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

		self.pos = np.array([self.x,self.y])		

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
		
		self.food_pos_deltas = np.asarray([obj.pos for obj in foods]) - self.pos
		self.nearest_food = foods[np.argmin(np.einsum('ij,ij->i',self.food_pos_deltas,self.food_pos_deltas))]
		
		self.nearest_food_dir = int(np.degrees(np.arctan((self.nearest_food.x - self.x) / ((self.nearest_food.y - self.y)+0.00001))))%360
		self.nearest_food_dis = np.sqrt( (self.nearest_food.x - self.x)**2 + (self.nearest_food.y - self.y)**2 )
		
		if self.nearest_food_dir > self.direction:
			self.senses = np.array([self.nearest_food_dir,1])
		else:
			self.senses = np.array([-self.nearest_food_dir,1])
		
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
		wobbles.append(wobble(np.random.randint(room_width),np.random.randint(room_height),4*np.random.random((input_layer_neurons,hidden_layer_neurons)) - 2,4*np.random.random((hidden_layer_neurons,output_layer_neurons)) - 2))

	return wobbles

#Spawnt Essen
def food_spawner(amount):
	foods = []
	for i in range(amount):
		foods.append(food(np.random.randint(room_width),np.random.randint(room_height)))
	return foods

def set_newgen_stats():

	global gen_survival_ticks
	global gen_survival_ticks_list 
	global gen_eaten_foods
	global gen_eaten_foods_list 
	global gen_real_fitness
	global gen_real_fitness_list

	gen_real_fitness = int((gen_eaten_foods*gen_survival_ticks)*0.001)

	gen_survival_ticks_list.append(gen_survival_ticks)
	print("This Gen_Ticks   : "+str(gen_survival_ticks))
	gen_survival_ticks = 0

	gen_eaten_foods_list.append(gen_eaten_foods)
	print("This Gen_Foods   : "+str(gen_eaten_foods))
	gen_eaten_foods = 0
	
	gen_real_fitness_list.append(gen_real_fitness)
	print("This Real_Fitness: "+str(gen_real_fitness))
	gen_real_fitness = 0
	
	

	print("Gen_Ticks_List  : "+str(gen_survival_ticks_list))
	print("Gen_Foods_List  : "+str(gen_eaten_foods_list))
	print("Gen_Real_F_List : "+str(gen_real_fitness_list))

	plt.clf()
	plt.plot(gen_survival_ticks_list,label='Survival Ticks')
	plt.plot(gen_eaten_foods_list,label='Eaten Foods')
	plt.plot(gen_real_fitness_list,label='Real Fitness')

	plt.xlabel('Generation')
	plt.ylabel('Stats')
	plt.title('Py-Wobble Data')
	plt.legend()
	plt.show()


frame = 0
cur_fps = 0
cur_fps_list = []
cur_fps_median = 0
frame_delta_time = 0
frame_delta_time_list = []
frame_delta_time_median = 0

gen_survival_ticks = 0
gen_survival_ticks_list = []
gen_eaten_foods = 0
gen_eaten_foods_list = []
gen_real_fitness = 0 			#ticks*eaten_food
gen_real_fitness_list = []

wobbles = wobble_spawner(wobble_amount)
foods = food_spawner(food_amount)

while True:

	t = time.time()

	for event in pygame.event.get():
		if event.type == QUIT:
			quit()
	if build_gui == True: screen.fill((220,220,220))			#Turn this off for no GUI
	
	if (len(wobbles) < 50) and (len(wobbles) != 0):
		for obj in wobbles:
			for i in range(int(wobble_amount/50)):

				new_syn0 = obj.syn0
				if np.random.randint(10) == 1:
					new_syn0[np.random.randint(new_syn0.shape[0]),np.random.randint(new_syn0.shape[1])] = 4*np.random.random_sample() - 2

				new_syn1 = obj.syn1
				if np.random.randint(10) == 1:
					new_syn1[np.random.randint(new_syn1.shape[0]),np.random.randint(new_syn1.shape[1])] = 4*np.random.random_sample() - 2

				newWobbles.append(wobble(np.random.randint(room_width),np.random.randint(room_height),new_syn0,new_syn1))
		set_newgen_stats()

		wobbles = wobbles + newWobbles
		newWobbles = []

	if len(wobbles) == 0:
		wobble_spawner(wobble_amount)
		
		set_newgen_stats()
	
	if len(foods) != food_amount:
		gen_eaten_foods += 1
		foods.append(food(np.random.randint(room_width),np.random.randint(room_height)))

	"""
	for obj in gameObjects:
		obj.step_event()
		if build_gui == True: obj.draw_event()			#Turn this off for no GUI
	"""

	gen_survival_ticks += 1

	[obj.step_event() for obj in gameObjects]
	if build_gui == True: [obj.draw_event() for obj in gameObjects]
	
	print(wobbles[0].l2)
	
	#clock.tick(60)				#Turn this off for no Frame Limit
	if build_gui == True: pygame.display.update()		#Turn this off for no GUI
	"""
	frame += 1
	frame_delta_time = time.time()-t
	cur_fps = int(1/frame_delta_time+1)
	frame_delta_time_list.append(frame_delta_time) 
	cur_fps_list.append(cur_fps)
	frame_delta_time_median = np.median(frame_delta_time_list)
	cur_fps_median = np.median(cur_fps_list)
	"""

	