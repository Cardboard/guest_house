import os

import pygame

class Requirements:
    def __init__(self):
	self.req_dict = {}
	self.sounds = {}
	self.sound_reqs = []
	
    def add_req(self, obj_name, reqs, antireqs=None):
	self.req_dict[obj_name] = []
	for req in reqs:
	    self.req_dict[obj_name].append(req)
	if antireqs != None:
	    self.req_dict[obj_name+'_anti'] = []
	    for anti in antireqs:
		self.req_dict[obj_name+'_anti'].append(anti)

    def req_check(self, obj, rooms):
	validates = True # gets set to false on unsatisfied requirement
	try:
	    for req in self.req_dict[obj.name]:
		print('*'*10)
		print('CHECKING {}'.format(obj.name))
		print(self.req_dict)
		print(req)
		for room in rooms:
		    for view in rooms[room]:
			try:
			    req = rooms[room][view]['view'].objects[req]
			    if req.activated:
				print('req activated', req.name)
				pass # everything is A-ok, captain!
			    else:
				print('req not activated', req.name)
				validates = False
			except KeyError:
			    pass
	except KeyError: # object has no reqs/antireqs
	    pass
	if validates:
	    try:
		for anti in self.req_dict[obj.name+'_anti']:
		    if anti.activated:
			validates = False
		    else:
			pass # nothing activated that shouldn't be. yaay!
	    # object has no antirequirements
	    except KeyError:
		pass
	if validates:
	    return (obj, False)
	else:
	    return (obj, True)
    
    def add_sound(self, path, filename, volume=1.0):
	if filename in self.sounds:
	    # sound has already been created
	    pass
	else:
	    sound = os.path.join(path, filename)
	    sound = pygame.mixer.Sound(sound)
	    sound.set_volume(volume)
	    self.sounds[filename] = sound
