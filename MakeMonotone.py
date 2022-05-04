# This script is a manim animation showcasing an algorithm to break down a polygon into monotone sub-polygons in nlog(n) time.
from manim import *
import numpy as np
import json


# Configuration
POLYGON = json.load(open("polygons.json"))
KEY = 'sharp2'
POINTS = POLYGON[KEY]
SCENE = None
TIME_SHORT = 0.5

# Manim Config
config.max_files_cached = 512
config.output_file = f'MakeMontone_{KEY}.mp4'

messages = []
def ClearMessage():
    global messages
    if messages:
        SCENE.play(*[FadeOut(x) for x in messages], run_time=TIME_SHORT)
        messages = []

def UpdateMessage(lines):
    global messages
    if type(lines) == str:
        lines = [lines]
    ClearMessage()
    messages.append(Text(lines[0]).shift(2.5 * DOWN))
    for i in range(1, len(lines)):
        messages.append(Text(lines[i]).next_to(messages[-1], DOWN))
    SCENE.play(*[Write(x) for x in messages], run_time=TIME_SHORT)
    SCENE.wait()

class MakeMonotoneAnimation(Scene):
    def construct(self):
        global SCENE
        SCENE = self
        primary_polygon = Polygon(*[x + [0]  for x in POINTS], color=PURPLE_B)
        self.add(primary_polygon)
        MakeMonotone(self, POINTS)


def AddDiagonal(points, i, j):
    diagonal_line = Line(points[i] + [0], points[j] + [0], color=BLUE)
    global SCENE
    SCENE.play(Create(diagonal_line))


def MakeMonotone(self, points):
    # Parameters:
    #   points: list of points
    # Return: list of triangles
    # Assume clockwise orientation
    # Scanline travels top to bottom

    # Manim Object
    ScanLineLine = lambda y: Line([-10, y, 0], [10, y, 0], color=RED)
    scanline = ScanLineLine(10)
    scanline_point = Dot([-10, 10, 0], color=RED)

    # Init scene
    self.add(scanline)
    self.add(scanline_point)
    # Sort by y
    # TODO: Resolve tie breakers in a better way
    sorted_points = np.argsort([x[1] - (0.001 * x[0]) for x in points])[::-1] # descending order

    UpdateMessage('Sort points by Y')
    sorted_dots = []
    actions = []
    for idx in sorted_points:
        sorted_dots.append(Dot(points[idx] + [0], color=BLUE))
        actions.append(Create(sorted_dots[-1]))
    self.play(*actions)
    actions = []
    for i, idx in enumerate(sorted_points):
        actions.append(Transform(sorted_dots[i], Dot([0, points[idx][1], 0], color=BLUE).to_edge(RIGHT, buff=1)))
    self.play(*actions)

    segments = ScanlineBST(self)
    for idx in sorted_points:
        prev_point, point, next_point = points[idx-1], points[idx], points[(idx+1) % len(points)]
        segments.setY(point[1])
        self.play(
            Transform(scanline, ScanLineLine(point[1])),
            Transform(scanline_point, Dot(point + [0], color=RED)),
        )
        self.play(Uncreate(sorted_dots.pop(0)))
        # what type of point is it?
        VertexDot = lambda c: Dot(point + [0], color=c)
        AddVertexDot = lambda c: self.play(Create(VertexDot(c)))
        if IsStartVertex(points, idx): # Angle like: /*\
            # add left edge to tree. We dont care about the right edge. It faces out.
            UpdateMessage(['This point is a start vertex', 'Add it\'s left edge to the tree'])
            AddVertexDot(YELLOW)
            node = segments.insert((point, prev_point), helper=idx) # must point edge downwards
        elif IsEndVertex(points, idx): # Angle like: \*/
            # look at the vertex's edges
            UpdateMessage(['This point is an end vertex', 'Check the helper of the left edge'])
            AddVertexDot(RED)
            edge = segments.find(point)
            if IsMergeVertex(points, edge.helper):
                UpdateMessage('The helper is a merge vertex. Add a diagonal')
                AddDiagonal(points, idx, edge.helper)
            else:
                UpdateMessage('The helper is not a merge vertex.')
            segments.delete(edge) # remove edge from tree
        elif IsSplitVertex(points, idx): # Angle like: */\*
            # find the edge to it's left
            UpdateMessage(['This point is a split vertex'])
            AddVertexDot(BLUE)
            edge = segments.findLeftOf(point)
            if edge.helper: # TODO: Why would it be None?
                UpdateMessage('Add a diagonal to this edge\'s helper')
                AddDiagonal(points, idx, edge.helper) # Found a diagonal!
            edge.set_helper(idx)
            UpdateMessage('Add the vertex\'s right edge to the tree.')
            segments.insert((point, prev_point)) # must point edge downwards
        elif IsMergeVertex(points, idx): # Angle like: *\/*
            # look at the edge terminating at v
            UpdateMessage(['This point is a merge vertex', 'Check the helper of it\'s right edge'])
            AddVertexDot(GREEN)
            edge = segments.find(point)
            if IsMergeVertex(points, edge.helper):
                UpdateMessage('The helper is a merge vertex. Add a diagonal.')
                AddDiagonal(points, idx, edge.helper) # Found a diagonal!
            else:
                UpdateMessage('The helper is not a merge vertex.')
            segments.delete(edge)
            # look at the edge to the left of v
            edge = segments.findLeftOf(point)
            if IsMergeVertex(points, edge.helper):
                UpdateMessage('This edge\'s helper is a merge vertex. Add a diagonal.')
                AddDiagonal(points, idx, edge.helper) # Found a diagonal!
            edge.set_helper(idx) # update helper
        else: # Interior point
            edge_node = segments.find(point)
            if edge_node is not None: # TODO: Is there a better condition to use?
                UpdateMessage(['This point is an left interior vertex'])
                edge = edge_node.edge
                if IsMergeVertex(points, edge_node.helper):
                    AddDiagonal(points, idx, edge_node.helper) # Found a diagonal!
                UpdateMessage(['Remove the edge above', 'Add the edge below'])
                segments.delete(edge_node, verbose=False)
                node = segments.insert((point, prev_point), helper=idx)
            else:
                UpdateMessage(['This point is an right interior vertex'])
                edge = segments.findLeftOf(point)
                if IsMergeVertex(points, edge.helper):
                    UpdateMessage('This helper is a merge vertex. Add a diagonal.')
                    AddDiagonal(points, idx, edge.helper) # Found a diagonal!
                edge.set_helper(idx)
    UpdateMessage(['The polygon is now composed', 'of monotone sub-polygons.'])
    # TODO: Triangulate monotone subpolygons
    return

