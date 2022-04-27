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
        pass

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
        pass

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
        if IsStartVertex(tri_points):
            # add edges to tree
            # Notice, we only care about left edges, right edges face outside, where we don't need triangles
            segments.insert((points[i-1], point))

            c = 'y' # DEBUG PLOT
        elif IsEndVertex(tri_points):
            # look at the vertex's edges
            edge = segments.find((points[i-1], point))
            # if helper(edge) is a merge vertex:
            if IsMergeVertex(edge.helper):
                # TODO: add a diagonal from v to helper(edge)
                pass
            # remove edge from tree
            segments.remove(edge)
            c = 'r' # DEBUG PLOT
        elif IsSplitVertex(tri_points):
            # find the edge to it's left
            edge = Segments.findLeftOf(point[0])
            # TODO: add a diagonal from v to helper(edge)
            # set hepder(edge) to v
            edge.helper = point
            # add v's edge to the tree
            segments.insert((point, tri_points[1]))
            c = 'b'
        elif IsMergeVertex(tri_points):
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
