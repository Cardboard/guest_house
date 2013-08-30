import os

import pygame

class View:
    def __init__(self, path, filename, objects={}):
	self.visited = False
	self.objects = objects
	self.image = pygame.image.load(os.path.join(path, filename)).convert()
	self.rect = self.image.get_rect()

    def draw(self, screen):
	# draw view first, then objects
	screen.blit(self.image, self.rect)
	examining = None # always draw object being examined on top of all other objects
	for obj in self.objects:
	    obj = self.objects[obj] # get object by getting value at objects[key]
	    # don't draw if object dies and is dead.
	    # broken and dead objects still get drawn.
	    if obj.dies and obj.dead:
		pass
	    else:
		if obj.parent == None:
		    if obj.examine and obj.activated:
			examining = [obj.image, obj.rect_on]
		    else:
			screen.blit(obj.image, (obj.x, obj.y))
		elif obj.parent != None:
		    if self.check_parents(obj):
			if obj.examine and obj.activated:
			    examining = [obj.image, obj.rect_on]
			else:
			    screen.blit(obj.image, (obj.x, obj.y))
	    pygame.draw.rect(screen, (255,21,22, 10), obj.rect)
	    #pygame.draw.rect(screen, (25,155,22), pygame.Rect(obj.x, obj.y, 10, 10))
	if examining:
	    screen.blit(examining[0], examining[1])
    
    def click_check(self, mpos):
	returned_object = None
	for obj in self.objects: # check objects closest to player first
	    obj = self.objects[obj] # get object by getting value at objects[key]
	    # mouse clicked on object
	    if obj.rect.collidepoint(mpos):
		# object is still able to be activated/deactivated
		if not(obj.dead):
		    if obj.parent == None:
			if obj.examine and obj.activated:
			    returned_object = obj
			# only return the object if an examined object hasn't been found
			elif returned_object == None:
			    returned_object = obj
		    elif obj.parent != None:
			if self.check_parents(obj):
			    if obj.examine and obj.activated:
				returned_object = obj
			    elif returned_object == None:
				returned_object = obj
		    else:
			return None
	return returned_object
	
    def check_parents(self, obj):
	validates = True
	if obj.parent == None and obj.antiparent == None:
	    return True
	if obj.parent != None:
	    for parent in obj.parent:
		if not(self.objects[parent].activated):
		    validates = False
	if obj.antiparent != None:
	    # if any antiparents are activated, validation fails
	    for antiparent in obj.antiparent:
		if self.objects[antiparent].activated:
		    validates = False
	return validates
