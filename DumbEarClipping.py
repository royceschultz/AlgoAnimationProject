from manim import *
import numpy as np
import json

def CalculateAngle(a, b):
    # x = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    # return np.arccos(x)
    x = np.cross(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    return np.arcsin(x).sum()

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

class LineTest(Scene):
    def construct(self):
        line1 = Line(UP, DOWN)
        line2 = Line(LEFT, RIGHT)
        self.play(Create(line1), Create(line2))
        self.play(Uncreate(line1), Uncreate(line2))

class EarClippingCubed(Scene):
    def construct(self):
        # Load polygons from json file
        saved_polygons = json.load(open('polygons.json'))
        key = 'sharp2'
        # User input method for selecting polygon
        if key is None: # Skip if key is already defined above
            for k, pts in saved_polygons.items():
                print(k)
            while True:
                key = input('Key: ')
                if key in saved_polygons:
                    break

        # Modify points to manim style
        points = [x + [0] for x in saved_polygons[key]]

        # Create shapes
        polygon = Polygon(*points, color=PURPLE_B)
        polygon.set_fill(PURPLE_B, opacity=1)

        self.add(polygon)
        self.wait()

        triangulations = []
        i = 0
        line1 = Line(LEFT, RIGHT)
        line2 = Line(UP, DOWN)
        while True:
            if len(points) < 3:
                break
            # Select 3 sequential points forming a triangle
            # info1 = Text('Find Ear based on angle')
            # info1.align_to(polygon, UP + LEFT)
            # self.play(Write(info1))
            query_triangle = [points[i], points[i-1], points[i-2]]
            a, b, c = query_triangle
            line1.put_start_and_end_on(b, a)
            line2.put_start_and_end_on(c, b)

            self.play(Create(line1), Create(line2))

            # Check if the triangle is inward or outward facing
            # TODO: Assumes clockwise order. Counter clockwise order will not work
            a, b, c = query_triangle
            angle = CalculateAngle(np.subtract(b, a), np.subtract(c,a))

            if angle > 0:
                angle_obj = Angle(line1, line2, radius=0.5, color=GREEN)
            else:
                angle_obj = Angle(line1, line2, radius=0.5, color=RED)
            self.play(Create(angle_obj))

            if angle < 0:
                self.play(Uncreate(angle_obj))
                self.play(Uncreate(line1), Uncreate(line2))
            if angle > 0:
                selection = Polygon(*query_triangle, color=WHITE)
                self.play(Create(selection))
                self.play(Uncreate(angle_obj))
                self.play(Uncreate(line1), Uncreate(line2))
                # Check if the query triangle contains no other points in the polygon
                # info1.set_text('Check if triangle contains no other points')
                # self.play(Write(info1))
                checked_points = []
                is_ear = True
                for j in range(len(points) - 3):
                    k = (i + j + 1) % len(points)
                    # Animate point selection
                    dot = Dot(points[k], color=RED)
                    checked_points.append(dot)
                    self.play(FadeIn(dot), run_time=0.5)
                    # If triangle contains another point, it cannot be clipped.
                    if CheckTriangleContains([a, b, c], points[k]):
                        self.play(dot.animate.scale(2))
                        is_ear = False
                        break
                    else:
                        # Animate passing of point
                        self.play(dot.animate.set_color(GREEN), run_time=0.5)

                if is_ear:
                    # New triangulation. Making progress on the problem.
                    new_triangle = Polygon(*query_triangle, color=BLUE)
                    triangulations.append(new_triangle)
                    self.play(FadeIn(new_triangle))
                    self.play(FadeOut(selection))

                    points.pop(i-1)
                    new_polygon = Polygon(*points, color=PURPLE_B)
                    new_polygon.set_fill(PURPLE_B, opacity=1)
                    new_polygon.set_z_index(-1)
                    self.add(new_polygon)
                    self.play(FadeOut(polygon))
                    polygon = new_polygon

                    
                 
                # Remove dots
                if checked_points:
                    self.play(*[FadeOut(dot) for dot in checked_points])


            i += 1
            i %= len(points)
