import sys
import os
import json

import pygame

import room
import view
import object as object_
import requirements

class Game:

    def __init__(self, width=800, height=600, caption="Adventure Game"):
	pygame.init()
	pygame.mixer.init()
	# constants
	self.JSON = "json"
	self.GRAPHICS = 'graphics'
	self.MUSIC = 'music'
	self.SFX = 'sfx'	
	self.BORDER = 70
	self.CUSTOMMOUSE = 0 # 0 for yes, 1 for no
	self.DEBUG = True # debug/editor mode press E to enter editor 

	self.width = width
	self.height = height
	self.screen = pygame.display.set_mode((self.width, self.height))
	pygame.display.set_caption(caption)
	# image with instructions to display before the game starts
	self.instructions = pygame.image.load(os.path.join(self.GRAPHICS, "instructions.png")).convert_alpha()
	self.intro = False
	self.running = True
	self.clock = pygame.time.Clock()
	self.fps = 30 # 30 fps is fine for an adventure game, right?
	self.font = pygame.font.SysFont('courier', 12)
	self.text = "" # holds object messages
	self.colors = {'black': (0,0,0),
			'white': (255,255,255)}
	self.rooms = {}
	self.cur_room = None
	self.cur_view = None
	# custom snazzy mouse!
	pygame.mouse.set_visible(self.CUSTOMMOUSE)
	self.mouse_default = pygame.image.load(os.path.join(self.GRAPHICS, "mouse_default.png")).convert_alpha()
	self.mouse_left = pygame.image.load(os.path.join(self.GRAPHICS, "mouse_left.png")).convert_alpha()
	self.mouse_right = pygame.image.load(os.path.join(self.GRAPHICS, "mouse_right.png")).convert_alpha()
	self.mouse = self.mouse_default

    def run(self):
	mpos = (0, 0)
	self.setup()

	music = os.path.join(self.MUSIC, "come_home.wav")
	pygame.mixer.music.load(music)
	pygame.mixer.music.set_volume(0.5)
	pygame.mixer.music.play(-1)

	while self.running:
	    for event in pygame.event.get():
		if event.type == pygame.QUIT:
		    sys.exit()
		    pygame.quit()
		if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
		    sys.exit()
		    pygame.quit()
		if event.type == pygame.MOUSEMOTION:
		    mpos = event.pos
		    if mpos[0] <= self.BORDER:
			self.mouse = self.mouse_left
		    elif mpos[0] >= (self.width - self.BORDER):
			self.mouse = self.mouse_right
		    else:
			self.mouse = self.mouse_default
		# get mouse position on release of left mouse button
		if event.type == pygame.MOUSEBUTTONUP:
		    if event.button == 1:
			# get rid of intro
			if self.intro:
			    self.intro = False
			else:
			    # clear any currently drawn message
			    self.text = ""
			    if self.DEBUG:
				print(mpos)
			    self.mouse_click(mpos)

		self.draw(mpos)
		#self.clock.tick(self.fps)
    
    def draw(self, mpos):
	# draw view and view's objects 
	self.rooms[self.cur_room][self.cur_view]['view'].draw(self.screen)	
	# draw message box at bottom of screen
	self.draw_message()
	# draw intro screen if applicable
	if self.intro:
	    self.screen.blit(self.instructions, (0,0))
	# draw custom mouse
	self.draw_mouse(mpos)
	# update the screen!
	pygame.display.update()

    def draw_mouse(self, mpos):
	if self.CUSTOMMOUSE == 0: # if mouse isn't visible
	    self.screen.blit(self.mouse, mpos)

    def draw_message(self):
	pygame.draw.rect(self.screen, self.colors['black'],\
			(0, self.height-20, self.width, self.height)) 
	# draw message in message box
	if self.text != "":
	    rendered_msg = self.font.render(self.text, 1,\
					    self.colors['white'], self.colors['black'])
	    self.screen.blit(rendered_msg, (10, self.height-15))	
    
    def mouse_click(self, mpos):
	# CHECK IF CLICKED OBJECT
	# check if clicked object is alive (and parent activated if applicable)
	obj = self.rooms[self.cur_room][self.cur_view]['view'].click_check(mpos)
	# clicked object is alive and parent activated if necessary
	if obj:
	    obj, msg = self.req.req_check(obj,
					self.rooms)
	    # object failed to validate
	    if msg:
		#! CHANGE TO DISPLAY ON SCREEN RATHER THAN IN TERMINAL
		self.text = obj.message
	    # all reqs validated
	    else:
		# obj.door == None
		if not(obj.door):
		    obj.toggle(self.req.sounds)
		else:
		    obj.toggle(self.req.sounds)
		    self.cur_room = obj.door[room] # Room
		    self.cur_view = obj.door[view] # int
	# CHECK IF CLICKED BORDER
	if mpos[0] <= self.BORDER:
	    self.cur_view = self.room.change_view(self.cur_view, "left")
	elif mpos[0] >= self.width - self.BORDER:
	    self.cur_view = self.room.change_view(self.cur_view, "right")
	 

    # define all objects, rooms, views, doors, requirements, etc.
    def setup(self):
	self.req = requirements.Requirements()

	# load starting JSON file that declares which rooms the game will use
	file_setup = open(os.path.join(self.JSON, "setup.json"), "r")
	print("* setup.json opened")
	data_setup = json.load(file_setup)
	file_setup.close()
	print("* setup.json closed")

	data_rooms = {}

	# create all of the rooms
	for room_name in data_setup["rooms"]:
	    # open file for each room and get the data from it
	    file_room = open(os.path.join(self.JSON, (room_name+".json")), "r")
	    print("* {}.json opened".format(room_name))
	    data_rooms[room_name] = json.load(file_room)
	    file_room.close()
	    print("* {}.json closed".format(room_name))

	    # create a room, ready to have views added to it
	    print("-creating room " + room_name)
	    self.rooms[room_name] = {room_name: room.Room()}

	    for view_name in data_rooms[room_name]:
		print(view_name)
		# create a room, ready to have rooms added to it
		print("    -creating view {}".format(view_name))
		view_path = os.path.join(self.GRAPHICS, room_name, view_name)
		self.rooms[room_name][view_name] = {'id': data_rooms[room_name][view_name]['id'],
						    'view': view.View(view_path, 'bg.png'),
						    'objects': []}

		# get data for the view
		data_view = data_rooms[room_name][view_name]
		for obj_name in data_view["objects"].keys():
		    # declare objects  
		    #print(data_view["objects"][obj_key])
		    obj = data_view["objects"][obj_name]
		    print("        -creating object {}".format(obj_name))
		    obj_path = os.path.join(self.GRAPHICS, room_name, view_name)
		    try:
			# object is already set up in json file
			vars()[obj_name] = self.create_object(obj_name, obj_path, obj)
		    except KeyError: # something in the object is not set up
			# launch the editor
			print("        @editing object {}".format(obj_name))
			self.editor(data_rooms, room_name, view_name, obj_name)
			# reload the file and grab the object just edited
			file_room = open(os.path.join(self.JSON, (room_name+".json")), "r")
			print("* {}.json opened".format(room_name))
			data_rooms[room_name] = json.load(file_room)
			file_room.close()
			print("* {}.json closed".format(room_name))
			# create the object
			vars()[obj_name] = self.create_object(obj_name, obj_path, obj)
		    # setup object doors
		    if obj['door']['room'] != "" and obj['door']['view'] != "":
			vars()[obj_name].door = {'room': obj['door']['room'], 'view': obj['door']['view']}
		    # setup object parents and antiparents
		    if obj['parents'] != [""]:
			parents = []
			for parent in obj['parents']:
			    parents.append(parent)
			vars()[obj_name].parents = parents
		    if obj['antiparents'] != [""]:
			antiparents = []
			for antiparent in obj['antiparents']:
			    antiparents.append(antiparent)
			vars()[obj_name].antiparents = antiparents
		    # add reqs and antireqs for object
		    reqs = []
		    if obj['reqs'] != []:
			reqs = obj['reqs']
			if obj['antireqs'] != []:
			    antireqs = obj['antireqs']
		    if reqs != []:
			if antireqs != []:
			    self.req.add_req(obj_name, reqs, antireqs)
			else:
			    self.req.add_req(obj_name, reqs)
		    # add sound effects
		    if obj['sound_on'] != "":
			vars()[obj_name].sound_on = obj['sound_on']
			self.req.add_sound(self.SFX, obj['sound_on'])
		    if obj['sound_off'] != "":
			vars()[obj_name].sound_off = obj['sound_off']
			self.req.add_sound(self.SFX, obj['sound_off'])
			    
		    self.rooms[room_name][view_name]['view'].objects[obj_name] = vars()[obj_name]
	    print("! done creating objects in view {}".format(view_name))
		
	    # construct rooms and set starting room
	    self.cur_room = data_setup['start_room']
	    self.cur_view = data_setup['start_view']

    def create_object(self, obj_name, obj_path, obj):
	new_object = object_.Object(obj_name, obj_path, obj['x'], obj['y'],
				obj['image_off'], obj['image_on'],
				obj['rect_off'], obj['rect_on'],
				activated=obj['activated'],examine=obj['examine'],
				breaks=obj['breaks'],dies=obj['dies'],message=obj['message'])
	return new_object


    def editor(self, data_rooms, room_name, view_name, obj_name):
	mpos = (0,0)
	new_object = {}
	stage = 1 # decides what is set on mouse click
	pos = None # x,y position of images
	pos_start = None
	pos_end = None
	image_on = None
	image_off = None
	examine = False
	self.text = "IMAGE_OFF IS BLANK IMAGE? (y/n)"

	flag_click = False
	flag_key = ''
	editing = True
	while editing:
	    # get mouse position
	    for event in pygame.event.get():
		if event.type == pygame.MOUSEMOTION:
		    mpos = event.pos
		if event.type == pygame.MOUSEBUTTONUP:
		    if event.button == 1: # left click
			flag_click = True
		if event.type == pygame.KEYDOWN:
		    if event.key == pygame.K_y:
			flag_key = 'y'
		    elif event.key == pygame.K_n:
			flag_key = 'n'
	    if stage == 1 and flag_key != "":
		if flag_key == 'y':
		    new_object['image_off'] = 'empty.png'
		    stage = 2
		    self.text = "IMAGE_ON IS BLANK IMAGE? (y/n)"
		    flag_key = ""
		elif flag_key == 'n':
		    new_object['image_off'] = obj_name + '_off.png'
		    image_path = os.path.join(self.GRAPHICS, room_name, view_name, obj_name)
		    image_path = image_path + "_off.png"
		    image_off = pygame.image.load(image_path).convert_alpha()
		    stage = 2
		    self.text = "IMAGE_ON IS BLANK IMAGE? (y/n)"
		    flag_key = ""
	    elif stage == 2 and flag_key != "":
		if flag_key == 'y':
		    new_object['image_on'] = 'empty.png'
		    stage = 3
		    self.text = "SET X, Y POS OF IMAGES"
		    flag_key = ""
		elif flag_key == 'n':
		    new_object['image_on'] = obj_name + '_on.png'
		    image_path = os.path.join(self.GRAPHICS, room_name, view_name, obj_name)
		    image_path = image_path + "_on.png"
		    image_on = pygame.image.load(image_path).convert_alpha()
		    stage = 3
		    self.text = "SET X, Y POS OF IMAGES"
		    flag_key = ""
	    # pick object's (both on and off) x and y position
	    elif stage == 3 and flag_click:
		new_object['x'], new_object['y'] = mpos 
		pos = mpos
		print("% object x and y set")
		stage = 4
		self.text = "SET RECT_OFF START POS"
		flag_click = False
	    # place object's rect_off
	    elif stage == 4 and flag_click:
		if pos_start == None:
		    pos_start = mpos
		    self.text = "SET RECT_OFF END POS"
		    flag_click = False
		elif pos_end == None:
		    pos_end = mpos
		    width = pos_end[0] - pos_start[0]
		    height = pos_end[1] - pos_start[1]
		    new_object['rect_off'] = (pos_start[0], pos_start[1], width, height)
		    print("% rect_off set")
		    # reset pos_start and pos_end for setting rect_off
		    pos_start = None
		    pos_end = None
		    stage = 5
		    self.text = "SET RECT_ON START POS"
		    flag_click = False
	    # place object's rect_on
	    elif stage == 5 and flag_click:
		if pos_start == None:
		    pos_start = mpos
		    self.text = "SET RECT_ON END POS"
		elif pos_end == None:
		    pos_end = mpos
		    width = pos_end[0] - pos_start[0]
		    height = pos_end[1] - pos_start[1]
		    new_object['rect_on'] = (pos_start[0], pos_start[1], width, height)
		    print("%s rect_on set")
		    stage = 6
		    self.text = "START OBJECT ACTIVATED? (y/n)"
		    flag_click = False
	    # ask about all possible properties
	    elif stage == 6 and flag_key: # activated
		if flag_key == 'y':
		    new_object['activated'] = True
		    stage = 7
		    self.text = "OBJECT GETS EXAMINED? (y/n)"
		    flag_key = ""
		elif flag_key == 'n':
		    new_object['activated'] = False
		    stage = 7
		    self.text = "OBJECT GETS EXAMINED? (y/n)"
		    flag_key = ""
	    elif stage == 7 and flag_key: # examine
		if flag_key == 'y':
		    new_object['examine'] = True
		    stage = 8
		    examine = True
		    self.text = "OBJECT BREAKS? (y/n)"
		    flag_key = False
		elif flag_key == 'n':
		    new_object['examine'] = False
		    stage = 8
		    self.text = "OBJECT BREAKS? (y/n)"
		    flag_key = False
	    elif stage == 8 and flag_key: # breaks 
		if flag_key == 'y':
		    new_object['breaks'] = True
		    stage = 9
		    self.text = "OBJECT DIES? (y/n)"
		    flag_key = False
		elif flag_key == 'n':
		    new_object['breaks'] = False
		    stage = 9
		    self.text = "OBJECT DIES? (y/n)"
		    flag_key = False
	    elif stage == 9 and flag_key: # dies 
		if flag_key == 'y':
		    new_object['dies'] = True
		    stage = 10
		    flag_key = False
		elif flag_key == 'n':
		    new_object['dies'] = False
		    stage = 10
		    flag_key = False
	    # let user select sound for sound_on from a list
	    # let user select sound for sound_off from a list
	    # message, reqs, antireqs, parents, and antiparents must be set manually
	    elif stage == 10:
		new_object['message'] = ""
		new_object['sound_on'] = ""
		new_object['sound_off'] = ""
		new_object['parents'] = []
		new_object['antiparents'] = []
		new_object['reqs'] = []
		new_object['antireqs'] = []
		new_object['door'] = {'room': "", 'view': ""}
		print("{} created successfully!".format(obj_name))
		
		self.text = "DONE EDITING OBJECT"
		# modify the object in the roomname.json file and save the updated file
		#file_room = open(os.path.join(self.JSON, (room_name+".json")), "r")
		#data_rooms = json.load(file_room)
		for field in new_object:
		    data_rooms[room_name][view_name]['objects'][obj_name][field] = new_object[field] 
		file_rooms = open(os.path.join(self.JSON, (room_name + ".json")), 'w')  
		json.dump(data_rooms[room_name], file_rooms, sort_keys=True,
					indent=4, separators=(',', ': '))
		file_rooms.close()
		print("! {}.json updated!".format(room_name))

		
		
		editing = False

	    flag_click = False
	    flag_key = ''

	    # draw stuff
	    # draw view background image
	    self.screen.blit(self.rooms[room_name][view_name]['view'].image, (0,0)) 
	    # draw objects already set up
	    for obj in self.rooms[room_name][view_name]['view'].objects:
		obj = self.rooms[room_name][view_name]['view'].objects[obj]
		self.screen.blit(obj.image_off, (obj.x, obj.y))
		if not(obj.examine): # don't need examined objects obscuring the entire screen
		    self.screen.blit(obj.image_on, (obj.x, obj.y))
	    # draw object after placing it
	    if image_on and not(examine):
		if pos:
		    self.screen.blit(image_on, pos)
		else:
		    self.screen.blit(image_on, mpos)
	    if image_off:
		if pos:
		    self.screen.blit(image_off, pos)
		else:
		    self.screen.blit(image_off, mpos)
	    # draw rect when placing rect
	    if pos_start and not(pos_end):
		if mpos[0] < pos_start[0]:
		    x = mpos[0]
		    w = pos_start[0] - mpos[0]
		else:
		    x = pos_start[0]
		    w = mpos[0] - pos_start[0]
		if mpos[1] < pos_start[1]:
		    y = mpos[1]
		    h = pos_start[1] - mpos[1]
		else:
		    y = pos_start[1]
		    h = mpos[1] - pos_start[1]
		pygame.draw.rect(self.screen, (255,225,225), (x,y,w,h))
	    self.draw_message() # draw message at bottom of screen
	    self.draw_mouse(mpos)
	    pygame.display.update()



