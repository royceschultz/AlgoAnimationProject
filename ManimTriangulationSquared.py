from manim import *
import numpy as np
import json

np.random.seed(42)

# Configuration
POLYGON = json.load(open("polygons.json"))
KEY = 'sharp'
POINTS = POLYGON[KEY]
PRIMARY_COLOR = PURPLE_B
TIME_SHORT = 0.5
MAX_DEPTH = 4

# Manim Config
config.max_files_cached = 512
config.output_file = f'Triangulation_{KEY}.mp4'

messages = []
def ClearMessage(self):
    global messages
    if messages:
        self.play(*[FadeOut(x) for x in messages], run_time=TIME_SHORT)
        messages = []

def UpdateMessage(self, lines):
    global messages
    if type(lines) == str:
        lines = [lines]
    ClearMessage(self)
    messages.append(Text(lines[0]).shift(2.5 * DOWN))
    for i in range(1, len(lines)):
        messages.append(Text(lines[i]).next_to(messages[-1], DOWN))
    self.play(*[Write(x) for x in messages], run_time=TIME_SHORT)
    # for message in messages:
    #     self.play(Write(message), run_time=TIME_SHORT)
    self.wait()
class Triangulation(Scene):
    def construct(self):
        primary_polygon = Polygon(*[x + [0]  for x in POINTS], color=PRIMARY_COLOR)
        self.add(primary_polygon)
        Triangulate(self, POINTS)
        ClearMessage(self)

def Triangulate(self, poly_points, depth=0):
    # Recursively find a diagonal to split the polygon into 2 sub-polygons
    # Base Case: If the polygon has 3 points, it is a triangle
    self.next_section()
    if depth >= MAX_DEPTH:
        return
    if len(poly_points) <= 3:
        return
    selection = Polygon(*[x + [0] for x in poly_points], color=WHITE)
    selection.set_fill(PRIMARY_COLOR, opacity=0.3)
    self.play(FadeIn(selection))
    UpdateMessage(self, f'Finding a diagonal at depth {depth}')
    # Find the diagonal to split the polygon
    i, j, cleanup = FindDiagonal(self, poly_points)
    partition_line = Line(poly_points[i] + [0], poly_points[j] + [0], color=BLUE)
    self.play(Create(partition_line), *cleanup)
    if i > j: # Sort to avoid symmetric case.
        i, j = j, i
    # Partition on diagonal
    left = poly_points[i:j+1]
    right = poly_points[j:] + poly_points[:i+1]
    # Randomize start point
    x = np.random.randint(0, len(left))
    left = left[x:] + left[:x]
    x = np.random.randint(0, len(right))
    right = right[x:] + right[:x]
    # Recursively triangulate both sides
    self.play(selection.animate.set_color(PRIMARY_COLOR))
    Triangulate(self, left, depth+1)
    Triangulate(self, right, depth+1)

    self.play(FadeOut(selection))
    return

def FindDiagonal(self, poly_points):
    # Find the diagonal of the polygon
    # poly_points: list of points
    # return: list of points

    # Pick a point to start, any point.
    a, b, c = [poly_points[-1], poly_points[0], poly_points[1]]

    # Bisect it's angle to create a ray
    UnitVector = lambda v: v / np.linalg.norm(v)
    v1 = UnitVector(np.subtract(a, b))
    v2 = UnitVector(np.subtract(c, b))
    angle = CalculateAngle(v1, v2)
    bisecting_ray = UnitVector(v1 + v2)
    if angle > 0: # Orient the ray inward, assumes clockwise polygon
        bisecting_ray *= -1
    # Initialise bisecting ray to be sufficiently large (should be infinite, but doesn't matter)
    bisecting_ray *= 100
    closest_intersection = list(np.add(b, bisecting_ray)) # Keep points in list form, not numpy array

    # Animate bisecting ray
    UpdateMessage(self, f'Pick a point and bisect it\'s angle')
    BisectingLine = lambda endpoint: Line(b + [0], endpoint + [0], color=GOLD)
    bray_line = BisectingLine(closest_intersection)
    self.play(Create(bray_line))

    # Scan all edges for intersections with the bisecting ray.
    # Find closest intersection.
    UpdateMessage(self, 'Scan all edges for the closest intersection point')
    k = None
    intersection_dot = Dot(closest_intersection + [0])
    old_selected_edge = None
    for i in range(2, len(poly_points)):
        # Check if the edge intersects the bisecting ray
        edge = (poly_points[i], poly_points[i-1])
        # Animate edge selection
        selected_edge_line = Line(edge[0] + [0], edge[1] + [0], color=YELLOW, stroke_width=10)
        if old_selected_edge is not None:
            # Fade current + previous for smoother (and faster) flow
            self.play(FadeIn(selected_edge_line), FadeOut(old_selected_edge), run_time=TIME_SHORT)
        else:
            self.play(FadeIn(selected_edge_line), run_time=TIME_SHORT)
        old_selected_edge = selected_edge_line

        intersection = FindIntersection(edge, (b, closest_intersection))
        if intersection is not None:
            closest_intersection = intersection
            k = i
            # Animate intersection finding
            self.play(Transform(intersection_dot, Dot(intersection + [0], color=RED)))
            self.play(Transform(bray_line, BisectingLine(intersection)), run_time=TIME_SHORT)
        
    # Cleanup edge selection loop
    self.play(FadeOut(old_selected_edge), run_time=TIME_SHORT)

    # Search LEFT partition
    UpdateMessage(self, 'Search the left side for a diagonal')
    UpdateMessage(self, ['Initialize a triangle on the', 'left side of the intersection edge'])
    is_found, data = SearchPartition(self, list(reversed(poly_points[1:k])), [b, closest_intersection])
    if is_found:
        idx, selected_triangle = data
        self.play(FadeOut(bray_line), FadeOut(intersection_dot), run_time=TIME_SHORT)
        return 0, (k-1) - idx, [FadeOut(selected_triangle)]
    # else not found (yet)
    # Search RIGHT partition
    UpdateMessage(self, 'Search the right side for a diagonal')
    is_found, data = SearchPartition(self, poly_points[k:], [b, closest_intersection])
    if is_found:
        idx, selected_triangle = data
        self.play(FadeOut(bray_line), FadeOut(intersection_dot), run_time=TIME_SHORT)
        return 0, k+1 + idx, [FadeOut(selected_triangle)]
    # else the point is an ear.
    UpdateMessage(self, 'The selected point is an ear')
    self.play(FadeOut(bray_line), FadeOut(intersection_dot))
    # self.play(FadeOut(query_point_dot), FadeOut(old_query_point_dot))
    return 1, len(poly_points) - 1, []