#
# Helpers
#
def InteriorAngle(a, b):
    # Parameters: a, b: Vectors
    # Return: Angle in degrees from a to b in clockwise direction
    angle = np.arctan2(a[1], a[0]) - np.arctan2(b[1], b[0])
    if angle > 2 * np.pi:
        angle -= 2 * np.pi
    if angle < 0:
        angle += 2 * np.pi
    return angle

def EdgesAtPoint(points, i):
    # Parameters:
    #   points: list of points of a polygon
    #   i: index of a point
    # return: 2 vectors representing point -> previous_point, point -> next_point
    a, b, c = points[i-1], points[i], points[(i+1) % len(points)]
    return np.subtract(a, b), np.subtract(c, b)

def IsStartVertex(points, i):
    # Parameters:
    #   points: list of points of a polygon
    #   i: index of point to check
    # Assumes clockwise orientation
    if i is None: return False
    v1, v2 = EdgesAtPoint(points, i)
    if v1[1] < 0 and v2[1] <= 0: # both edges point down
        if InteriorAngle(v2, v1) < np.pi: # angle < 180 degrees
            return True
    return False

def IsEndVertex(points, i):
    if i is None: return False
    v1, v2 = EdgesAtPoint(points, i)
    if v1[1] > 0 and v2[1] > 0: # both edges point up
        if InteriorAngle(v2, v1) < np.pi: # angle is < 180 degrees
            return True
    return False

def IsSplitVertex(points, i):
    if i is None: return False
    v1, v2 = EdgesAtPoint(points, i)
    if v1[1] < 0 and v2[1] <= 0: # both edges point down
        if InteriorAngle(v2, v1) > np.pi: # angle is > 180 degrees
            return True
    return False

def IsMergeVertex(points, i):
    if i is None: return False
    v1, v2 = EdgesAtPoint(points, i)
    if v1[1] > 0 and v2[1] > 0: # both edges point up
        if InteriorAngle(v2, v1) > np.pi: # angle > 180
            return True
    return False

#
# Helper Classes
#
class SegmentNode:
    def __init__(self, edge, left=None, right=None, helper=None):
        # Parameters:
        #   edge: a tuple of 2 points
        #   left: a SegmentNode
        #   right: a SegmentNode
        #   helper: INT, An index
        self.edge = edge
        self.left = left
        self.right = right
        self.helper = helper
        self.helper_mobject = None

        # Animate node addition
        edge_line = Line(edge[0] + [0], edge[1] + [0], color=YELLOW, stroke_width=5)
        SCENE.play(Create(edge_line))
        self.mobject = edge_line

        

    def value(self, y):
        # Return the x-coordinate of the segment at a given y
        # y: a number
        # return: a number
        # This function was written by an AI!
        if y >= self.edge[0][1]:
            return self.edge[0][0]
        elif y <= self.edge[1][1]:
            return self.edge[1][0]
        else:
            return self.edge[0][0] + (self.edge[1][0] - self.edge[0][0]) * (y - self.edge[0][1]) / (self.edge[1][1] - self.edge[0][1])

    def InOrder(self):
        # Return a list of all SegmentNodes in order
        left, right = [], []
        if self.left is not None:
            left = self.left.InOrder()
        if self.right is not None:
            right = self.right.InOrder()
        return left + [self] + right

    def set_helper(self, helper):
        # Parameters:
        #   helper: INT, An index
        UpdateMessage(['Update the edge\'s helper'])
        self.helper = helper
        helper_point = POINTS[helper]
        new_helper_line = Line([self.value(helper_point[1]), helper_point[1]] + [0], helper_point + [0], color=GREEN, stroke_width=5)
        if self.helper_mobject is not None:
            SCENE.play(Transform(self.helper_mobject, new_helper_line))
        else:
            SCENE.play(Create(new_helper_line))
            self.helper_mobject = new_helper_line
        return


