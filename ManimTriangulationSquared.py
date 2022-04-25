from manim import *
import numpy as np
import json

config.max_files_cached = 256

POLYGON = json.load(open("polygons.json"))
KEY = 'large'
POINTS = POLYGON[KEY]
PRIMARY_COLOR = PURPLE_B
TIME_SHORT = 0.5

class Triangulation(Scene):
    def construct(self):
        primary_polygon = Polygon(*[x + [0]  for x in POINTS], color=PRIMARY_COLOR)
        self.add(primary_polygon)
        self.wait()
        Triangulate(self, POINTS)

def Triangulate(self, poly_points, depth=0):
    # Recursively find a diagonal to split the polygon into 2 sub-polygons
    # Base Case: If the polygon has 3 points, it is a triangle
    self.next_section()
    if depth >= 6:
        return
    if len(poly_points) <= 3:
        return
    selection = Polygon(*[x + [0] for x in poly_points], color=GREEN)
    selection.set_fill(PRIMARY_COLOR, opacity=0.3)
    self.play(FadeIn(selection))
    self.wait()
    # Find the diagonal to split the polygon
    i, j = FindDiagonal(self, poly_points)
    if i > j: # Sort to avoid symmetric case.
        i, j = j, i
    # Partition on diagonal
    left = poly_points[i:j+1]
    right = poly_points[j:] + poly_points[:i+1]
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

    # Pick a point to start.
    a, b, c = [poly_points[-1], poly_points[0], poly_points[1]]

    # Bisect it's angle to create a ray
    v1 = np.subtract(a, b)
    v2 = np.subtract(c, b)
    v1 /= np.linalg.norm(v1)
    v2 /= np.linalg.norm(v2)

    angle = CalculateAngle(v1, v2)
    bisecting_ray = v1 + v2
    bisecting_ray /= np.linalg.norm(bisecting_ray)
    if angle > 0: # Orient the ray inward, assumes (clockwise|counterclockwise[?]) polygon
        bisecting_ray *= -1
    # Initialise bisecting ray to be sufficiently large (should be infinite, but doesn't matter)
    bisecting_ray *= 100
    closest_intersection = list(np.add(b, bisecting_ray)) # Keep points in list form, not numpy array

    # Animate bisecting ray
    bray_line = Line(b + [0], closest_intersection + [0])
    self.play(Create(bray_line))

    # Scan all edges for intersections with the bisecting ray.
    # Find closest intersection.
    k = None
    intersection_dot = Dot(b + [0])
    for i in range(2, len(poly_points)):
        # Check if the edge intersects the bisecting ray
        edge = (poly_points[i], poly_points[i-1])
        # Animate edge selection
        selected_edge_line = Line(edge[0] + [0], edge[1] + [0], color=YELLOW)
        self.play(FadeIn(selected_edge_line), run_time=TIME_SHORT)

        intersection = FindIntersection(edge, (b, closest_intersection))
        if intersection is not None:
            # Animate intersection finding
            new_dot = Dot(intersection + [0], color=RED)
            self.play(Transform(intersection_dot, new_dot))
            # Update bray: transform bray_line to new length
            new_bray_line = Line(b + [0], intersection + [0])
            self.play(Transform(bray_line, new_bray_line))

            # Update calculation variables
            closest_intersection = intersection
            k = i
        
        # Cleanup edge selection loop
        self.play(FadeOut(selected_edge_line), run_time=TIME_SHORT)

    # Use closest intersection edge to partition the rest of the points
    # Left = poly_points[:k]
    # Right = poly_points[k:]

    # Animate partitioning
    dot_k = Dot(poly_points[k] + [0], color=BLUE)
    dot_km1 = Dot(poly_points[k-1] + [0], color=BLUE)
    self.play(FadeIn(dot_k), FadeIn(dot_km1))

    #
    # Search LEFT partition
    #
    selected_index = k - 1
    tri_points = [b, closest_intersection, poly_points[selected_index]]
    selected_triangle = Polygon(*[x + [0] for x in tri_points], color=YELLOW)
    selected_triangle.set_fill(YELLOW, opacity=0.3)
    self.play(FadeIn(selected_triangle))
    query_point_dot = Dot(poly_points[selected_index] + [0], color=RED)
    self.play(Create(query_point_dot))
    for i, query_point in reversed(list(enumerate(poly_points[1:k-1]))):
        # Animate query_point_selection
        new_query_point_dot = Dot(query_point + [0], color=RED)
        self.play(Transform(query_point_dot, new_query_point_dot))
        if CheckTriangleContains(tri_points, query_point):
            # Update selected triangle
            selected_index = i + 1
            tri_points = [b, closest_intersection, poly_points[selected_index]]
            new_selected_triangle = Polygon(*[x + [0] for x in tri_points], color=YELLOW)
            new_selected_triangle.set_fill(YELLOW, opacity=0.3)
            self.play(Transform(selected_triangle, new_selected_triangle))

    if selected_index != 1:
        # Found a diagonal!
        partition_line = Line(b + [0], poly_points[selected_index] + [0], color=BLUE)
        # Clean up plot
        self.play(FadeOut(dot_k), FadeOut(dot_km1), FadeOut(query_point_dot), FadeOut(intersection_dot), FadeOut(bray_line))
        # Show new partition line
        self.play(Create(partition_line))
        self.play(FadeOut(selected_triangle))
        self.wait()
        return 0, selected_index

    # No diagonal from b to left polygon
    # Turn min line red (invalid)
    self.play(selected_triangle.animate.set_fill(RED, opacity=0.3), selected_triangle.animate.set_stroke(RED, width=2))
    self.play(FadeOut(selected_triangle))
    # Save to remove later
    old_query_point_dot = query_point_dot
    
    #
    # Search RIGHT partition
    #
    selected_index = k
    tri_points = [b, closest_intersection, poly_points[selected_index]]
    selected_triangle = Polygon(*[x + [0] for x in tri_points], color=YELLOW)
    selected_triangle.set_fill(YELLOW, opacity=0.3)
    self.play(FadeIn(selected_triangle))
    query_point_dot = Dot(poly_points[selected_index] + [0], color=RED)
    self.play(Create(query_point_dot))
    for i, query_point in enumerate(poly_points[k+1:]):
        # Animate query point selection
        new_query_point_dot = Dot(query_point + [0], color=RED)
        self.play(Transform(query_point_dot, new_query_point_dot))
        if CheckTriangleContains(tri_points, query_point):
            # Update selected triangle
            selected_index = i + k + 1
            tri_points = [b, closest_intersection, poly_points[selected_index]]
            new_selected_triangle = Polygon(*[x + [0] for x in tri_points], color=YELLOW)
            new_selected_triangle.set_fill(YELLOW, opacity=0.3)
            self.play(Transform(selected_triangle, new_selected_triangle))

    if selected_index != len(poly_points) - 1:
        # Found a valid diagonal (b -> point with minimum angle)

        # Clean up plot
        self.play(FadeOut(dot_k), FadeOut(dot_km1), FadeOut(bray_line), FadeOut(intersection_dot), FadeOut(query_point_dot), FadeOut(old_query_point_dot))
        # Add triangulation edge
        partition_line = Line(b + [0], poly_points[selected_index] + [0], color=BLUE)
        self.play(Create(partition_line))
        self.play(FadeOut(selected_triangle))

        return 0, selected_index
    # Else unsuccessful search on the right side
    self.play(selected_triangle.animate.set_fill(RED, opacity=0.3))
    self.play(selected_triangle.animate.set_fill(RED, opacity=0.3), selected_triangle.animate.set_stroke(RED, width=2))
    self.play(FadeOut(selected_triangle))
    # Found a proper ear between left and right sides
    self.play(FadeOut(selected_triangle))
    partition_line = Line(a + [0], c + [0], color=BLUE)
    self.play(FadeOut(dot_k), FadeOut(dot_km1), FadeOut(bray_line), FadeOut(intersection_dot))
    self.play(Create(partition_line))
    self.play(FadeOut(query_point_dot), FadeOut(old_query_point_dot))
    return 1, len(poly_points) - 1



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