def SearchPartition(self, points, tri_base):
    # input:
    #   self: reference to the scene for animations
    #   points: list of points to search
    #   tri_base: 2 points that form the base of triangle, query point is the 3rd point
    # returns:
    #   selected_index
    #   manim objects (How else to cleanup?)
    # Note: Searches front to back
    if len(points) == 0:
        return False, None
    selected_index = 0
    QueryTriangle = lambda point, color=YELLOW: Polygon(*[x + [0] for x in tri_base + [point]], color=color).set_fill(color, opacity=0.3)
    selected_triangle = QueryTriangle(points[selected_index])
    self.play(FadeIn(selected_triangle))
    query_point_dot = Dot(points[selected_index] + [0], color=RED)
    self.play(Create(query_point_dot))
    UpdateMessage(self, 'Search partition for a point in the triangle')
    for i, query_point in enumerate(points):
        # Animate query_point_selection
        new_query_point_dot = Dot(query_point + [0], color=RED)
        self.play(Transform(query_point_dot, new_query_point_dot, run_time=TIME_SHORT))
        if CheckTriangleContains(tri_base + [points[selected_index]], query_point):
            selected_index = i
            # Update selected triangle
            self.play(Transform(selected_triangle, QueryTriangle(points[selected_index])))
    
    if selected_index != len(points) - 1:
        # Found a valid diagonal (b -> point with minimum angle)
        self.play(selected_triangle.animate.set_fill(GREEN, opacity=0.3).set_stroke(GREEN), run_time=TIME_SHORT)
        UpdateMessage(self, 'Found a diagonal!')
        # Clean up plot
        self.play(FadeOut(query_point_dot), run_time=TIME_SHORT)
        return True, (selected_index, selected_triangle)
    # Else unsuccessful search the other side
    self.play(selected_triangle.animate.set_fill(RED, opacity=0.3).set_stroke(RED))
    UpdateMessage(self, ['No Good!', 'Triangle contains a polygon edge.'])
    self.play(FadeOut(selected_triangle), FadeOut(query_point_dot))
    return False, None


#
# Helper Functions
#

def CalculateAngle(a, b):
    # Returns angle between [-pi, pi]
    # a, b: vectors
    angle = np.arctan2(a[1], a[0]) - np.arctan2(b[1], b[0])
    if angle > np.pi:
        angle -= 2 * np.pi
    if angle < -np.pi:
        angle += 2 * np.pi
    return angle


def FindIntersection(line1, line2):
    # returns the point of intersection of the two lines (if it exists)
    # returns None if the lines do not intersect
    x1, y1 = line1[0]
    x2, y2 = line1[1]
    x3, y3 = line2[0]
    x4, y4 = line2[1]
    denom = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
    if denom == 0:
        return None
    ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / denom
    ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / denom
    if ua >= 0 and ua <= 1 and ub >= 0 and ub <= 1:
        return [x1 + ua * (x2 - x1), y1 + ua * (y2 - y1)]
    else:
        return None


def CheckTriangleContains(tri, point):
    a, b, c = tri
    i = CalculateAngle(np.subtract(b, a), np.subtract(point, a))
    j = CalculateAngle(np.subtract(c, b), np.subtract(point, b))
    k = CalculateAngle(np.subtract(a, c), np.subtract(point, c))
    if i > 0 and j > 0 and k > 0:
        return True
    if i < 0 and j < 0 and k < 0:
        return True
    return False
