
#Maybe make it a dataclass?
class ExploreRequest(object):
    def __init__(self, query=None, radius=None, location=None):
        self.query = query
        self.radius = radius
        self.location = location

    def is_valid(self):
        return self.query != None and self.radius != None and self.location != None