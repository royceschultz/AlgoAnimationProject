# Polygon Triangulation Algorithms

# Definitions
* Triangulation
* Diagonal
* Ear

# Basic Operations
* Angle between 2 vectors
* Point within triangle

# Control: Brute Force in O(n<sup>4</sup>)
for all point pairs, check against all edges for intersection. Repeat n times.

# Improvement with theory: Dumb Ear Clipping O(n<sup>3</sup>)
Lemma: All polygons have at least 2 ears.
For each vertex, check against all points if it is an ear. Repeat n times.

# Smart Ear Clipping O(n<sup>2</sup>)
[Linear time ear finding, 1993](https://www.sciencedirect.com/science/article/pii/016786559390141Y)
*Slight modification:* Find a **diagonal** in linear time. Repeat n times.

# Monotization O(nlog(n))
[Lecture Notes, Jyh-Ming Lien](https://cs.gmu.edu/~jmlien/teaching/09_fall_cs633/uploads/Main/lecture03.pdf)
Use a scanline approach. Requires sorting so immediately omega(nlogn).
5 types of points.
ScanlineBST data structure for edges. Edge Helpers.

Triangulating a monotone polygon in O(n)

# ??? O(n)
[Chazelle, 1991](https://www.cs.princeton.edu/~chazelle/pubs/polygon-triang.pdf)
