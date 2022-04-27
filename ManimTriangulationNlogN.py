from manim import *
import numpy as np
import json

from matplotlib import pyplot as plt


# Configuration
POLYGON = json.load(open("polygons.json"))
KEY = 'large'
POINTS = POLYGON[KEY]


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

    # DEBUG PLOT
    for i in range(len(points)):
        edge = np.array([points[i-1], points[i]])
        plt.plot(edge[:, 0], edge[:, 1], 'k-')

    # Sort points in order of x (or y)
    # TODO: We can probably use arg sort instead.
    sorted_points = np.argsort([x[0] for x in points])
    segments = BST()
    sub_polygons = []
    for i in sorted_points:
        point = points[i]
        # what type of point is it?
        # Assume clockwise orientation
        # Scanline travels top to bottom

        # if start vertex:
        tri_points = [points[i-1], point, points[(i+1) % len(points)]]
        c = 'm'
        if IsStartVertex(tri_points):
            # add edges to tree
            c = 'y' # DEBUG PLOT
        elif IsEndVertex(tri_points):
            # look at the vertex's edges
            # if helper(edge) is a merge vertex:
                # add a diagonal from v to helper(edge)
            # remove edge from tree
            c = 'r' # DEBUG PLOT
        elif IsSplitVertex(tri_points):
            # find the edge to it's left
            # add a diagonal from v to helper(edge)
            # set hepder(edge) to v
            # add v's edges to the tree
            c = 'b'
        elif IsMergeVertex(tri_points):
            # look at the edge terminating at v
            # if helper(edge) is a merge vertex:
                # add a diagonal from v to helper(edge)
            # remove edge from tree
            # look at the edge to the left of v
            # if helper(edge) is a merge vertex:
                # add a diagonal from v to helper(edge)
            # helper(edge) = v
            c = 'g'
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

def IsStartVertex(tri_points):
    # Parameters:
    # tri_points: list of 3 points, query vertex is tri_points[1]
    # Assumes clockwise orientation
    a, b, c = tri_points
    v1 = np.subtract(a, b)
    v2 = np.subtract(c, b)
    # both edges point down
    if v1[1] < 0 and v2[1] <= 0:
        angle = InteriorAngle(v2, v1)
        # assert angle > 0
        if angle < np.pi:
            return True
    return False

def IsEndVertex(tri_points):
    a, b, c = tri_points
    v1 = np.subtract(a, b)
    v2 = np.subtract(c, b)
    # both edges point up
    if v1[1] > 0 and v2[1] > 0:
        angle = InteriorAngle(v2, v1)
        # assert angle > 0
        if angle < np.pi:
            return True
    return False

def IsSplitVertex(tri_points):
    a, b, c = tri_points
    v1 = np.subtract(a, b)
    v2 = np.subtract(c, b)
    if v1[1] < 0 and v2[1] <= 0:
        angle = InteriorAngle(v2, v1)
        # assert angle > 0
        if angle > np.pi:
            return True
    return False

def IsMergeVertex(tri_points):
    a, b, c = tri_points
    v1 = np.subtract(a, b)
    v2 = np.subtract(c, b)
    if v1[1] > 0 and v2[1] > 0:
        angle = InteriorAngle(v2, v1)
        # assert angle > 0
        if angle > np.pi:
            return True
    return False

# interior vertex?
    # one edge points up, one points down
    # Does left or right matter?


if __name__ == "__main__":
    Triangulate(POINTS)
