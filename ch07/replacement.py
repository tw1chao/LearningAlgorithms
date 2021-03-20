"""
Home-grown replacement for networkx IN CASE this package is not found.
This implementation is not meant to be production-quality, but simply
a stub object that provides a reasonable implementation.

Note: Doesn't offer capability to draw graphs.
"""
from algs.node import Node

WEIGHT = 'weight'

class Edge:
    """
    Replacement edge in case networkx is not available. Stores optional weight
    """
    def __init__(self, head, tail, weight=None):
        self.head = head
        self.tail = tail
        self.weight = weight

    def __item__(self, tag):
        """Use to get weight from edge."""
        if tag == 'weight':
            return self.weight
        return None

    def __str__(self):
        if self.weight:
            return '{} -> {} ({})'.format(self.head, self.tail, self.weight)
        else:
            return '{} -> {}'.format(self.head, self.tail)

class UndirectedGraph:
    """
    Use Dictionary to store all vertices. Values are lists of neighboring nodes.
    """
    def __init__(self):
        self.adjacency = {}
        self.positions = {}
        self.weights   = {}
        self.E         = 0

    def add_node(self, u, pos=None):
        """Add node to graph, if not already there."""
        if u in self.adjacency:
            return
        self.adjacency[u] = None
        self.positions[u] = pos

    def add_nodes_from(self, nodes):
        """Add nodes to graph, if not already there."""
        for n in nodes:
            self.add_node(n)

    def __getitem__(self, u):
        """Get neighboring nodes to this node."""
        for node in self.adjacency[u]:
            yield node

    def number_of_nodes(self):
        """Return number of nodes in graph."""
        return len(self.adjacency)

    def nodes(self):
        """Return all nodes."""
        return self.adjacency.keys()

    def edges(self, u=None, data=True):
        """Return all edges. Make sure not to double count..."""
        all_nodes = list(self.nodes())
        
        if u:
            n = self.adjacency[u]
            while n:
                yield (u, n.value)
                n = n.next
        else:
            seen = []
            for u in all_nodes:
                n = self.adjacency[u]
                while n:
                    if not n.value in seen:
                        yield (u, n.value)
                    n = n.next
                seen.append(u)

    def number_of_edges(self):
        """Return number of edges in graph."""
        return self.E

    def neighbors(self, u):
        """Return neighboring nodes."""
        for node in self.adjacency[u]:
            yield node
    
    def add_edge(self, u, v):
        """Add edge (u,v) to a graph."""
        if not u in self.adjacency:
            self.adjacency[u] = None
            
        if not v in self.adjacency:
            self.adjacency[v] = None

        n = self.adjacency[v]
        while n:
            if n.value == v:
                return   # already there
            n = n.next
            
        self.adjacency[u] = Node(v, self.adjacency[u])
        self.adjacency[v] = Node(u, self.adjacency[v])
        self.E += 1

    def add_edges_from(self, edges):
        """Add edges to graph, if not already there."""
        for u,v in edges:
            self.add_edge(u,v)

class AdjacencyViewer:
    def __init__(self, mat, i, neighbors):
        self.mat = mat
        self.i = i
        self.neighbors = neighbors
        
    def __getitem__(self, target):
        """Get neighboring nodes to this node by iterating over all nodes."""
        for j in self.neighbors:
            if j == target:
                if (self.i, j) in self.mat.weights:
                    return {WEIGHT: self.mat.weights[(self.i,j)]}
                else:
                    return (self.mat.labels[self.i], self.mat.labels[j])

    def __iter__(self):
        for j in self.neighbors:
            if (self.i, j) in self.mat.weights:
                yield {WEIGHT: self.mat.weights[(self.i,j)]}
            else:
                yield self.mat.labels[j]

