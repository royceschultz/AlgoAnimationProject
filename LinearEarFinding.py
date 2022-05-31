from manim import *
import numpy as np
import json

np.random.seed(43)

# DEBUG
import matplotlib.pyplot as plt

POLYGONS = json.load(open("polygons.json"))
KEY = 'medium'
POINTS = POLYGONS[KEY]
TIME_SHORT = 0.2
VERBOSE = True

# Manim Config
config.max_files_cached = 512
config.output_file = f'LTEF_{KEY}.mp4'


messages = []
def ClearMessage():
    global messages
    if messages:
        SCENE.play(*[FadeOut(x) for x in messages], runtime=TIME_SHORT)
        messages = []

def UpdateMessage(lines):
    if not VERBOSE:
        return
    global messages
    if type(lines) == str:
        lines = [lines]
    ClearMessage()
    messages.append(Text(lines[0]).shift(2.5 * DOWN))
    for i in range(1, len(lines)):
        messages.append(Text(lines[i]).next_to(messages[-1], DOWN))
    SCENE.play(*[Write(x) for x in messages], runtime=TIME_SHORT)
    SCENE.wait(TIME_SHORT)

# Assume a method to find diagonals in linear time
# (Covered in other animations)
def FindDiagonalFrom(point_idx, points):
    possible_diagonals = []
    i = point_idx + 2
    while i < len(points):
        possible_diagonals.append(i)
        i += 1
    i = 0
    while i < point_idx - 1:
        possible_diagonals.append(i)
        i += 1
    # Shuffle the list
    np.random.shuffle(possible_diagonals)
    for i in possible_diagonals:
        if IsDiagonal(i, point_idx, points):
            return i
    raise 'No Diagonal Exists'

def IsDiagonal(a, b, points):
    diagonal = (points[a], points[b])
    # Check if the diagonal is on the interior of the polygon
    edge_next = (points[a], points[(a + 1) % len(points)])
    edge_prev = (points[a], points[(a - 1) % len(points)])
    EdgeVector = lambda s: np.subtract(s[1], s[0])
    poly_angle = CalculateAngle(EdgeVector(edge_next), EdgeVector(edge_prev))
    diagonal_angle = CalculateAngle(EdgeVector(edge_next), EdgeVector(diagonal))
    if diagonal_angle > poly_angle:
        return False
    # Check if the diagonal intersects any of the lines
    for i in range(len(points)):
        # If edge starts/ends at the diagonal, skip
        if i == a or i == b or i-1 == a or i-1 == b:
            continue
        edge = (points[i-1], points[i])
        edge_line = Line(edge[0] + [0], edge[1] + [0], color=RED)
        if IsIntersect(edge, diagonal):
            return False
    return True

def IsIntersect(line1, line2):
    # Parameters:
    # line1, line2: Line segments like [(x1, y1), (x2, y2)]
    # Returns: True if the lines intersect, else false
    (x1, y1), (x2, y2) = line1
    (x3, y3), (x4, y4) = line2
    slope1 = (y2 - y1) / (x2 - x1)
    slope2 = (y4 - y3) / (x4 - x3)
    intercept1 = y1 - slope1 * x1
    intercept2 = y3 - slope2 * x3
    if slope1 == slope2: # Parallel lines
        if intercept1 == intercept2:
            return True
        return False
    x_intersect = (intercept2 - intercept1) / (slope1 - slope2)
    if x_intersect >= min(x1, x2) and x_intersect <= max(x1, x2):
        if x_intersect >= min(x3, x4) and x_intersect <= max(x3, x4):
            return True
    return False

def CalculateAngle(a, b):
    # Returns clockwise angle between [0, 2 * pi]
    # a, b: vectors
    angle = np.arctan2(a[1], a[0]) - np.arctan2(b[1], b[0])
    if angle > 2 * np.pi:
        angle -= 2 * np.pi
    if angle < 0:
        angle += 2 * np.pi
    return angle

def PartitionPoints(points, i, j):
    # Parameters:
    # points: list of points
    # i, j: Indices of a diagonal of a polygon.
    # Returns:
    # left, right: lists of points from each side of the partition
    if i > j: # Sort to avoid symmetric case
        i, j = j, i
    left = points[i:j+1]
    right = points[j:len(points)] + points[0:i+1]
    print(len(points), len(left), len(right))
    return left, right

