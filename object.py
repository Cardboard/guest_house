import os

import pygame

class Object:
    def __init__(self, name, path, x, y, image_off, image_on, rect_off, rect_on,\
	    activated=False, examine=False, breaks=False, dies=False, message=""):
	self.name = name
	self.x = x
	self.y = y 
	self.image_off = pygame.image.load(os.path.join(path, image_off)).convert_alpha()
	self.image_on = pygame.image.load(os.path.join(path, image_on)).convert_alpha()
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
	self.examine = examine # if examine is true, object deactivates when view changes
	self.breaks = breaks # determines if can only be activated/deactivated once
	self.dies = dies # determines if object disappears after being activated/deactivated
	self.dead = False # once dead, cannot be activated/deactivated again
	self.message = message
	# set after initialization
	self.parent = None
	self.antiparent = None
	self.door = None

    # toggle image and rect between activated and deactivated
    def toggle(self):
	if not(self.dead):
	    if self.activated:
		self.image = self.image_off
		self.rect = self.rect_off
		self.activated = False
	    elif not(self.activated):
		self.image = self.image_on
		self.rect = self.rect_on
		self.activated = True
	    # kill it if it should be killed
	    if self.breaks or self.dies:
		self.dead = True
