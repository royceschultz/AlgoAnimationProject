from matplotlib import pyplot as plt
import matplotlib as mpl
import json
import os

plt.figure(figsize=(12, 6))

plt.plot([-7,7],[-4,4], 'wo')

poly_points = []
patch = None

while True:
    plt.title('Press enter to finish')
    pts = plt.ginput(1)
    print(pts)
    if pts:
        poly_points.append(pts[0])
        plt.plot(pts[0][0], pts[0][1], 'ro')
        plt.draw()
    else:
        break
    if len(poly_points) >= 3:
        if patch:
            patch.remove()
        polygon = plt.Polygon(poly_points, color='b', fill='c', closed=True)
        patch = polygon
        plt.gca().add_patch(polygon)
        plt.draw()
plt.close()

while True:
    save = input('Save? (y/n) ')
    if save == 'y':
        break
    elif save == 'n':
        quit()

key = input('Key: ')

if save == 'y':
    # if file exists
    if os.path.isfile('polygons.json'):
        with open('polygons.json', 'r') as f:
            polygons = json.load(f)
    else:
        polygons = {}
    polygons[key] = poly_points
    with open('polygons.json', 'w') as outfile:
        json.dump(polygons, outfile)
