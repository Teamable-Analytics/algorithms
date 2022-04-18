class Edge(object):

    def __init__(self, src, dest, weight):
        self.src = src
        self.dest = dest
        self.weight = weight

    def get_source(self):
        return self.src

    def get_destination(self):
        return self.dest
    
    def get_weight(self):
        return self.weight