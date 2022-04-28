from manim import *
import numpy as np
import json

from matplotlib import pyplot as plt


# Configuration
POLYGON = json.load(open("polygons.json"))
KEY = 'large'
POINTS = POLYGON[KEY]


class SegmentNode:
    def __init__(self, edge, left=None, right=None):
        # Parameters:
        # edge: a tuple of 2 points
        self.edge = edge
        self.left = left
        self.right = right
        self.helper = None

    def value(self, y):
        # Return the x-coordinate of the segment at y
        # y: a number
        # return: a number
        if y >= self.edge[0][1]:
            return self.edge[0][0]
        elif y <= self.edge[1][1]:
            return self.edge[1][0]
        else:
            return self.edge[0][0] + (self.edge[1][0] - self.edge[0][0]) * (y - self.edge[0][1]) / (self.edge[1][1] - self.edge[0][1])

    def InOrder(self):
        left, right = [], []
        if self.left is not None:
            left = self.left.InOrder()
        if self.right is not None:
            right = self.right.InOrder()
        return left + [self] + right


class ScanlineBST:
    def __init__(self):
        self.root = None
        self.y = None

    def __repr__(self):
        if self.root is None:
            return 'ScanlineBST(None)'
        return f'ScanlineBST({[x.edge[1] for x in self.root.InOrder()]})'

    def setY(self, y):
        # Place the scanline at y
        self.y = y

    def insert(self, edge):
        # Parameters:
        # edge: a tuple of 2 points
        # return: A reference to the node that was inserted
        # Assume edges always point down.
        print('insert', edge)

        # DEBUG PLOT
        plt.plot([edge[0][0], edge[1][0]], [edge[0][1], edge[1][1]], 'r-')

        new_node = SegmentNode(edge)
        if self.root is None:
            self.root = new_node
            return new_node
        head = self.root
        while True:
            if edge[0][0] < head.value(edge[0][1]):
                if head.left is None:
                    head.left = new_node
                    break
                head = head.left
            else:
                if head.right is None:
                    head.right = new_node
                    break
                head = head.right
        return new_node

    def find(self, point):
        # Should this take an edge as input?
        x, y = point
        head = self.root
        while head is not None:
            print('comparing', head.value(y), head.edge[1], y)
            if head.value(y) == x:
                return head
            else:
                if x < head.value(y):
                    head = head.left
                else:
                    head = head.right
        # Not found
        return None

    def findLeftOf(self, value):
        head = self.root
        best_fit = None
        while head is not None:
            if head.value(self.y) <= value:
                best_fit = head
                head = head.right
            else:
                head = head.left
        return best_fit

    def delete(self, value):
        print('delete', value)
        if type(value) == SegmentNode:
            value = value.value(self.y)
            print('delete value', value)
        head = self.root
        parent = None
        while head is not None:
            if head.value(self.y) == value:
                # Found the thing to delete
                # Need to patch in the children
                # and possibly the root
                # TODO
                to_delete = head
                if head.left is None:
                    # No left child, easy patch
                    if parent is None:
                        self.root = head.right
                        return
                    if parent.left == head:
                        parent.left = head.right
                        return
                    else:
                        parent.right = head.right
                        return
                else:
                    # Left child, need to find the rightmost node
                    # of the left child
                    left_child = head.left
                    left_child_parent = head
                    while left_child.right is not None:
                        left_child_parent = left_child
                        left_child = left_child.right
                    # Now left_child is the rightmost node of the left child
                    # We can patch in the left child
                    left_child.right = head.right
                    if left_child_parent != head:
                        left_child.left = head.left
                        left_child_parent.right = None
                    if parent is None:
                        self.root = left_child
                        return
                    if parent.left == head:
                        parent.left = left_child
                        return
                    else:
                        parent.right = left_child
                        return
                break
            else:
                parent = head
                if head.value(self.y) < value:
                    head = head.right
                else:
                    head = head.left
        if head is None:
            # Didn't find the node to delete
            assert(False)

def AddDiagonal(points, i, j):
    plt.plot([points[i][0], points[j][0]], [points[i][1], points[j][1]], 'c-')

