import os

import pygame

class Object:
    def __init__(self, name, x, y, image_off, image_on, rect_off, rect_on, layer=0,\
	    activated=False, examine=False, breaks=False, dies=False, message=""):
	self.name = name
	self.x = x
	self.y = y 
	self.image_off = pygame.image.load(image_off).convert_alpha()
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
	# set after initialization
	self.parents = None
	self.antiparents = None
	self.breakparent = False # if true, doesn't deactivate after activating then deactivating parents
	self.door = None
	# sound stuff
	self.sound_on = None
	self.sound_off = None

    # toggle image and rect between activated and deactivated
    def toggle(self, sounds):
	if not(self.dead):
	    if self.activated:
		self.image = self.image_off
		self.rect = self.rect_off
		self.activated = False
		if self.sound_on: # object has sound for activation
		    sounds[self.sound_off].play()
	    elif not(self.activated):
		self.image = self.image_on
		self.rect = self.rect_on
		self.activated = True
		if self.sound_off: # object has sound for deactivation
		    sounds[self.sound_off].play()
		if self.door != None:
		    self.image = self.image_off
		    self.activated = False
	    # kill it if it should be killed
	    if self.breaks or self.dies:
		self.dead = True
