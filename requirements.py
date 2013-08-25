import os

import pygame

class Requirements:
    def __init__(self):
	self.req_dict = {}
	self.sounds = {}
	self.sound_reqs = []
	
    def add_req(self, obj, reqs, antireqs=None):
	self.req_dict[obj.name] = []
	for req in reqs:
	    self.req_dict[obj.name].append(req)
	if antireqs != None:
	    self.req_dict[obj.name+'_anti'] = []
	    for anti in antireqs:
		self.req_dict[obj.name+'_anti'].append(anti)

    def req_check(self, obj, objects):
	validates = True # gets set to false on unsatisfied requirement
	try:
	    for req in self.req_dict[obj.name]:
		if req.activated:
		    pass # everything is A-ok, captain!
		else:
		    validates = False
	# object has no requirements
	except KeyError:
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
    
    def add_sound(self, path, filename, view, reqs, volume=1.0):
	if filename in self.sounds:
	    # sound has already been created
	    pass
	else:
	    sound = os.path.join(path, filename)
	    sound = pygame.mixer.Sound(sound)
	    sound.set_volume(volume)
	    self.sounds[filename] = sound
	self.sound_reqs.append({'name': filename,
				'view': view,
				'reqs': reqs,
				'triggered': False})

    def sound_check(self, view):
	# check = {'name', 'reqs', 'triggered'}
	for check in self.sound_reqs:
	    validates = True
	    if check['view'] != view:
		validates = False
	    for obj in view.objects:
		# the object is in the sound's reqs
		if obj in check['reqs']:
		    # the sound is not activated
		    if not(obj.activated):
			if check['triggered'] == True:
			    check['triggered'] = False 
			    self.sounds[check['name']].play()
			validates = False
	    # reqs are activated and sound hasn't been triggered
	    if validates and check['triggered'] == False:
		self.sounds[check['name']].play()
		check['triggered'] = True


