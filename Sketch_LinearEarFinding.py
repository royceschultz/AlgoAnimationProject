import numpy as np
import json

# DEBUG
import matplotlib.pyplot as plt

POLYGONS = json.load(open("polygons.json"))
KEY = 'sharp'
POINTS = POLYGONS[KEY]

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
    return left, right

def FindGoodSubPolygon(points, i, j):
    # Parameters:
    # points: list of points
    # i, j: Indices of a diagonal of a polygon.
    left, right = PartitionPoints(points, i, j)
    # Search the smaller side
    sub_polygon = left
    if len(right) < len(left):
        sub_polygon = right
    middle_index = len(sub_polygon) // 2
    try:
        d = FindDiagonalFrom(middle_index, sub_polygon)
    except:
        # Is this necessary? I don't think so.
        # Pretty sure this implies middle_index is an ear.
        # Could exit early instead.
        d = FindDiagonalFrom(middle_index + 1, points)
    return sub_polygon, middle_index, d


# Find a diagonal, any diagonal.
a = 0
try:
    b = FindDiagonalFrom(a, POINTS)
    # Possibly no diagonal exists from a
except: # Try again, guaranteed to work
    a = 1
    b = FindDiagonalFrom(a, POINTS)
sub_polygon = POINTS
while len(sub_polygon) > 3:
    sub_polygon, a, b = FindGoodSubPolygon(sub_polygon, a, b)
