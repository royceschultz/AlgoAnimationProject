from manim import *
import numpy as np
import json

config.max_files_cached = 256

POLYGON = json.load(open("polygons.json"))
key = 'sharp'
POINTS = POLYGON[key]

PRIMARY_COLOR = PURPLE_B

TIME_SHORT = 0.5

class Triangulation(Scene):
    def construct(self):
        manim_points = [x + [0]  for x in POINTS]
        print(manim_points)
        primary_polygon = Polygon(*manim_points, color=PRIMARY_COLOR)
        primary_polygon.set_fill(PRIMARY_COLOR, opacity=0.05)

        self.add(primary_polygon)
        self.wait()

        Triangulate(self, POINTS)

def Triangulate(self, poly_points, depth=0):
    # Highlight self as 'selected'
    # color as a function of depth
    if len(poly_points) <= 3:
        return
    selection = Polygon(*[x + [0] for x in poly_points], color=PURPLE_B)
    selection.set_fill(PURPLE_B, opacity=0.3)
    self.play(FadeIn(selection))
    self.wait()
    i, j = FindDiagonal(self, poly_points)

    # Partition on diagonal
    if i > j:
        i, j = j, i
    left = poly_points[i:j+1]
    right = poly_points[j:] + poly_points[:i+1]

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
    if angle > 0: # Orient the ray inward
        bisecting_ray *= -1
    # Initialise bisecting ray to be sufficiently large
    bisecting_ray *= 100
    closest_intersection = list(np.add(b, bisecting_ray))

    bray_line = Line(b + [0], closest_intersection + [0])
    self.play(Create(bray_line))

    # Scan all edges for intersections with the bisecting ray.
    # Find closest intersection.
    
    k = None
    intersection_dot = None
    for i in range(2, len(poly_points)):
        # Check if the edge intersects the bisecting ray
        edge = (poly_points[i], poly_points[i-1])
        # Animate edge selection
        selected_edge_line = Line(edge[0] + [0], edge[1] + [0], color=YELLOW)
        self.play(FadeIn(selected_edge_line), run_time=TIME_SHORT)

        intersection = FindIntersection(edge, (b, closest_intersection))
        if intersection is not None:
            # Animate intersection finding
            if intersection_dot is None:
                # First intersection found
                intersection_dot = Dot(intersection + [0], color=RED)
                self.play(Create(intersection_dot))
            else:
                # Transition from old dot
                new_dot = Dot(intersection + [0], color=RED)
                self.play(Transform(intersection_dot, new_dot))
            # Update bray
            new_bray_line = Line(b + [0], intersection + [0])
            # transform bray_line to new length
            self.play(Transform(bray_line, new_bray_line))
            self.wait()
            
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

    # Find minimum angle on left side
    minimum_angle = 2 * np.pi
    minimum_index = None
    query_line = None
    min_line = None
    for i, query_point in reversed(list(enumerate(poly_points[1:k]))):
        # Animate query point selection
        if query_line is None:
            # Draw Query Line
            query_line = Line(b + [0], query_point + [0], color=YELLOW)
            self.play(Create(query_line))
        else:
            # Update query line
            new_query_line = Line(b + [0], query_point + [0], color=YELLOW)
            self.play(Transform(query_line, new_query_line))
        
        query_vec = np.subtract(query_point, b)
        angle = abs(CalculateAngle(query_vec, bisecting_ray))
        print(minimum_angle, angle)
        if angle < minimum_angle:
            minimum_angle = angle
            minimum_index = i + 1
            # Animate minimum angle selection
            if min_line is None:
                # Draw minimum line
                min_line = Line(poly_points[0] + [0], poly_points[minimum_index] + [0], color=GREEN)
                self.play(Create(min_line))
            else:
                # Update minimum line
                new_min_line = Line(poly_points[0] + [0], poly_points[minimum_index] + [0], color=GREEN)
                self.play(Transform(min_line, new_min_line))

    if minimum_index != 1:
        # Found a diagonal!
        # Clean up plot
        partition_line = Line(b + [0], poly_points[minimum_index] + [0], color=BLUE)
        self.play(FadeOut(dot_k), FadeOut(dot_km1), FadeOut(query_line), FadeOut(bray_line), FadeOut(intersection_dot))
        self.play(Transform(min_line, partition_line))
        self.wait()
        # Found a valid diagonal (b -> point with minimum angle)
        return 0, minimum_index
    # Else unsucessful search on the left side
    # scan right side next

    # Turn min line red (invalid)
    self.play(min_line.animate.set_color(RED))
    self.play(Uncreate(min_line), Uncreate(query_line))

    minimum_angle = 2 * np.pi
    minimum_index = None
    query_line = None
    min_line = None
    for i, query_point in enumerate(poly_points[k:]):
        # Animate query point selection
        if query_line is None:
            # Draw Query Line
            query_line = Line(b + [0], query_point + [0], color=YELLOW)
            self.play(Create(query_line))
        else:
            # Update query line
            new_query_line = Line(b + [0], query_point + [0], color=YELLOW)
            self.play(Transform(query_line, new_query_line))
        
        query_vec = np.subtract(query_point, b)
        angle = abs(CalculateAngle(query_vec, bisecting_ray))
        if angle < minimum_angle:
            minimum_angle = angle
            minimum_index = i + k

            # Animate minimum angle selection
            if min_line is None:
                # Draw minimum line
                min_line = Line(b + [0], poly_points[minimum_index] + [0], color=GREEN)
                self.play(Create(min_line))
            else:
                # Update minimum line
                new_min_line = Line(b + [0], poly_points[minimum_index] + [0], color=GREEN)
                self.play(Transform(min_line, new_min_line))

    if minimum_index != len(poly_points) - 1:
        # Found a valid diagonal (b -> point with minimum angle)

        # Clean up plot
        self.play(FadeOut(dot_k), FadeOut(dot_km1), FadeOut(query_line), FadeOut(bray_line), FadeOut(intersection_dot))
        # Add triangulation edge
        partition_line = Line(b + [0], poly_points[minimum_index] + [0], color=BLUE)
        self.play(Transform(min_line, partition_line))

        return 0, minimum_index
    # Else unsucessful search on the right side
    # Found a proper ear between left and right sides
    self.play(min_line.animate.set_color(RED))
    self.play(Uncreate(min_line), Uncreate(query_line))



    partition_line = Line(a + [0], c + [0], color=BLUE)
    self.play(FadeOut(dot_k), FadeOut(dot_km1), FadeOut(query_line), FadeOut(bray_line), FadeOut(intersection_dot))
    self.play(Create(partition_line))
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