## DECLARE OBJECTS
#	o_bedroom_bed = object_.Object("bedroom_bed", self.GRAPHICS, 121, 193,
#			"bedroom_bedroom_bed_off.png", "bedroom_bedroom_bed_on.png",
#			(121, 193, 388, 212), (121, 193, 388, 212))
#	o_bedroom_desk = object_.Object("bedroom_desk", self.GRAPHICS, 490, 294,
#			"bedroom_bedroom_desk_off.png", "bedroom_bedroom_desk_on.png",
#			(524, 345, 172, 88), (490, 423, 181, 88))
#	o_bedroom_article = object_.Object("bedroom_article", self.GRAPHICS, 591, 405,
#			"bedroom_bedroom_article_off.png", "bedroom_bedroom_article_on.png",
#			(591, 405, 42, 34), "full",
#			examine=True)
#	o_bedroom_alarm = object_.Object("bedroom_alarm", self.GRAPHICS, 628, 294,
#			"bedroom_bedroom_alarm_off.png", "bedroom_bedroom_alarm_on.png",
#			(628, 294, 45, 36), "full",
#			examine=True)
#	o_bedroom_diary = object_.Object("bedroom_diary", self.GRAPHICS, 551, 296,
#			"bedroom_bedroom_diary_off.png", "bedroom_bedroom_diary_on.png",
#			(551, 296, 68, 29), "full",
#			examine=True)
#
#	o_medals_tv = object_.Object("medals_tv", self.GRAPHICS, 167, 139,
#			"bedroom_medals_tv_off.png", "bedroom_medals_tv_on.png",
#			(167, 139, 255, 176), (167, 139, 255, 176))
#	o_medals_picture = object_.Object("medals_picture", self.GRAPHICS, 438, 269,
#			"bedroom_medals_picture_off.png", "bedroom_medals_picture_on.png",
#			(438, 269, 113, 87), (459, 345, 94, 19),
#			breaks=True, message="I can't seem to take my mind off those medals...")
#	o_medals_closetkey = object_.Object("medals_closetkey", self.GRAPHICS, 468, 318,
#			"bedroom_medals_closetkey_off.png", "empty.png",
#			(468, 318, 74, 27), (0,0,0,0),
#			dies=True)
#	o_medals_medal1 = object_.Object("medals_medal1", self.GRAPHICS, 140, 374,
#			"bedroom_medals_medal_off.png", "empty.png",
#			(147, 374, 51, 117), (147, 374, 51, 117))
#	o_medals_medal2 = object_.Object("medals_medal2", self.GRAPHICS, 188, 368,
#			"bedroom_medals_medal_off.png", "empty.png",
#			(188, 368, 51, 117), (188, 368, 51, 117))
#	o_medals_medal3 = object_.Object("medals_medal3", self.GRAPHICS, 245, 365,
#			"bedroom_medals_medal_off.png", "empty.png",
#			(245, 365, 51, 117), (245, 365, 51, 117))
#	o_medals_medal4 = object_.Object("medals_medal4", self.GRAPHICS, 297, 369,
#			"bedroom_medals_medal_off.png", "empty.png",
#			(297, 396, 51, 117), (297, 396, 51, 117))
#	o_medals_medal5 = object_.Object("medals_medal5", self.GRAPHICS, 345, 373,
#			"bedroom_medals_medal_off.png", "empty.png",
#			(345, 373, 51, 117), (345, 373, 51, 117))
#	o_medals_medal6 = object_.Object("medals_medal6", self.GRAPHICS, 392, 371,
#			"bedroom_medals_medal_off.png", "empty.png",
#			(392, 371, 51, 117), (392, 371, 51, 117))
#	o_medals_medal7 = object_.Object("medals_medal7", self.GRAPHICS, 439, 371,
#			"bedroom_medals_medal_off.png", "empty.png",
#			(439, 371, 51, 117), (439, 371, 51, 117))
#	o_medals_medal8 = object_.Object("medals_medal8", self.GRAPHICS, 487, 369,
#			"bedroom_medals_medal_off.png", "empty.png",
#			(487, 369, 51, 117), (487, 369, 51, 117))
#	o_medals_medal9 = object_.Object("medals_medal9", self.GRAPHICS, 541, 367,
#			"bedroom_medals_medal_off.png", "empty.png",
#			(541, 367, 51, 117), (541, 367, 51, 117))
#	o_medals_medal0 = object_.Object("medals_medal0", self.GRAPHICS, 591, 373,
#			"bedroom_medals_medal_off.png", "empty.png",
#			(591, 373, 51, 117), (591, 373, 51, 117))
#
#	o_closet_closet = object_.Object("closet_closet", self.GRAPHICS, 0, 0,
#			"bedroom_closet_closet_off.png", "bedroom_closet_closet_on.png",
#			(0,0,800,600), (0,0,800,600),
#			message="The door is locked. I think the key is around here somewhere..")
#	o_closet_shirt1 = object_.Object("closet_shirt1", self.GRAPHICS, 113, 125,
#			"bedroom_closet_greenshirt_off.png", "empty.png",
#			(113, 125, 241, 241), (113, 125, 241, 241))
#	o_closet_shirt2 = object_.Object("closet_shirt2", self.GRAPHICS, 169, 139, 
#			"bedroom_closet_redshirt_off.png", "empty.png",
#			(169+50, 139, 241, 241), (169+50, 139, 241, 241))
#	o_closet_shirt3 = object_.Object("closet_shirt3", self.GRAPHICS, 241, 133,
#			"bedroom_closet_blueshirt_off.png", "empty.png",
#			(241+50, 133, 241, 241), (241+50, 133, 241, 241))
#	o_closet_shirt4 = object_.Object("closet_shirt4", self.GRAPHICS, 311, 112,
#			"bedroom_closet_blueshirt_off.png", "empty.png",
#			(311+50, 112, 241, 241), (311+50, 112, 241, 241))
#	o_closet_shirt5 = object_.Object("closet_shirt5", self.GRAPHICS, 369, 116,  
#			"bedroom_closet_greenshirt_off.png", "empty.png",
#			(369+50, 116, 241, 241), (369+50, 116, 241, 241))
#	o_closet_shirt6 = object_.Object("closet_shirt6", self.GRAPHICS, 435, 112,
#			"bedroom_closet_blueshirt_off.png", "empty.png",
#			(435+50, 112, 241, 241), (435+50, 112, 241, 241))
#	o_closet_article = object_.Object("closet_article", self.GRAPHICS, 307, 475,
#			"bedroom_closet_article_off.png", "bedroom_closet_article_on.png",
#			(307, 475, 57, 55), "full",
#			examine=True)
#	o_closet_gun = object_.Object("closet_gun", self.GRAPHICS, 415, 478,
#			"bedroom_closet_gun_off.png", "empty.png",
#			(415, 478, 80, 39), (0,0,0,0),
#			dies=True)
#	o_door_door = object_.Object("door_door", self.GRAPHICS, 16, 32,
#			"bedroom_door_door_off.png", "bedroom_door_door_on.png",
#	           	(236, 72, 323, 447), (68, 86, 212, 512),
#			message="I don't think it's safe to go out there...")
#
#	# DECLARE OBJECT PARENTS
#	o_bedroom_article.parent = [o_bedroom_desk]
#	o_medals_closetkey.parent = [o_medals_picture]
#	o_closet_article.parent = [o_closet_closet, o_closet_shirt3, o_closet_shirt4, o_closet_shirt6]
#	o_closet_article.antiparent = [o_closet_shirt1, o_closet_shirt2, o_closet_shirt5]
#	o_closet_gun.parent = [o_closet_closet, o_closet_shirt3, o_closet_shirt4, o_closet_shirt6]
#	o_closet_gun.antiparent = [o_closet_shirt1, o_closet_shirt2, o_closet_shirt5]
#	o_closet_shirt1.parent = [o_closet_closet]
#	o_closet_shirt2.parent = [o_closet_closet]
#	o_closet_shirt3.parent = [o_closet_closet]
#	o_closet_shirt4.parent = [o_closet_closet]
#	o_closet_shirt5.parent = [o_closet_closet]
#	o_closet_shirt6.parent = [o_closet_closet]
#
#	o_door_door.parent = [o_closet_gun]
#	# DECLARE VIEWS
#	v_bedroom_bedroom = view.View(self.GRAPHICS, "bedroom_bedroom.png", [o_bedroom_bed, o_bedroom_desk, o_bedroom_article, o_bedroom_alarm, o_bedroom_diary])
#	v_bedroom_medals = view.View(self.GRAPHICS, "bedroom_medals.png", [o_medals_tv, o_medals_picture, o_medals_closetkey, o_medals_medal1, o_medals_medal2, o_medals_medal3,
#			    o_medals_medal4, o_medals_medal5, o_medals_medal6, o_medals_medal7, o_medals_medal8, o_medals_medal9, o_medals_medal0])    
#	v_bedroom_closet = view.View(self.GRAPHICS, "bedroom_closet.png", [o_closet_closet, o_closet_article, o_closet_gun, o_closet_shirt1, o_closet_shirt2, o_closet_shirt3,
#			     o_closet_shirt4, o_closet_shirt5, o_closet_shirt6])
#	v_bedroom_door = view.View(self.GRAPHICS, "bedroom_door.png", [o_door_door])
#	# DECLARE ROOMS and set starting room/view
#	self.r_bedroom = room.Room([v_bedroom_bedroom, v_bedroom_closet, v_bedroom_door, v_bedroom_medals])
#	self.room = self.r_bedroom
#	self.cur_view = 0
#	# SETUP OBJECT DOORS
#	# SET OBJECT REQUIREMENTS
#	self.req = requirements.Requirements()
#	self.req.add_req(o_medals_picture, [o_medals_medal2, o_medals_medal3, o_medals_medal8], 
#			[o_medals_medal1, o_medals_medal4, o_medals_medal4, o_medals_medal5, o_medals_medal6, o_medals_medal7, o_medals_medal9, o_medals_medal0])
#	self.req.add_req(o_closet_closet, [o_medals_closetkey])
#	# SET OBJECT SOUND EFFECTS
#	# v_bedroom_bedroom
#	self.req.add_sound(self.SFX, "plastic.wav", v_bedroom_bedroom, [o_bedroom_alarm])
#	self.req.add_sound(self.SFX, "examine.wav", v_bedroom_bedroom, [o_bedroom_article])
#	self.req.add_sound(self.SFX, "cloth.wav", v_bedroom_bedroom, [o_bedroom_bed])
#	self.req.add_sound(self.SFX, "drawer.wav", v_bedroom_bedroom, [o_bedroom_desk])
#	self.req.add_sound(self.SFX, "book.wav", v_bedroom_bedroom, [o_bedroom_diary])
#	# v_bedroom_closet
#	self.req.add_sound(self.SFX, "wood.wav", v_bedroom_closet, [o_closet_closet])
#	self.req.add_sound(self.SFX, "examine.wav", v_bedroom_closet, [o_closet_article])
#	self.req.add_sound(self.SFX, "plastic.wav", v_bedroom_closet, [o_closet_gun])
#	self.req.add_sound(self.SFX, "drop.wav", v_bedroom_closet, [o_closet_shirt3, o_closet_shirt4, o_closet_shirt6])
#	self.req.add_sound(self.SFX, "cloth.wav", v_bedroom_closet, [o_closet_shirt1])
#	self.req.add_sound(self.SFX, "cloth.wav", v_bedroom_closet, [o_closet_shirt2])
#	self.req.add_sound(self.SFX, "cloth.wav", v_bedroom_closet, [o_closet_shirt3])
#	self.req.add_sound(self.SFX, "cloth.wav", v_bedroom_closet, [o_closet_shirt4])
#	self.req.add_sound(self.SFX, "cloth.wav", v_bedroom_closet, [o_closet_shirt5])
#	self.req.add_sound(self.SFX, "cloth.wav", v_bedroom_closet, [o_closet_shirt6])
#	# v_bedroom_medals 
#	self.req.add_sound(self.SFX, "power.wav", v_bedroom_medals, [o_medals_tv])
#	self.req.add_sound(self.SFX, "closetkey.wav", v_bedroom_medals, [o_medals_closetkey])
#	self.req.add_sound(self.SFX, "wood.wav", v_bedroom_medals, [o_medals_picture])
#	self.req.add_sound(self.SFX, "medal.wav", v_bedroom_medals, [o_medals_medal1])
#	self.req.add_sound(self.SFX, "medal.wav", v_bedroom_medals, [o_medals_medal2])
#	self.req.add_sound(self.SFX, "medal.wav", v_bedroom_medals, [o_medals_medal3])
#	self.req.add_sound(self.SFX, "medal.wav", v_bedroom_medals, [o_medals_medal4])
#	self.req.add_sound(self.SFX, "medal.wav", v_bedroom_medals, [o_medals_medal5])
#	self.req.add_sound(self.SFX, "medal.wav", v_bedroom_medals, [o_medals_medal6])
#	self.req.add_sound(self.SFX, "medal.wav", v_bedroom_medals, [o_medals_medal7])
#	self.req.add_sound(self.SFX, "medal.wav", v_bedroom_medals, [o_medals_medal8])
#	self.req.add_sound(self.SFX, "medal.wav", v_bedroom_medals, [o_medals_medal9])
#	self.req.add_sound(self.SFX, "medal.wav", v_bedroom_medals, [o_medals_medal0])
#	# v_bedroom_door
#	self.req.add_sound(self.SFX, "door.wav", v_bedroom_door, [o_door_door])
#
#