def FindGoodSubPolygon(points, i, j):
    # Parameters:
    # points: list of points
    # i, j: Indices of a diagonal of a polygon.
    global SCENE
    left, right = PartitionPoints(points, i, j)
    # Search the smaller side
    UpdateMessage('Pick the smaller side')
    good_sub_polygon, bad_sub_polygon = left, right
    go_left = True
    if len(right) < len(left):
        good_sub_polygon, bad_sub_polygon = right, left
        go_left = False
    # Animate polygon partition
    gsp_polygon = Polygon(*[x + [0] for x in good_sub_polygon])
    bsp_polygon = Polygon(*[x + [0] for x in bad_sub_polygon])
    gsp_polygon.set_fill(GREEN, opacity=0.3)
    bsp_polygon.set_fill(RED, opacity=0.3)
    SCENE.play(FadeIn(gsp_polygon), FadeIn(bsp_polygon))
    
    UpdateMessage('Find the middle point.')
    SCENE.play(FadeOut(gsp_polygon)) # Clean up GSP animation

    middle_index = len(good_sub_polygon) // 2
    # animate finding middle index
    a, b = i, j
    for i in range(middle_index):
        a_dot = Dot(points[a] + [0], color=GREEN, radius=0.5, fill_opacity=0.3)
        b_dot = Dot(points[b] + [0], color=GREEN, radius=0.5, fill_opacity=0.3)
        SCENE.play(FadeIn(a_dot), FadeIn(b_dot))
        SCENE.play(FadeOut(a_dot), FadeOut(b_dot))
        if go_left:
            a = (a + 1) % len(points)
            b = (b - 1) % len(points)
        else:
            a = (a - 1) % len(points)
            b = (b + 1) % len(points)

    middle_dot = Dot(good_sub_polygon[middle_index] + [0], color=GREEN, radius=0.5, fill_opacity=0.3)
    SCENE.play(FadeIn(middle_dot))
    SCENE.play(FadeOut(middle_dot))
    UpdateMessage('Find a diagonal from the partition point.')
    try:
        d = FindDiagonalFrom(middle_index, good_sub_polygon)
    except:
        # Is this necessary? I don't think so.
        # Pretty sure this implies middle_index is an ear.
        # Could exit early instead.
        try:
            middle_index += 1
            d = FindDiagonalFrom(middle_index, good_sub_polygon)
        except:
            print(len(good_sub_polygon), len(bad_sub_polygon))
            raise
    diagonal_line = Line(good_sub_polygon[middle_index] + [0], good_sub_polygon[d] + [0])
    SCENE.play(Create(diagonal_line))
    return good_sub_polygon, middle_index, d


# Manim Global Variables
SCENE = None


class LinearTimeEarFinding(Scene):
    def construct(self):
        global SCENE
        SCENE = self
        primary_polygon = Polygon(*[x + [0]  for x in POINTS], color=PURPLE)
        self.add(primary_polygon)
        FindEar(POINTS)

def FindEar(points):
    # Find a diagonal, any diagonal.
    UpdateMessage('Find a diagonal in linear time.')
    a = 0
    try:
        b = FindDiagonalFrom(a, POINTS)
        # Possibly no diagonal exists from a
    except: # Try again, guaranteed to work
        a = 1
        b = FindDiagonalFrom(a, POINTS)
    diagonal_line = Line(points[a] + [0], points[b] + [0])
    SCENE.play(Create(diagonal_line))
    sub_polygon = POINTS
    while True:
        sub_polygon, a, b = FindGoodSubPolygon(sub_polygon, a, b)
        left, right = PartitionPoints(sub_polygon, a, b)
        if min(len(left), len(right)) <= 3:
            break
    good_sub_polygon, bad_sub_polygon = left, right
    if len(right) < len(left):
        good_sub_polygon, bad_sub_polygon = right, left
    gsp_polygon = Polygon(*[x + [0] for x in good_sub_polygon])
    bsp_polygon = Polygon(*[x + [0] for x in bad_sub_polygon])
    gsp_polygon.set_fill(GREEN, opacity=0.3)
    bsp_polygon.set_fill(RED, opacity=0.3)
    SCENE.play(FadeIn(gsp_polygon), FadeIn(bsp_polygon))
    UpdateMessage('Found an Ear!')
