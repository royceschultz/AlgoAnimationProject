def Triangulate(self, poly_points, depth=0):
    # A naive n^3 triangulation method using ear clipping
    # poly_points: list of points
    # return: list of triangles
    triangles = []
    n = len(poly_points)
    for i in range(n-3): # Clip n ears
        for j in range(len(poly_points)): # Search n points for a convex point
            # If point j is convex
            if True:
                is_ear = True
                for k in range(len(poly_points) - 3): # Search n points for a point inside the triangle
                    l = (j + k + 2) % n
                    # if point l is inside triangle
                    if True:
                        is_ear = False
                        break
                if is_ear:
                    # clip the ear
                    break
            
