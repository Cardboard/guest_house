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
        self.fps = 70 # 30 fps is fine for an adventure game, right?
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
            dt = self.clock.tick(self.fps) / 10.0

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

            self.draw(mpos, dt)
    
    def draw(self, mpos, dt):
        # draw view and view's objects 
        self.rooms[self.cur_room][self.cur_view]['view'].draw(self.screen, dt)  
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
                self.text = obj.message
                # all reqs validated
            else:
                # only display response when object is activated
                if obj.response != "" and not(obj.activated):
                    self.text = obj.response
                else:
                    self.text = ""
                obj.toggle(self.req.sounds)
                # change room/view if object is a door
                if obj.door:
                    self.cur_room = obj.door['room'] # Room
                    self.cur_view = obj.door['view'] # int
        # CHECK IF CLICKED BORDER
        if mpos[0] <= self.BORDER:
            i = self.rooms[self.cur_room][self.cur_view]['id']
            i -= 1 
            if i < 0:
                i = len(self.rooms[self.cur_room]) - 1
            for view in self.rooms[self.cur_room]:
                if self.rooms[self.cur_room][view]['id'] == i:
                    self.cur_view = view
        elif mpos[0] >= self.width - self.BORDER:
            i = self.rooms[self.cur_room][self.cur_view]['id']
            i += 1
            if i > len(self.rooms[self.cur_room]) - 1:
                i = 0
            for view in self.rooms[self.cur_room]:
                if self.rooms[self.cur_room][view]['id'] == i:
                    self.cur_view = view
             
    # define all objects, rooms, views, doors, requirements, etc.
    def setup(self):
        self.req = requirements.Requirements()

        # load starting JSON file that declares which rooms the game will use
        file_setup = open(os.path.join(self.JSON, "setup.json"), "r")
        if self.DEBUG:
            print("* setup.json opened")
        data_setup = json.load(file_setup)
        file_setup.close()
        if self.DEBUG:
            print("* setup.json closed")

        data_rooms = {}

        # create all of the rooms
        for room_name in data_setup["rooms"]:
            # open file for each room and get the data from it
            file_room = open(os.path.join(self.JSON, (room_name+".json")), "r")
            if self.DEBUG:
                print("* {}.json opened".format(room_name))
            data_rooms[room_name] = json.load(file_room)
            file_room.close()
            if self.DEBUG:
                print("* {}.json closed".format(room_name))

            if self.DEBUG:
                print("-creating room " + room_name)
            # create a room, ready to have views added to it
            self.rooms[room_name] = {}

            for view_name in data_rooms[room_name]:
                # create a room, ready to have rooms added to it
                if self.DEBUG:
                    print("    -creating view {}".format(view_name))
                view_path = os.path.join(self.GRAPHICS, room_name, view_name)
                self.rooms[room_name][view_name] = {'id': data_rooms[room_name][view_name]['id'],
                                    'view': view.View(view_path, 'bg.png')} 

                # get data for the view
                data_view = data_rooms[room_name][view_name]
                objects = {}
                editor_queue = [] # get all currently set up objects before editing new objects
                for obj_name in data_view["objects"].keys():
                    # declare objects  
                    obj = data_view["objects"][obj_name]
                    obj_name = room_name + "_" + view_name + "_" + obj_name
                    obj_path = os.path.join(self.GRAPHICS, room_name, view_name)
                    try:
                        # object is already set up in json file
                        self.create_object(objects, room_name, view_name, obj_name, obj_path, obj)
                        self.setup_object(objects, room_name, view_name, obj_name, obj_path, obj)
                    except KeyError: # something in the object is not set up
                        # launch the editor
                        if self.DEBUG:
                            print('        # {} added to editor queue'.format(obj_name))
                            editor_queue.append(obj_name)
                        else:
                            print("Error: {} has not been set up.".format(obj_name))
                            print("Remove the objects from {}.json or set it".format(room_name))
                            print("up by setting self.DEBUG = True")
                            sys.exit()
                            pygame.quit()
                if self.DEBUG:    
                    print("    ! done creating objects in view {}".format(view_name))
                # open editor to create objects that need to be created
                for obj_name in editor_queue:
                    self.editor(data_rooms, room_name, view_name, obj_name, objects)
                    #sys.exit()
                    #pygame.quit()
                    if self.DEBUG:
                        print("        -creating object {}".format(obj_name))
                    obj_path = os.path.join(self.GRAPHICS, room_name, view_name)
                    # reload the file and grab the object just edited
                    file_room = open(os.path.join(self.JSON, (room_name+".json")), "r")
                    if self.DEBUG:
                        print("* {}.json opened".format(room_name))
                    data_rooms[room_name] = json.load(file_room)
                    file_room.close()
                    if self.DEBUG:
                        print("* {}.json closed".format(room_name))
                    # create the object
                    obj = data_rooms[room_name][view_name]["objects"][obj_name]
                    self.create_object(objects, room_name, view_name, obj_name, obj_path, obj)
                    self.setup_object(objects, room_name, view_name, obj_name, obj_path, obj)
                self.rooms[room_name][view_name]['view'].objects = objects

        # construct rooms and set starting room
        self.cur_room = data_setup['start_room']
        self.cur_view = data_setup['start_view']

    def create_object(self, objects, room_name, view_name, obj_name, obj_path, obj):
        if self.DEBUG:
            print("        -creating object {}".format(obj_name))
        if obj['image_off'] == "empty.png":
            image_off = os.path.join(self.GRAPHICS, "empty.png")
        else:
            if type(obj['image_off']) == list: # object is animated
                image_list = []
                for i in range(len(obj['image_off'])):
                    image_list.append(os.path.join(self.GRAPHICS, room_name, view_name, obj["image_off"][i]))
                image_off = image_list
            else:
                image_off = os.path.join(self.GRAPHICS, room_name, view_name, obj["image_off"])
        if obj['image_on'] == "empty.png":
            image_on = os.path.join(self.GRAPHICS, "empty.png")
        else:
            if type(obj['image_on']) == list: # object is animated
                image_list = []
                for i in range(len(obj['image_on'])):
                    image_list.append(os.path.join(self.GRAPHICS, room_name, view_name, obj["image_on"][i]))
                image_on = image_list
            else:
                image_on = os.path.join(self.GRAPHICS, room_name, view_name, obj["image_on"])
	# Check if object has "loop" property in json description.
	# Object only has 'loop' in json description if it shouldn't loop.
	# Loop is True by default
	loop = True
	try: 
	    if obj['loop'] == False:
		loop = False
		if self.DEBUG:
		    print("            loop mode for {} set to False".format(obj_name))
	except KeyError:
	    pass
        new_object = object_.Object(obj_name, obj['x'], obj['y'],\
                    image_off, image_on,\
                    obj['rect_off'], obj['rect_on'],\
                    layer=obj['layer'],\
                    activated=obj['activated'],examine=obj['examine'],\
                    breaks=obj['breaks'],dies=obj['dies'],message=obj['message'],response=obj["response"],\
                    info=obj['info'],speed=obj['speed'],loop=loop)
        #self.rooms[room_name][view_name]['view'].objects[obj_name] = new_object
        objects[obj_name] = new_object

    def setup_object(self, objects, room_name, view_name, obj_name, obj_path, obj):
        # setup object doors
        if obj['door']['room'] != "" and obj['door']['view'] != "":
            objects[obj_name].door = \
                {'room': obj['door']['room'], 'view': obj['door']['view']}
        # setup object parents and antiparents
        if obj['parents'] != [""]:
                    parents = []
        for parent in obj['parents']:
                parents.append(parent)
                objects[obj_name].parents = parents
        if obj['antiparents'] != [""]:
                    antiparents = []
        for antiparent in obj['antiparents']:
                antiparents.append(antiparent)
                objects[obj_name].antiparents = antiparents
        # add reqs and antireqs for object
        reqs = []
        antireqs = []
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
            objects[obj_name].sound_on = obj['sound_on']
            self.req.add_sound(self.SFX, obj['sound_on'])
        if obj['sound_off'] != "":
            objects[obj_name].sound_off = obj['sound_off']
            self.req.add_sound(self.SFX, obj['sound_off'])
        if self.DEBUG:
            print("        ! added {} to {}".format(obj_name, view_name))


    def editor(self, data_rooms, room_name, view_name, obj_name, objects):
        print("        @editing object {}".format(obj_name))
        mpos = (0,0)
        new_object = {}
        obj_name_sans = obj_name.split('_')[2] # pure object name, NOT room_view_object structure
        stage = 0 # decides what is set on key press or mouse click
        animated = False
        pos = None # x,y position of images
        pos_start = None
        pos_end = None
        image_on = None
        image_off = None
        examine = False
        self.text = "SELECT OBJECT LAYER. LOWER NUMBERS DRAWN FIRST. (0-9)"

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
                    key = event.key
                    if key == pygame.K_y:
                        flag_key = 'y'
                    elif key == pygame.K_n:
                        flag_key = 'n'
                    elif key == pygame.K_0: flag_key = 0
                    elif key == pygame.K_1: flag_key = 1
                    elif key == pygame.K_2: flag_key = 2
                    elif key == pygame.K_3: flag_key = 3
                    elif key == pygame.K_4: flag_key = 4
                    elif key == pygame.K_5: flag_key = 5
                    elif key == pygame.K_6: flag_key = 6
                    elif key == pygame.K_7: flag_key = 7
                    elif key == pygame.K_8: flag_key = 8
                    elif key == pygame.K_9: flag_key = 9
                    print(flag_key)
            if stage == 0 and flag_key != "": # choose object layer
                if flag_key in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]:
                    new_object['layer'] = flag_key
                    stage = 11
                    self.text = "IMAGE IS ANIMATED? (y/n)"
                    flag_key = ""
            elif stage == 11 and flag_key != "": # animated?
                if flag_key == 'y':
                    animated = True
                    stage = 1
                    self.text = "IMAGE_OFF IS BLANK IMAGE? (y/n)"
                    flag_key = ""
                elif flag_key == 'n':
                    stage = 1
                    self.text = "IMAGE_OFF IS BLANK IMAGE? (y/n)"
                    flag_key = ""
            elif stage == 1 and flag_key != "": # image_off
                if flag_key == 'y':
                    new_object['image_off'] = 'empty.png'
                    stage = 2
                    self.text = "IMAGE_ON IS BLANK IMAGE? (y/n)"
                    flag_key = ""
                elif flag_key == 'n':
                    suffix = ""
                    if animated:
                        suffix = "_1"
                    new_object['image_off'] = obj_name_sans + '_off' + suffix + '.png'
                    image_path = os.path.join(self.GRAPHICS, room_name, view_name, obj_name_sans)
                    image_path = image_path + "_off" + suffix + ".png"
                    image_off = pygame.image.load(image_path).convert_alpha()
                    stage = 2
                    self.text = "IMAGE_ON IS BLANK IMAGE? (y/n)"
                    flag_key = ""
            elif stage == 2 and flag_key != "": # image_on
                if flag_key == 'y':
                    new_object['image_on'] = 'empty.png'
                    stage = 3
                    self.text = "SET X, Y POS OF IMAGES"
                    flag_key = ""
                elif flag_key == 'n':
                    suffix = ""
                    if animated:
                        suffix = "_1"
                    new_object['image_on'] = obj_name_sans + '_on' + suffix + '.png'
                    image_path = os.path.join(self.GRAPHICS, room_name, view_name, obj_name_sans)
                    image_path = image_path + "_on" + suffix + ".png"
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
                    # set rect to entire screen
                    new_object['rect_on'] = 'full'
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
                new_object['response'] = ""
                new_object['sound_on'] = ""
                new_object['sound_off'] = ""
                new_object['parents'] = []
                new_object['antiparents'] = []
                new_object['reqs'] = []
                new_object['antireqs'] = []
                new_object['door'] = {'room': "", 'view': ""}
                new_object['info'] = False
                new_object['speed'] = 0 # speed of animation
                print("{} created successfully!".format(obj_name))
                
                self.text = "DONE EDITING OBJECT"
                # modify the object in the roomname.json file and save the updated file
                #file_room = open(os.path.join(self.JSON, (room_name+".json")), "r")
                #data_rooms = json.load(file_room)
                for field in new_object:
                    data_rooms[room_name][view_name]['objects'][obj_name_sans][field] = new_object[field] 
                file_rooms = open(os.path.join(self.JSON, (room_name + ".json")), 'w')  
                json.dump(data_rooms[room_name], file_rooms, sort_keys=True,
                            indent=4, separators=(',', ': '))
                file_rooms.close()
                print("! {}.json updated!".format(room_name))
            
                editing = False

            flag_click = False
            flag_key = ''

            # draw view background image
            self.screen.blit(self.rooms[room_name][view_name]['view'].image, (0,0)) 
            # START OBJECT DRAWING
            # draw objects already set up
            queue = {'0':[],'1':[],'2':[],'3':[],'4':[],'5':[],'6':[],'7':[],'8':[],'9':[]}
            # draw view first, then objects
            for obj in objects:
                obj = objects[obj] # get object by getting value at objects[key]
                # don't draw if object dies and is dead.
                # broken and dead objects still get drawn.
                if type(obj.image_off) == list:
                    queue[str(obj.layer)].append((obj.image_off[0], (obj.x, obj.y)))
                else:
                    queue[str(obj.layer)].append((obj.image_off, (obj.x, obj.y)))
                if obj.examine:
                    pass # don't draw the 'on' image of examined objects
                else:
                    if type(obj.image_on) == list:
                        queue[str(obj.layer)].append((obj.image_on[0], (obj.x, obj.y)))
                    else:
                        queue[str(obj.layer)].append((obj.image_on, (obj.x, obj.y)))
            # draw object after placing it
            if image_on and not(examine):
                layer = str(new_object["layer"])
                if pos:
                    queue[layer].append((image_on, pos))
                    #self.screen.blit(image_on, pos)
                else:
                    queue[layer].append((image_on, mpos))
                    #self.screen.blit(image_on, mpos)
            if image_off:
                layer = str(new_object["layer"])
                if pos:
                    queue[layer].append((image_off, pos))
                    #self.screen.blit(image_on, pos)
                else:
                    queue[layer].append((image_off, mpos))
                    #self.screen.blit(image_on, mpos)
            # Print objects in queue in order of layers.
            # Lower numbers drawn first (0-9)
            for number in range(0, 10):
                if queue[str(number)] != []:
                    for i in queue[str(number)]:
                        self.screen.blit(i[0], i[1])
            # END OBJECT DRAWING

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
