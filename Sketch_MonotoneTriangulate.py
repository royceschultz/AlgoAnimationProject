import numpy as np
import json
from matplotlib import pyplot as plt

POLYGON = json.load(open("polygons.json"))
KEY = 'monotone2'
POINTS = POLYGON[KEY]

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



#
# Main Function
#

# Assume polygon is monotone and defined clockwise
# (Verifiable in linear time, but not done here)
y_coords = [point[1] for point in POINTS]
min_idx = np.argmin(y_coords)
max_idx = np.argmax(y_coords)
left, right = [], []
i = (min_idx + 1) % len(POINTS)
while i != max_idx:
    left.append(POINTS[i])
    i = (i + 1) % len(POINTS)
i = (min_idx - 1) % len(POINTS)
while i != max_idx:
    right.append(POINTS[i])
    i = (i - 1) % len(POINTS)
print(len(left), len(right), len(POINTS))
# Length of left + right is 2 less than POINTS
# (Excludes min and max)
# TODO: Does this affect termination?
# I think not. But it's not clear.
# Seems like by induction, we can add 1 point a triangulated polygon and create another triangulated polygon.

# DEBUG PLOT
plt.plot([point[0] for point in POINTS], [point[1] for point in POINTS])

left_stack = []
right_stack = []
# Initialize stacks
left_stack.append(left.pop(0))
right_stack.append(right.pop(0))
# If left side is longer than the right side
if left_stack[-1][1] > right_stack[-1][1]:
    # Add to the right side
    while right[0][1] < left_stack[-1][1]:
        # TODO: Also require reflex vertex
        right_stack.append(right.pop(0))
else:
    # Mirror above

# If stopped because of heights, add diagonals from 1 to the other

# If stopped because of reflex vertiices, add diagonals on just 1 side

# Plot left and right stacks
plt.plot([point[0] for point in left_stack], [point[1] for point in left_stack], 'ro')
plt.plot([point[0] for point in right_stack], [point[1] for point in right_stack], 'bo')

plt.show()
