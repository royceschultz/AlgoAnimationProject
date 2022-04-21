import numpy as np

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
