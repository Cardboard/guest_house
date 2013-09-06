import os

import pygame

class Requirements:
	def __init__(self):
		self.req_dict = {}
		self.antireq_dict = {}
		self.sounds = {}
		self.sound_reqs = []
	
	def add_req(self, obj_name, reqs, antireqs=None):
		self.req_dict[obj_name] = []
		self.antireq_dict[obj_name] = []
		for req in reqs:
			self.req_dict[obj_name].append(req)
		if antireqs != None:
			for anti in antireqs:
				self.antireq_dict[obj_name].append(anti)

	def req_check(self, obj, rooms):
		validates = True # gets set to false on unsatisfied requirement
		try:
			for req in self.req_dict[obj.name]:
				for room in rooms:
					for view in rooms[room]:
						try:
							req = rooms[room][view]['view'].objects[req]
							if req.activated:
								pass # everything is A-ok, captain!
							else:
								validates = False
						except KeyError:
							pass
		except KeyError: # object has no reqs/antireqs
			pass
		if validates:
			try:
				for anti in self.antireq_dict[obj.name]:
					for room in rooms:
						for view in rooms[room]:
							try:
								anti = rooms[room][view]['view'].objects[anti]
								if anti.activated:
									validates = False
								else:
									pass # nothing activated that shouldn't be. yaay!
							except KeyError:
								pass
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
