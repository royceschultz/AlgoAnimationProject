# Just a sketch for now

# Assume a method to find diagonals in linear time
# (Covered in other animations)

# Find a diagonal, any diagonal.
# Pick a side of the diagonal (right or left)
# Bisect that side
# Find a diagonal containing the bisecting point and within that side
# Choose the good side.
# The good side will always be less than 1/2 the points
# This forms a geometric series
# Recurse until an ear is found in linear time.
# Repeat n times to triangulate.
# Overall O(n^2)

# This is more memory efficient than other method.
# Other method relies on recursing on both sides, requiring a function stack for all calls.
# This method works itteratively, requiring no more memory than the single function call.