class MatrixUndirectedGraph:
    NO_EDGE = float('-inf')
    
    """
    Use Two Dimensional Matrix to store whether there is an edge between U and V.
    """
    def __init__(self):
        self.matrix = None
        self.positions = []
        self.labels    = []
        self.weights   = {}
        self.E         = 0

    def add_node(self, u, pos=None):
        """Add node to graph, if not already there."""
        if u in self.labels:
            return
        self.labels.append(u)
        self.positions.append(pos)
        N = len(self.labels)

        # Either initialize 1x1 matrix or extend with new column and one new '0' in each column.
        if self.matrix is None:
            self.matrix =  [[MatrixUndirectedGraph.NO_EDGE] * 1] * 1
        else:
            self.matrix.append([MatrixUndirectedGraph.NO_EDGE] * (N-1))
            for i in range(N):
                self.matrix[i].append(MatrixUndirectedGraph.NO_EDGE)

    def add_nodes_from(self, nodes):
        """Add nodes to graph, if not already there."""
        for n in nodes:
            self.add_node(n)

    def __getitem__(self, u):
        """Get neighboring nodes to this node by iterating over all nodes."""
        idx = self.labels.index(u)
        neighbors = {}
        for j in range(len(self.labels)):
            if self.matrix[idx][j] != MatrixUndirectedGraph.NO_EDGE:
                neighbors[j] = self.matrix[idx][j]
        return AdjacencyViewer(self, idx, neighbors)

    def number_of_nodes(self):
        """Return number of nodes in graph."""
        return len(self.labels)

    def nodes(self):
        """Return all nodes."""
        for n in self.labels:
            yield n

    def edges(self, u=None, data=True):
        """Return all edges. Make sure not to double count..."""
        if u:
            idx = self.labels.index(u)
            for j in range(len(self.labels)):
                if self.matrix[idx][j] != MatrixUndirectedGraph.NO_EDGE:
                    u,v = self.labels[idx], self.labels[j]
                    if (idx,j) in self.weights and data:
                        yield (u, v, {WEIGHT: self.weights[(idx,j)]})
                    else:
                        yield (u, v)
        else:
            for i in range(len(self.labels)-1):
                for j in range(i+1, len(self.labels)):
                    if self.matrix[i][j] != MatrixUndirectedGraph.NO_EDGE:
                        u,v = self.labels[i], self.labels[j]
                        if (i,j) in self.weights and data:
                            yield (u, v, {WEIGHT: self.weights[(i,j)]})
                        else:
                            yield (u, v)

    def get_edge_data(self, u, v):
        """Return weight for edge."""
        if not u in self.labels:
            return None

        if not v in self.labels:
            return None

        i = self.labels.index(u)
        j = self.labels.index(v)
        if self.matrix[i][j] == MatrixUndirectedGraph.NO_EDGE:
            return None
        return {WEIGHT: self.weights[(i,j)]}
        
    def number_of_edges(self):
        """Return number of edges in graph."""
        return self.E

    def neighbors(self, u):
        """Return neighboring nodes."""
        idx = self.labels.index(u)
        for j in range(len(self.labels)):
            if self.matrix[idx][j]:
                yield self.labels[j]

    def add_edge(self, u, v, weight=None):
        """Add edge (u,v) to a graph."""
        if not u in self.labels:
            self.add_node(u)

        if not v in self.labels:
            self.add_node(v)

        if weight == MatrixUndirectedGraph.NO_EDGE:
            raise ValueError('{} is reserved to represent that edge does not exist.'.format(weight))

        # already there
        i = self.labels.index(u)
        j = self.labels.index(v)
        if self.matrix[i][j] != MatrixUndirectedGraph.NO_EDGE:
            return
        self.matrix[i][j] = True
        self.matrix[j][i] = True
        self.E += 1
        if weight:
            self.weights[(i,j)] = weight
            self.weights[(j,i)] = weight

    def add_edges_from(self, edges):
        """Add edges to graph, if not already there."""
        for u,v in edges:
            self.add_edge(u,v)            

