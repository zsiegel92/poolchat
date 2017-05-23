class nexthing:
    def __init__(a="hey",next = None):
        if next:
            if isinstance(next,dict):
                self.next = next
            else:
                self.next = {"default":next}
        else:
            self.next = next #None
        self.a = a
    def nextfun():
        if isinstance(self.next,dict):
            self.dict
