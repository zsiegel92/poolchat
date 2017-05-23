	#If self.menu == 'fieldstate', update fields and go to next field.
	#If self.menu == 'edit_field', update field and return to that menu.
	#If self.menu ==

# PREVIOUS SOLUTION:
	def next(self,input=None):
		if self.returnToMenu():
		  self.fieldstate = self.menu
		  self.menu = 'menu'
		  return self.head()

		print("self.nextField(" + input + ") ==" + self.nextField(input), file=sys.stderr)
		newFieldState = self.nextField(input)
		newNode = self.getField(newFieldState)
		print("Changing self.fieldstate from " + str(self.fieldstate) + " to " + str(newFieldState), file=sys.stderr)
		print("self.menu: " + str(self.menu))
		self.fieldstate = newFieldState
		print("Returning new node.", file=sys.stderr)
		return newNode


	def returnToMenu(self):
		return (self.menu !='fieldstate')

CHANGED A LOT
	def next(self,input=None):
		if self.menu == 'fieldstate'
			self.fieldstate = self.nextField(input)
			return self.head()
		else:
			self.fieldstate = self.menu
			self.menu = 'menu'
			return self.head()
