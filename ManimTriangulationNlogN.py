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

    def value(self, y):
        # Return the x-coordinate of the segment at y
        # y: a number
        # return: a number
        # This was written by an AI!!!
        if y < self.edge[0][1]:
            return self.edge[0][0]
        elif y > self.edge[1][1]:
            return self.edge[1][0]
        else:
            return self.edge[0][0] + (y - self.edge[0][1]) * (self.edge[1][0] - self.edge[0][0]) / (self.edge[1][1] - self.edge[0][1])


class ScanlineBST:
    def __init__(self):
        self.root = None
        self.y = None

    def setY(self, y):
        # Place the scanline at y
        self.y = y

    def insert(self, edge):
        # Parameters:
        # edge: a tuple of 2 points
        # return: A reference to the node that was inserted
        new_node = SegmentNode(edge)
        if self.root is None:
            self.root = new_node
            return
        head = self.root
        while True:
            if new_node.value(self.y) < head.value(self.y):
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

    def find(self, value):
        # Should this take an edge as input?
        head = self.root
        while head is not None:
            if head.value(self.y) == value:
                return head
            else:
                if head.value(self.y) < value:
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
                    if head.right is None:
                        # No children
                        self.root = None
                    else:
                        # Right child only
                        self.root = head.right
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

def Triangulate(points):
    # nlog(n) Triangulation Method
    # points: list of points
    # return: list of triangles
    # TODO: Implement this method

    # DEBUG PLOT
    for i in range(len(points)):
        edge = np.array([points[i-1], points[i]])
        plt.plot(edge[:, 0], edge[:, 1], 'k-')

    # Sort points in order of x (or y)
    sorted_points = np.argsort([x[1] for x in points])[::-1] # descending order
    segments = ScanlineBST()
    sub_polygons = []
    for i in sorted_points:
        point = points[i]
        segments.setY(point[1])
        # what type of point is it?
        # Assume clockwise orientation
        # Scanline travels top to bottom

        # if start vertex:
        tri_points = [points[i-1], point, points[(i+1) % len(points)]]
        c = 'm'
        if IsStartVertex(points, i): # Angle like: /*\
            # add edges to tree
            # Notice, we only care about left edges, right edges face outside, where we don't need triangles
            segments.insert((points[i-1], point))
            c = 'y' # DEBUG PLOT
        elif IsEndVertex(tri_points): # Angle like: \*/
            # look at the vertex's edges
            edge = segments.find(point[0])
            # if helper(edge) is a merge vertex:
            if IsMergeVertex(edge.helper):
                # TODO: add a diagonal from v to helper(edge))
                pass
            # remove edge from tree
            segments.remove(edge)
            c = 'r' # DEBUG PLOT
        elif IsSplitVertex(tri_points): # Angle like: */\*
            # find the edge to it's left
            edge = Segments.findLeftOf(point[0])
            # TODO: add a diagonal from v to helper(edge)
            # set hepder(edge) to v
            edge.helper = point
            # add v's edge to the tree
            segments.insert((point, tri_points[1]))
            c = 'b'
        elif IsMergeVertex(tri_points): # Angle like: *\/*
            # look at the edge terminating at v
            edge = Segments.find((point, tri_points[1]))
            # if helper(edge) is a merge vertex:
            if IsMergeVertex(edge.helper):
                # TODO: add a diagonal from v to helper(edge)
                pass
            # remove edge from tree
            segments.remove(edge)
            # look at the edge to the left of v
            edge = Segments.findLeftOf(point[0])
            # if helper(edge) is a merge vertex:
            if IsMergeVertex(edge.helper):
                # TODO: add a diagonal from v to helper(edge)
                pass
            # helper(edge) = v
            edge.helper = point
            c = 'g' # DEBUG PLOT
        plt.plot(point[0], point[1], 'o', color=c)
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
