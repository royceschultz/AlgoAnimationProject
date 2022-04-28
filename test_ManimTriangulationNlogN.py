import pytest

from ManimTriangulationNlogN import *

def test_POINTS_exists():
    assert POINTS is not None

def test_BST_inits():
    t = ScanlineBST()
    assert t.root is None

def test_BST_insert():
    edge1 = (POINTS[0], POINTS[1])
    edge2 = (POINTS[1], POINTS[2])
    t = ScanlineBST()
    t.setY(edge1[0][1])
    t.insert(edge1)
    t.setY(edge2[0][1])
    t.insert(edge2)
    assert t.root is not None
    assert t.root.left is not None or t.root.right is not None

def test_BST_lookup():
    edge1 = (POINTS[0], POINTS[1])
    t = ScanlineBST()
    t.setY(edge1[0])
    t.insert(edge1)
    x = t.find(edge1[0]) # Lookup by x value
    assert x is not None

def test_BST_lookup2():
    edge1 = (POINTS[0], POINTS[1])
    edge2 = (POINTS[1], POINTS[2])
    t = ScanlineBST()
    t.insert(edge1)
    t.insert(edge2)
    x = t.find(edge1[1])
    assert x is not None

def test_SegmentNode():
    edge1 = ((0,0), (1,1))
    node = SegmentNode(edge1)
    assert node.value(0) == 0
    assert node.value(1) == 1
    assert node.value(0.5) == 0.5

def test_SegmentNode2():
    edge1 = ((1,0), (0,1))
    node = SegmentNode(edge1)
    assert node.value(0) == 1
    assert node.value(1) == 0
    assert node.value(0.5) == 0.5
