import sys
import os

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
	self.GRAPHICS = 'graphics'
	self.MUSIC = 'music'
	self.SFX = 'sfx'	
	self.BORDER = 70
	self.OLDTOPMAN = False # debug/cheat mode (doesn't really do anything yet)

	self.width = width
	self.height = height
	self.screen = pygame.display.set_mode((self.width, self.height))
	pygame.display.set_caption(caption)
	# image with instructions to display before the game starts
	self.instructions = pygame.image.load(os.path.join(self.GRAPHICS, "instructions.png")).convert_alpha()
	self.intro = True
	self.running = True
	self.clock = pygame.time.Clock()
	self.fps = 30 # 30 fps is fine for an adventure game, right?
	self.font = pygame.font.SysFont('courier', 12)
	self.text = "" # holds object messages
	self.colors = {'black': (0,0,0),
			'white': (255,255,255)}
	self.room = None
	self.cur_view = None
	# custom snazzy mouse!
	pygame.mouse.set_visible(0)
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
			    if self.OLDTOPMAN:
				print(mpos)
			    self.mouse_click(mpos)
				
		self.draw(mpos)
		#self.clock.tick(self.fps)
    
    def draw(self, mpos):
	# draw view and view's objects 
	self.room[self.cur_view].draw(self.screen)	
	# draw message box at bottom of screen
	pygame.draw.rect(self.screen, self.colors['black'],\
			(0, self.height-20, self.width, self.height)) 
	# draw message in message box
	if self.text != "":
	    rendered_msg = self.font.render(self.text, 1,\
					    self.colors['white'], self.colors['black'])
	    self.screen.blit(rendered_msg, (10, self.height-15))	
	# draw intro screen if applicable
	if self.intro:
	    self.screen.blit(self.instructions, (0,0))
	# draw custom mouse
	self.screen.blit(self.mouse, mpos)
	# update the screen!
	pygame.display.update()
    
    def mouse_click(self, mpos):
	# CHECK IF CLICKED OBJECT
	# check if clicked object is alive (and parent activated if applicable)
	obj = self.room[self.cur_view].click_check(mpos)
	# clicked object is alive and parent activated if necessary
	if obj:
	    obj, msg = self.req.req_check(obj,
					self.room[self.cur_view].objects)
	    # object failed to validate
	    if msg:
		#! CHANGE TO DISPLAY ON SCREEN RATHER THAN IN TERMINAL
		self.text = obj.message
	    # all reqs validated
	    else:
		# obj.door == None
		if not(obj.door):
		    obj.toggle()
		else:
		    self.room = obj.door[0] # Room
		    self.cur_view = obj.door[1] # int
	# CHECK IF CLICKED BORDER
	if mpos[0] <= self.BORDER:
	    self.cur_view = self.room.change_view(self.cur_view, "left")
	elif mpos[0] >= self.width - self.BORDER:
	    self.cur_view = self.room.change_view(self.cur_view, "right")
	# check sounds
	self.req.sound_check(self.room[self.cur_view])

    # define all objects, rooms, views, doors, requirements, etc.
    def setup(self):
	# DECLARE OBJECTS
	o_bedroom_bed = object_.Object("bedroom_bed", self.GRAPHICS, 121, 193,
			"bedroom_bedroom_bed_off.png", "bedroom_bedroom_bed_on.png",
			(121, 193, 388, 212), (121, 193, 388, 212))
	o_bedroom_desk = object_.Object("bedroom_desk", self.GRAPHICS, 490, 294,
			"bedroom_bedroom_desk_off.png", "bedroom_bedroom_desk_on.png",
			(524, 345, 172, 88), (490, 423, 181, 88))
	o_bedroom_article = object_.Object("bedroom_article", self.GRAPHICS, 591, 405,
			"bedroom_bedroom_article_off.png", "bedroom_bedroom_article_on.png",
			(591, 405, 42, 34), "full",
			examine=True)
	o_bedroom_alarm = object_.Object("bedroom_alarm", self.GRAPHICS, 628, 294,
			"bedroom_bedroom_alarm_off.png", "bedroom_bedroom_alarm_on.png",
			(628, 294, 45, 36), "full",
			examine=True)
	o_bedroom_diary = object_.Object("bedroom_diary", self.GRAPHICS, 551, 296,
			"bedroom_bedroom_diary_off.png", "bedroom_bedroom_diary_on.png",
			(551, 296, 68, 29), "full",
			examine=True)

	o_medals_tv = object_.Object("medals_tv", self.GRAPHICS, 167, 139,
			"bedroom_medals_tv_off.png", "bedroom_medals_tv_on.png",
			(167, 139, 255, 176), (167, 139, 255, 176))
	o_medals_picture = object_.Object("medals_picture", self.GRAPHICS, 438, 269,
			"bedroom_medals_picture_off.png", "bedroom_medals_picture_on.png",
			(438, 269, 113, 87), (459, 345, 94, 19),
			breaks=True, message="I can't seem to take my mind off those medals...")
	o_medals_closetkey = object_.Object("medals_closetkey", self.GRAPHICS, 468, 318,
			"bedroom_medals_closetkey_off.png", "empty.png",
			(468, 318, 74, 27), (0,0,0,0),
			dies=True)
	o_medals_medal1 = object_.Object("medals_medal1", self.GRAPHICS, 140, 374,
			"bedroom_medals_medal_off.png", "empty.png",
			(147, 374, 51, 117), (147, 374, 51, 117))
	o_medals_medal2 = object_.Object("medals_medal2", self.GRAPHICS, 188, 368,
			"bedroom_medals_medal_off.png", "empty.png",
			(188, 368, 51, 117), (188, 368, 51, 117))
	o_medals_medal3 = object_.Object("medals_medal3", self.GRAPHICS, 245, 365,
			"bedroom_medals_medal_off.png", "empty.png",
			(245, 365, 51, 117), (245, 365, 51, 117))
	o_medals_medal4 = object_.Object("medals_medal4", self.GRAPHICS, 297, 369,
			"bedroom_medals_medal_off.png", "empty.png",
			(297, 396, 51, 117), (297, 396, 51, 117))
	o_medals_medal5 = object_.Object("medals_medal5", self.GRAPHICS, 345, 373,
			"bedroom_medals_medal_off.png", "empty.png",
			(345, 373, 51, 117), (345, 373, 51, 117))
	o_medals_medal6 = object_.Object("medals_medal6", self.GRAPHICS, 392, 371,
			"bedroom_medals_medal_off.png", "empty.png",
			(392, 371, 51, 117), (392, 371, 51, 117))
	o_medals_medal7 = object_.Object("medals_medal7", self.GRAPHICS, 439, 371,
			"bedroom_medals_medal_off.png", "empty.png",
			(439, 371, 51, 117), (439, 371, 51, 117))
	o_medals_medal8 = object_.Object("medals_medal8", self.GRAPHICS, 487, 369,
			"bedroom_medals_medal_off.png", "empty.png",
			(487, 369, 51, 117), (487, 369, 51, 117))
	o_medals_medal9 = object_.Object("medals_medal9", self.GRAPHICS, 541, 367,
			"bedroom_medals_medal_off.png", "empty.png",
			(541, 367, 51, 117), (541, 367, 51, 117))
	o_medals_medal0 = object_.Object("medals_medal0", self.GRAPHICS, 591, 373,
			"bedroom_medals_medal_off.png", "empty.png",
			(591, 373, 51, 117), (591, 373, 51, 117))

	o_closet_closet = object_.Object("closet_closet", self.GRAPHICS, 0, 0,
			"bedroom_closet_closet_off.png", "bedroom_closet_closet_on.png",
			(0,0,800,600), (0,0,800,600),
			message="The door is locked. I think the key is around here somewhere..")
	o_closet_shirt1 = object_.Object("closet_shirt1", self.GRAPHICS, 113, 125,
			"bedroom_closet_greenshirt_off.png", "empty.png",
			(113, 125, 241, 241), (113, 125, 241, 241))
	o_closet_shirt2 = object_.Object("closet_shirt2", self.GRAPHICS, 169, 139, 
			"bedroom_closet_redshirt_off.png", "empty.png",
			(169+50, 139, 241, 241), (169+50, 139, 241, 241))
	o_closet_shirt3 = object_.Object("closet_shirt3", self.GRAPHICS, 241, 133,
			"bedroom_closet_blueshirt_off.png", "empty.png",
			(241+50, 133, 241, 241), (241+50, 133, 241, 241))
	o_closet_shirt4 = object_.Object("closet_shirt4", self.GRAPHICS, 311, 112,
			"bedroom_closet_blueshirt_off.png", "empty.png",
			(311+50, 112, 241, 241), (311+50, 112, 241, 241))
	o_closet_shirt5 = object_.Object("closet_shirt5", self.GRAPHICS, 369, 116,  
			"bedroom_closet_greenshirt_off.png", "empty.png",
			(369+50, 116, 241, 241), (369+50, 116, 241, 241))
	o_closet_shirt6 = object_.Object("closet_shirt6", self.GRAPHICS, 435, 112,
			"bedroom_closet_blueshirt_off.png", "empty.png",
			(435+50, 112, 241, 241), (435+50, 112, 241, 241))
	o_closet_article = object_.Object("closet_article", self.GRAPHICS, 307, 475,
			"bedroom_closet_article_off.png", "bedroom_closet_article_on.png",
			(307, 475, 57, 55), "full",
			examine=True)
	o_closet_gun = object_.Object("closet_gun", self.GRAPHICS, 415, 478,
			"bedroom_closet_gun_off.png", "empty.png",
			(415, 478, 80, 39), (0,0,0,0),
			dies=True)
	o_door_door = object_.Object("door_door", self.GRAPHICS, 16, 32,
			"bedroom_door_door_off.png", "bedroom_door_door_on.png",
	           	(236, 72, 323, 447), (68, 86, 212, 512),
			message="I don't think it's safe to go out there...")

	# DECLARE OBJECT PARENTS
	o_bedroom_article.parent = [o_bedroom_desk]
	o_medals_closetkey.parent = [o_medals_picture]
	o_closet_article.parent = [o_closet_closet, o_closet_shirt3, o_closet_shirt4, o_closet_shirt6]
	o_closet_article.antiparent = [o_closet_shirt1, o_closet_shirt2, o_closet_shirt5]
	o_closet_gun.parent = [o_closet_closet, o_closet_shirt3, o_closet_shirt4, o_closet_shirt6]
	o_closet_gun.antiparent = [o_closet_shirt1, o_closet_shirt2, o_closet_shirt5]
	o_closet_shirt1.parent = [o_closet_closet]
	o_closet_shirt2.parent = [o_closet_closet]
	o_closet_shirt3.parent = [o_closet_closet]
	o_closet_shirt4.parent = [o_closet_closet]
	o_closet_shirt5.parent = [o_closet_closet]
	o_closet_shirt6.parent = [o_closet_closet]

	o_door_door.parent = [o_closet_gun]
	# DECLARE VIEWS
	v_bedroom_bedroom = view.View(self.GRAPHICS, "bedroom_bedroom.png", [o_bedroom_bed, o_bedroom_desk, o_bedroom_article, o_bedroom_alarm, o_bedroom_diary])
	v_bedroom_medals = view.View(self.GRAPHICS, "bedroom_medals.png", [o_medals_tv, o_medals_picture, o_medals_closetkey, o_medals_medal1, o_medals_medal2, o_medals_medal3,
			    o_medals_medal4, o_medals_medal5, o_medals_medal6, o_medals_medal7, o_medals_medal8, o_medals_medal9, o_medals_medal0])    
	v_bedroom_closet = view.View(self.GRAPHICS, "bedroom_closet.png", [o_closet_closet, o_closet_article, o_closet_gun, o_closet_shirt1, o_closet_shirt2, o_closet_shirt3,
			     o_closet_shirt4, o_closet_shirt5, o_closet_shirt6])
	v_bedroom_door = view.View(self.GRAPHICS, "bedroom_door.png", [o_door_door])
	# DECLARE ROOMS and set starting room/view
	self.r_bedroom = room.Room([v_bedroom_bedroom, v_bedroom_closet, v_bedroom_door, v_bedroom_medals])
	self.room = self.r_bedroom
	self.cur_view = 0
	# SETUP OBJECT DOORS
	# SET OBJECT REQUIREMENTS
	self.req = requirements.Requirements()
	self.req.add_req(o_medals_picture, [o_medals_medal2, o_medals_medal3, o_medals_medal8], 
			[o_medals_medal1, o_medals_medal4, o_medals_medal4, o_medals_medal5, o_medals_medal6, o_medals_medal7, o_medals_medal9, o_medals_medal0])
	self.req.add_req(o_closet_closet, [o_medals_closetkey])
	# SET OBJECT SOUND EFFECTS
	# v_bedroom_bedroom
	self.req.add_sound(self.SFX, "plastic.wav", v_bedroom_bedroom, [o_bedroom_alarm])
	self.req.add_sound(self.SFX, "examine.wav", v_bedroom_bedroom, [o_bedroom_article])
	self.req.add_sound(self.SFX, "cloth.wav", v_bedroom_bedroom, [o_bedroom_bed])
	self.req.add_sound(self.SFX, "drawer.wav", v_bedroom_bedroom, [o_bedroom_desk])
	self.req.add_sound(self.SFX, "book.wav", v_bedroom_bedroom, [o_bedroom_diary])
	# v_bedroom_closet
	self.req.add_sound(self.SFX, "wood.wav", v_bedroom_closet, [o_closet_closet])
	self.req.add_sound(self.SFX, "examine.wav", v_bedroom_closet, [o_closet_article])
	self.req.add_sound(self.SFX, "plastic.wav", v_bedroom_closet, [o_closet_gun])
	self.req.add_sound(self.SFX, "drop.wav", v_bedroom_closet, [o_closet_shirt3, o_closet_shirt4, o_closet_shirt6])
	self.req.add_sound(self.SFX, "cloth.wav", v_bedroom_closet, [o_closet_shirt1])
	self.req.add_sound(self.SFX, "cloth.wav", v_bedroom_closet, [o_closet_shirt2])
	self.req.add_sound(self.SFX, "cloth.wav", v_bedroom_closet, [o_closet_shirt3])
	self.req.add_sound(self.SFX, "cloth.wav", v_bedroom_closet, [o_closet_shirt4])
	self.req.add_sound(self.SFX, "cloth.wav", v_bedroom_closet, [o_closet_shirt5])
	self.req.add_sound(self.SFX, "cloth.wav", v_bedroom_closet, [o_closet_shirt6])
	# v_bedroom_medals 
	self.req.add_sound(self.SFX, "power.wav", v_bedroom_medals, [o_medals_tv])
	self.req.add_sound(self.SFX, "closetkey.wav", v_bedroom_medals, [o_medals_closetkey])
	self.req.add_sound(self.SFX, "wood.wav", v_bedroom_medals, [o_medals_picture])
	self.req.add_sound(self.SFX, "medal.wav", v_bedroom_medals, [o_medals_medal1])
	self.req.add_sound(self.SFX, "medal.wav", v_bedroom_medals, [o_medals_medal2])
	self.req.add_sound(self.SFX, "medal.wav", v_bedroom_medals, [o_medals_medal3])
	self.req.add_sound(self.SFX, "medal.wav", v_bedroom_medals, [o_medals_medal4])
	self.req.add_sound(self.SFX, "medal.wav", v_bedroom_medals, [o_medals_medal5])
	self.req.add_sound(self.SFX, "medal.wav", v_bedroom_medals, [o_medals_medal6])
	self.req.add_sound(self.SFX, "medal.wav", v_bedroom_medals, [o_medals_medal7])
	self.req.add_sound(self.SFX, "medal.wav", v_bedroom_medals, [o_medals_medal8])
	self.req.add_sound(self.SFX, "medal.wav", v_bedroom_medals, [o_medals_medal9])
	self.req.add_sound(self.SFX, "medal.wav", v_bedroom_medals, [o_medals_medal0])
	# v_bedroom_door
	self.req.add_sound(self.SFX, "door.wav", v_bedroom_door, [o_door_door])


