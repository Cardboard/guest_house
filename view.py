import os

import pygame

class View:
	def __init__(self, path, filename, objects={}):
		self.visited = False
		self.objects = objects
		self.image = pygame.image.load(os.path.join(path, filename)).convert()
		self.rect = self.image.get_rect()

	def draw(self, screen, dt):
		queue = {'0':[],'1':[],'2':[],'3':[],'4':[],'5':[],'6':[],'7':[],'8':[],'9':[]}
		# draw view first, then objects
		screen.blit(self.image, self.rect)
		examining = None # always draw object being examined on top of all other objects
		for obj in self.objects:
			obj = self.objects[obj] # get object by getting value at objects[key]
			obj.set_image(dt)
			# don't draw if object dies and is dead.
			# broken and dead objects still get drawn.
			if obj.dies and obj.dead:
				pass
			else:
				if obj.parents == None:
					if obj.examine and obj.activated:
						examining = [obj.image, obj.rect_on]
					else:
						#screen.blit(obj.image, (obj.x, obj.y))
						queue[str(obj.layer)].append((obj.image, (obj.x, obj.y)))
				elif obj.parents != None:
					if self.check_parents(obj):
						if obj.examine and obj.activated:
							examining = [obj.image, obj.rect_on]
						else:
						#screen.blit(obj.image, (obj.x, obj.y))
							queue[str(obj.layer)].append((obj.image, (obj.x, obj.y)))
			#pygame.draw.rect(screen, (255,21,22, 10), obj.rect)
			#pygame.draw.rect(screen, (25,155,22), pygame.Rect(obj.x, obj.y, 10, 10))
		# Print objects in queue in order of layers.
		# Lower numbers drawn first (0-9)
		for number in range(0, 10):
			if queue[str(number)] != []:
				for i in queue[str(number)]:
					screen.blit(i[0], i[1])

		if examining:
			screen.blit(examining[0], examining[1])
	
	def click_check(self, mpos):
		returned_object = None
		possible_object = None
		queue = {'0':None,'1':None,'2':None,'3':None,'4':None,'5':None,'6':None,'7':None,'8':None,'9':None}
		for obj in self.objects: # check objects closest to player first
			obj = self.objects[obj] # get object by getting value at objects[key]
			# mouse clicked on object
			if obj.rect.collidepoint(mpos):
				# object is still able to be activated/deactivated
				if not(obj.dead):
					if obj.parents == None:
						if obj.examine and obj.activated:
							possible_object = obj
						# only return the object if an examined object hasn't been found
						elif possible_object == None:
							possible_object = obj
					elif obj.parents != None:
						if self.check_parents(obj):
							if obj.examine and obj.activated:
								possible_object = obj
							elif possible_object == None:
								possible_object = obj
					else:
						return None
				queue[str(obj.layer)] = possible_object
				possible_object = None
		for number in range(0, 10):
			if queue[str(number)] != None:
				returned_object = queue[str(number)]

		return returned_object
	
	def check_parents(self, obj):
		validates = True
		if obj.parents == None and obj.antiparents == None:
			return True
		if obj.parents != None:
			for parent in obj.parents:
				if not(self.objects[parent].activated):
					validates = False
		if obj.antiparents != None:
			# if any antiparents are activated, validation fails
			for antiparent in obj.antiparents:
				if self.objects[antiparent].activated:
					validates = False
		return validates