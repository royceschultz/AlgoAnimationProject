from manim import *
import numpy as np
import json

np.random.seed(42)

# DEBUG
import matplotlib.pyplot as plt

POLYGONS = json.load(open("polygons.json"))
KEY = 'medium'
POINTS = POLYGONS[KEY]
TIME_SHORT = 0.2

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
    edge1 = (points[a], points[(a + 1) % len(points)])
    edge2 = (points[a], points[(a - 1) % len(points)])
    EdgeVector = lambda s: np.subtract(s[1], s[0])
    angle1 = CalculateAngle(EdgeVector(diagonal), EdgeVector(edge1))
    angle2 = CalculateAngle(EdgeVector(diagonal), EdgeVector(edge2))
    if angle1 * angle2 >= 0:
        return False
    # Check if the diagonal intersects any of the lines
    for i in range(len(points)):
        if i == a or i == b or i-1 == a or i-1 == b:
            continue
        edge = (points[i-1], points[i])
        if IsIntersect(edge, diagonal):
            return False
    return True

def IsIntersect(line1, line2):
    x1, y1 = line1[0]
    x2, y2 = line1[1]
    x3, y3 = line2[0]
    x4, y4 = line2[1]
    denom = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
    if denom == 0:
        return False
    ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / denom
    ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / denom
    if ua >= 0 and ua <= 1 and ub >= 0 and ub <= 1:
        return True
    else:
        return False

def CalculateAngle(a, b):
    # Returns angle between [-pi, pi]
    # a, b: vectors
    angle = np.arctan2(a[1], a[0]) - np.arctan2(b[1], b[0])
    if angle > np.pi:
        angle -= 2 * np.pi
    if angle < -np.pi:
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
    if len(right) < len(left):
        good_sub_polygon, bad_sub_polygon = right, left
    # Animate polygon partition
    gsp_polygon = Polygon(*[x + [0] for x in good_sub_polygon])
    bsp_polygon = Polygon(*[x + [0] for x in bad_sub_polygon])
    gsp_polygon.set_fill(GREEN, opacity=0.3)
    bsp_polygon.set_fill(RED, opacity=0.3)
    SCENE.play(FadeIn(gsp_polygon), FadeIn(bsp_polygon))
    
    UpdateMessage('Find the middle point.')
    SCENE.play(FadeOut(gsp_polygon)) # Clean up GSP animation
    middle_index = len(good_sub_polygon) // 2
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
            middle_index -= 2
            d = FindDiagonalFrom(middle_index, good_sub_polygon)
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
        if min(len(left), len(right)) == 3:
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