def Triangulate(points):
    # nlog(n) Triangulation Method
    # points: list of points
    # return: list of triangles
    # TODO: Implement this method

    # DEBUG PLOT
    for i in range(len(points)):
        edge = np.array([points[i-1], points[i]])
        plt.plot(edge[:, 0], edge[:, 1], 'k-')

    # Sort by y
    # TODO: Resolve tie breakers in a better way
    sorted_points = np.argsort([x[1] - (0.001 * x[0]) for x in points])[::-1] # descending order
    segments = ScanlineBST()
    sub_polygons = []
    diagonals = []
    for idx in sorted_points:
        print(' ')
        prev_point, point, next_point = points[idx-1], points[idx], points[(idx+1) % len(points)]

        segments.setY(point[1])
        # what type of point is it?
        # Assume clockwise orientation
        # Scanline travels top to bottom

        c = 'm' # DEBUG PLOT
        if IsStartVertex(points, idx): # Angle like: /*\
            # add left edge to tree. We dont care about the right edge. It faces out.
            node = segments.insert((point, prev_point)) # must point edge downwards
            node.helper = idx
            c = 'y' # DEBUG PLOT
        elif IsEndVertex(points, idx): # Angle like: \*/
            # # look at the vertex's edges
            edge = segments.find(point)
            # if helper(edge) is a merge vertex:
            if IsMergeVertex(points, edge.helper):
                # add a diagonal from v to helper(edge))
                AddDiagonal(points, idx, edge.helper)
                pass
            # remove edge from tree
            segments.delete(edge)
            c = 'r' # DEBUG PLOT
        elif IsSplitVertex(points, idx): # Angle like: */\*
            # find the edge to it's left
            edge = segments.findLeftOf(point[0])
            # add a diagonal from v to helper(edge)
            if edge.helper:
                AddDiagonal(points, idx, edge.helper)
            # set hepder(edge) to v
            edge.helper = idx
            # add v's edge to the tree
            segments.insert((point, prev_point)) # must point edge downwards
            c = 'b'
        elif IsMergeVertex(points, idx): # Angle like: *\/*
            # # look at the edge terminating at v
            edge = segments.find(point)
            # if helper(edge) is a merge vertex:
            if IsMergeVertex(points, edge.helper):
                # add a diagonal from v to helper(edge)
                AddDiagonal(points, idx, edge.helper)
            # delete edge from tree
            segments.delete(edge)
            # look at the edge to the left of v
            edge = segments.findLeftOf(point[0])
            # if helper(edge) is a merge vertex:
            if IsMergeVertex(points, edge.helper):
                # Add a diagonal from v to helper(edge)
                AddDiagonal(points, idx, edge.helper)
            edge.helper = idx
            c = 'g' # DEBUG PLOT
        else: # Interior point
            edge_node = segments.find(point)
            if edge_node is not None:
                # DEBUG PLOT
                edge = edge_node.edge
                plt.plot([edge[0][0], edge[1][0]], [edge[0][1], edge[1][1]], 'm-')
                segments.delete(edge_node)
                node = segments.insert((point, prev_point))
                node.helper = idx
                c = 'c'
            else:
                left_edge = segments.findLeftOf(point[0])
                left_edge.helper = idx
        plt.plot(point[0], point[1], 'o', color=c)
        plt.show(block=False)
        plt.pause(0.1)
        x = input('press enter to continue')
    plt.show()
    
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

#
# Helpers
#
def InteriorAngle(a, b):
    # v1, v2: vectors
    # return: angle in degrees
    # Define Interior:
    # Assume clockwise orientation
    # v1 points backwards, v2 points forwards
    # left of v1 and right of v2 is interior.
    angle = np.arctan2(a[1], a[0]) - np.arctan2(b[1], b[0])
    if angle > 2 * np.pi:
        angle -= 2 * np.pi
    if angle < 0:
        angle += 2 * np.pi
    return angle

def EdgesAtPoint(points, i):
    # return: 2 vectors representing point -> previous_point, point -> next_point
    a, b, c = points[i-1], points[i], points[(i+1) % len(points)]
    return np.subtract(a, b), np.subtract(c, b)

def IsStartVertex(points, i):
    # Parameters:
    # points: list of points
    # i: index of point to check
    # Assumes clockwise orientation
    if i is None: return False
    v1, v2 = EdgesAtPoint(points, i)
    if v1[1] < 0 and v2[1] <= 0: # both edges point down
        angle = InteriorAngle(v2, v1)
        if angle < np.pi: # angle < 180 degrees
            return True
    return False

def IsEndVertex(points, i):
    if i is None: return False
    v1, v2 = EdgesAtPoint(points, i)
    if v1[1] > 0 and v2[1] > 0: # both edges point up
        angle = InteriorAngle(v2, v1)
        if angle < np.pi: # angle is < 180 degrees
            return True
    return False

def IsSplitVertex(points, i):
    if i is None: return False
    v1, v2 = EdgesAtPoint(points, i)
    if v1[1] < 0 and v2[1] <= 0: # both edges point down
        angle = InteriorAngle(v2, v1)
        if angle > np.pi: # angle is > 180 degrees
            return True
    return False

def IsMergeVertex(points, i):
    if i is None: return False
    v1, v2 = EdgesAtPoint(points, i)
    if v1[1] > 0 and v2[1] > 0: # both edges point up
        angle = InteriorAngle(v2, v1)
        if angle > np.pi: # angle > 180
            return True
    return False


if __name__ == "__main__":
    Triangulate(POINTS)
