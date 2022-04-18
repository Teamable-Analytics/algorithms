class Graph(object):
    
    def __init__(self):
        self.nodes = []
        self.edges = {}
        
    def add_node(self, node):
        if node in self.nodes:
            raise ValueError('Duplicate Node')
        else:
            self.nodes.append(node.get_name())
            self.edges[node.get_name()] = []

    def add_edge(self, edge):
        src = edge.get_source()
        dest = edge.get_destination()
        weight = edge.get_weight()
        if not (src in self.nodes and dest in self.nodes):
            raise ValueError('Node not in graph')
        self.edges[src].append([dest, weight])
    
    def get_nodes(self):
        
        return self.nodes
    
    
    def get_edges(self):
        
        return self.edges