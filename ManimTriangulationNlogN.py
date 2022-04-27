class Node:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right


class BST:
    def __init__(self):
        self.root = None


def Triangulate(points):
    # nlog(n) Triangulation Method
    # points: list of points
    # return: list of triangles
    # TODO: Implement this method

    # Sort points in order of x (or y)
    trees = BST()
    sub_polygons = []
    for point in points:
        pass
        # what type of point is it?
        # start vertex? both edges point up
        # end vertex? both edges point down
        # side vertex? one edge points up, one points down (left or right?)
        # if start or end vertex, add to tree
        # if a side vertex, attach at node in the tree
            # is this the closest node?
            # does left/right matter?

        # Potentially add edges and split polygons
    
    for polygon in sub_polygons:
        pass
        # Monotone triangulate

def MonotoneTriangulate(points):
    # Check points are monotone
    # Divide into 2 sets
    # Greedy triangulate
