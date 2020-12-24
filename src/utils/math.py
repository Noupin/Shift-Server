#pylint: disable=C0103, C0301, R0903
"""
The custom decoder class for Shift
"""
__author__ = "Noupin"

#Third Party Imports
import operator
from typing import List, Tuple, Iterable
from functools import reduce


def prod(iterable: Iterable) -> int:
    """
    Multiplies each element of the iterable.

    Args:
        iterable (iter): The object to be iterated and multiplied

    Returns:
        int: The product of each element of the iterable
    """

    return reduce(operator.mul, iterable, 1)


def rectangleArea(rectangle: Tuple[int]) -> int:
    """
    Gets the area of rectangle

    Args:
        rectangle (tuple of int): The x, y, width, and height of the rectangle

    Returns:
        int: The area of rectangle
    """

    _, _, width, height = rectangle

    return width*height


def getLargestRectangle(rectangles: List[Tuple[int]]) -> Tuple[int]:
    """
    Given a list of rectangles the largest rectangle is returned

    Args:
        rectangles (list of tuple of int): A list of the x, y, width, and height for the rectangle

    Returns:
        tuple of int: The largest rectangle
    """

    largestRectangle = rectangles[0]
    largestRectangleArea = rectangleArea(rectangles[0])

    for rectangle in rectangles:
        if rectangleArea(rectangle) > largestRectangleArea:
            continue

        largestRectangle = rectangle
        largestRectangleArea = rectangleArea(rectangle)
    
    return largestRectangle
