import os

import pygame

class Object:
	def __init__(self, name, x, y, image_off, image_on, rect_off, rect_on, layer=0,\
		activated=False, examine=False, breaks=False, dies=False, message="", response="",\
		info=False, speed=None, loop=True):
		self.name = name
		self.x = x
		self.y = y 
		if type(image_off) == list: # object is animated!
			image_list = []
			for image in image_off:
				image_list.append(pygame.image.load(image).convert_alpha())
			self.image_off = image_list
		else: 
			self.image_off = pygame.image.load(image_off).convert_alpha()
		if type(image_on) == list:
			image_list = []
			for image in image_on:
				image_list.append(pygame.image.load(image).convert_alpha())
			self.image_on = image_list
		else:
			self.image_on = pygame.image.load(image_on).convert_alpha()
		self.rect_off = pygame.Rect(rect_off)
		if rect_on == 'full':
			surface = pygame.display.get_surface()
			self.rect_on = pygame.Rect(0, 0, surface.get_width(), surface.get_height())
		else:
			self.rect_on = pygame.Rect(rect_on)
		self.activated = activated
		if self.activated:
			self.image = self.image_on
			self.rect = self.rect_on
		else:
			self.image = self.image_off
			self.rect = self.rect_off
		self.layer = layer # determines when the object is drawn, lower numbers drawn first (0-9)
		self.examine = examine # if examine is true, object deactivates when view changes
		self.breaks = breaks # determines if can only be activated/deactivated once
		self.dies = dies # determines if object disappears after being activated/deactivated
		self.dead = False # once dead, cannot be activated/deactivated again
		self.message = message
		self.response = response
		self.info = info
		# set after initialization
		self.parents = None
		self.antiparents = None
		self.breakparent = False # if true, doesn't deactivate after activating then deactivating parents
		self.door = None # is a door
		self.info = info # object is only for information; it never gets activated
		# sound stuff
		self.sound_on = None
		self.sound_off = None
		# animation stuff
		self.frame = 0
		self.clock = speed
		self.speed = speed
		self.loop = loop
		self.stop_anim = False # True when animation is over and loop=False

	# toggle image and rect between activated and deactivated
	def toggle(self, sounds):
		if not(self.dead):
			if self.stop_anim == True:
			    self.stop_anim = False
			if self.activated:
				self.rect = self.rect_off
				self.activated = False
				self.frame = 0
				self.clock = self.speed
				if self.sound_off: # object has sound for deactivation
					sounds[self.sound_off].play()
			elif not(self.activated):
				if self.info or self.door != None:
					# don't change activation state or rect
					# of doors and info objects
					pass
				else:
					self.rect = self.rect_on
					self.activated = True
					self.frame = 0
					self.clock = self.speed
				if self.sound_on: # object has sound for activation
					sounds[self.sound_on].play()      
			# kill it if it should be killed
			if self.breaks or self.dies:
				self.dead = True

	def set_image(self, dt):
		if self.activated:
			# object is animated
			if type(self.image_on) == list:
				if not(self.stop_anim):
					# add dt to objects clock
					self.clock -= dt
					# increment frame and reset clock
					if self.clock < 0.0:
						self.frame += 1
						self.clock = self.speed
						# if frame > # frames, set back to 0
						if self.frame >= len(self.image_on):
						    if self.loop:
							self.frame = 0
						    else:
							self.frame = len(self.image_on)-1
							self.stop_anim = True
						    
					# set image to appropriate image
					self.image = self.image_on[self.frame]
			else:
				self.image = self.image_on
		else:
			# object is animated
			if type(self.image_off) == list:
				if not(self.stop_anim):
					# add dt to objects clock
					self.clock -= dt
					# increment frame and reset clock
					if self.clock < 0.0:
						self.frame += 1
						self.clock = self.speed
						# if frame > # frames, set back to 0
						if self.frame >= len(self.image_off):
						    if self.loop:
							self.frame = 0
						    else:
							self.frame = len(self.image_off)-1
							self.stop_anim = True
					# set image to appropriate image
					self.image = self.image_off[self.frame]
			else:
				self.image = self.image_off