class DirectedGraph:
    """
    Use Dictionary to store all vertices. Values are lists of neighboring nodes.
    """
    def __init__(self):
        self.adjacency = {}
        self.positions = {}
        self.weights   = {}
        self.E         = 0
 
    def __contains__(self, v):
        """Determine if v is in the graph."""
        return v in self.adjacency
 
    def add_node(self, u, pos=None):
        """Add node to graph, if not already there."""
        if u in self.adjacency:
            return
        self.adjacency[u] = []
        self.positions[u] = pos

    def add_nodes_from(self, nodes):
        """Add nodes to graph, if not already there."""
        for n in nodes:
            self.add_node(n)

    def __getitem__(self, u):
        """Get neighboring nodes to this node."""
        if u in self.adjacency:
            for node in self.adjacency[u]:
                yield node

    def get_edge_data(self, u, v):
        """Return weight for edge."""
        if not u in self.adjacency:
            return None

        if not v in self.adjacency[u]:
            return None

        return {WEIGHT: self.weights[(u,v)]}

    def nodes(self):
        """Return all nodes."""
        return self.adjacency.keys()

    def number_of_nodes(self):
        """Return number of nodes in graph."""
        return len(self.adjacency)

    def edges(self, u=None, data=True):
        """Return all edges, with weights as optional data."""
        if u:
            for v in self.adjacency[u]:
                if (u,v) in self.weights and data:
                    yield (u, v, {WEIGHT: self.weights[(u,v)]})
                else:
                    yield (u, v)
        else:
            for u in self.nodes():
                for v in self.adjacency[u]:
                    if (u,v) in self.weights and data:
                        yield (u, v, {WEIGHT: self.weights[(u,v)]})
                    else:
                        yield (u, v)

    def number_of_edges(self):
        """Return number of edges in graph."""
        return self.E

    def add_edge(self, u, v, weight=None):
        """Add edge from u => v with optional weight associated with edge."""
        if not u in self.adjacency:
            self.adjacency[u] = []

        if not v in self.adjacency:
            self.adjacency[v] = []

        # already there
        if v in self.adjacency[u]:
            return
        self.adjacency[u].append(v)
        self.E += 1
        if weight:
            self.weights[(u,v)] = weight
            
    def remove_edge(self, u, v):
        """Remove edge from u => v."""
        if not u in self.adjacency:
            return

        if not v in self.adjacency:
            return

        # Not present? leave now
        if not v in self.adjacency[u]:
            return
        
        self.adjacency[u].remove(v)
        self.E -= 1
        if (u,v) in self.weights:
            self.weights((u,v), None)

    def add_edges_from(self, edges):
        """Add edges to graph, if not already there."""
        for edge in edges:
            if len(edge) == 2:
                self.add_edge(edge[0], edge[1])
            else:
                self.add_edge(edge[0], edge[2], edge[3])    # weights

class Graph(MatrixUndirectedGraph):
    def __init__(self):
        MatrixUndirectedGraph.__init__(self)

class DiGraph(DirectedGraph):
    def __init__(self):
        DirectedGraph.__init__(self)

def single_source_shortest_path(self, graph, src):
    """
    Act on Single Source Shortest Path and return path as dictionary, where
    each node is expanded to have its 
    """
    from ch07.dijkstra_sp import dijkstra_sp
    (dist_to, edge_to) = dijkstra_sp(graph, src)
    
    expanded = {}
    for n in graph.nodes():
        if n == src:
            expanded[src] = []
        else:
            path = []
            t = n
            while t != src:
                path.insert(0, t)
                t = edge_to[t][0]
            path.insert(0, src)
            expanded[n] = path
    
    return expanded

def topological_sort(digraph):
    """Link in with Topological sort."""
    from ch07.digraph_search import topological_sort
    return topological_sort(digraph)

def get_node_attributes(graph):
    """I am not going to provide this capability."""
    return graph.positions

def draw(graph, pos, with_labels = True, node_color='w', font_size=8, ax=None):
    """I am not going to provide this capability."""
    pass

def dijkstra_path(G, src, target):
    """Dijkstra delegation."""
    from ch07.dijkstra_sp import dijkstra_sp
    
    return dijkstra_sp(G, src, target)