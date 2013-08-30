class Room:
    def __init__(self, views={}):
	self.visited = False
	self.views = views

    def change_view(self, current, direction):
	current = current
	if direction == 'left':
	    current -= 1
	    # wraparound to view to farthest right of list
	    if current < 0:
		current = len(self.views) - 1
	if direction == 'right':
	    current += 1
	    # wraparound to first view in list
	    if current >= len(self.views):
		current = 0

	return current

    def __getitem__(self, index):
	return self.views[index]
