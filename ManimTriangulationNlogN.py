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
        # Assume clockwise orientation
        # Scanline travels top to bottom
        # start vertex?
            # both edges point down
            # interior angle is < 180
        # end vertex?
            # both edges point up
            # interior angle is < 180
        # split vertex?
            # both edges point down
            # interior angle is > 180
        # merge vertex?
            # both edges point up
            # interior angle is > 180
        # interior vertex?
            # one edge points up, one points down
            # Does left or right matter?

        # if start vertex:
            # add edges to tree
        # if end vertex:
            # look at the vertex's edges
            # if helper(edge) is a merge vertex:
                # add a diagonal from v to helper(edge)
            # remove edge from tree
        # if split vertex:
            # find the edge to it's left
            # add a diagonal from v to helper(edge)
            # set hepder(edge) to v
            # add v's edges to the tree
        # if merge vertex:
            # look at the edge terminating at v
            # if helper(edge) is a merge vertex:
                # add a diagonal from v to helper(edge)
            # remove edge from tree
            # look at the edge to the left of v
            # if helper(edge) is a merge vertex:
                # add a diagonal from v to helper(edge)
            # helper(edge) = v
        

        # Potentially add edges and split polygons
    
    for polygon in sub_polygons:
        pass
        # Monotone triangulate

def MonotoneTriangulate(points):
    # Check points are monotone
    # Divide into 2 sets, sorted in monotone direction (tbd)
    left_points, right_points = MonotoneSplit(points)
    # Greedy triangulate

    # 2 stacks
    left_stack = []
    right_stack = []

    while True:
        pass
        # if left_points.top() < right_points.top():
            # left_stack.push(left_points.pop())
        # else:
            # right_stack.push(right_points.pop())
        # expect each stack to have 1 element
        # 1 stack may exceed this IF nodes are reflex (angle > 180, sweeping outward)
        # if both stacks have more than 1 element
            # do some triangulating

        # how to terminate?