class ScanlineBST:
    # A ScanlineBST is a binary search tree of SegmentNodes.
    # Each node has an edge composed of 2 points.
    # Nodes are sorted by x coodinate AT A GIVEN Y - the scanline.

    # TODO: This tree has no balancing constraints.
    # Operations may run in O(n) time!

    def __init__(self, scene):
        # Parameters:
        #   scene: a Manim Scene object
        self.root = None
        self.y = None
        self.scene = scene

    def __repr__(self):
        if self.root is None:
            return 'ScanlineBST(None)'
        return f'ScanlineBST({[x.edge[1] for x in self.root.InOrder()]})'

    def setY(self, y):
        # Place the scanline at y
        # TODO: deprecate this.
        self.y = y

    def insert(self, edge, **kwargs):
        # Parameters:
        #   edge: a tuple of 2 points
        # Return a reference to the node that was inserted
        # Assume edges always point down.
        assert(edge[0][1] > edge[1][1])

        new_node = SegmentNode(edge, **kwargs)

        if self.root is None: # Empty tree
            self.root = new_node
            return new_node
        # Find the node to insert after
        head = self.root
        while True:
            if edge[0][0] < head.value(edge[0][1]):
                if head.left is None:
                    head.left = new_node # Insert here
                    break
                head = head.left
            else:
                if head.right is None:
                    head.right = new_node # or insert here
                    break
                head = head.right
        return new_node

    def find(self, point):
        # Parameters:
        #   point: (x, y) coordinates
        # Returns a SegmentNode if the point lies on it's edge
        # TODO: This is an imprecise way to address nodes.
        x, y = point
        head = self.root
        while head is not None:
            if head.value(y) == x:
                return head
            else:
                if x < head.value(y):
                    head = head.left
                else:
                    head = head.right
        # Not found
        return None

    def findLeftOf(self, point):
        # Parameters:
        #   point: (x, y) coordinates
        # Returns the SegmentNode that is the left of the point
        # TODO: [low priority] Is there an easy way to ignore edges landing on this point?
        UpdateMessage('Find the edge to the left of the node')
        x, y = point
        head = self.root
        best_fit = None
        while head is not None:
            if head.value(y) <= x:
                best_fit = head
                head = head.right
            else:
                head = head.left
        endpoint = [best_fit.value(y), y]
        query_line = Line(point + [0], endpoint + [0], color=GOLD, stroke_width=5)
        self.scene.play(Create(query_line))
        self.scene.play(Uncreate(query_line))
        return best_fit

    def delete(self, value, verbose=True):
        # Parameters:
        #   value: a number OR a SegmentNode
        if verbose:
            UpdateMessage('Remove an edge from the tree')
        if type(value) == SegmentNode: # Get node value
            value = value.value(self.y)
        head = self.root
        parent = None
        while head is not None: # Find the node to delete
            if not head.value(self.y) == value: # Not found
                # Traverse deeper in the tree
                parent = head
                if head.value(self.y) < value:
                    head = head.right
                else:
                    head = head.left
            else: # Found it!
                # Patch the children and possibly the root
                if head.left is None: # No left child, easy patch!
                    if parent is None: # head is root
                        self.root = head.right
                    elif parent.left == head: # head is left child
                        parent.left = head.right
                    else: # head is right child
                        parent.right = head.right
                else: # Left child exists
                    # Goal: Replace head with the max of head's left subtree
                    left_child = head.left
                    left_child_parent = head
                    while left_child.right is not None:
                        left_child_parent = left_child
                        left_child = left_child.right
                    # Now left_child is the rightmost node (maximum) of the left-subtree
                    # Patch in the left child
                    left_child.right = head.right
                    if left_child_parent != head:
                        left_child.left = head.left
                        left_child_parent.right = None
                    if parent is None: # head is root
                        self.root = left_child # Now left_child is the new root
                    elif parent.left == head: # head is left child
                        parent.left = left_child
                    else: # head is right child
                        parent.right = left_child
                if head.mobject:
                    actions = [Uncreate(head.mobject)]
                    if head.helper_mobject is not None:
                        actions.append(Uncreate(head.helper_mobject))
                    self.scene.play(*actions)
                else:
                    print('No mobject')
                return
        assert head is not None # Nothing to delete
