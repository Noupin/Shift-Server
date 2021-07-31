#pylint: disable=C0103, C0301, R0903
"""
The utility functions related to math
"""
__author__ = "Noupin"

#Third Party Imports
import dlib
import operator
import _dlib_pybind11
from functools import reduce
from typing import List, Tuple, Iterable, Any


def prod(iterable: Iterable) -> int:
    """
    Multiplies each element of the iterable.

    Args:
        iterable (iter): The object to be iterated and multiplied

    Returns:
        int: The product of each element of the iterable
    """

    return reduce(operator.mul, iterable, 1)


def flattenList(multiDimList: List[List[Any]]) -> List[Any]:
    """
    Given a multi-dimensional list it will be flattened by one dimension.

    Args:
        multiDimList (list of list of any): The list to be flattened

    Returns:
        list of any: The flattened list
    """

    return reduce(operator.iconcat, multiDimList, [])


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

    if len(rectangles) == 0:
        return (0, 0, 0, 0)

    largestRectangle = rectangles[0]
    largestRectangleArea = rectangleArea(rectangles[0])

    for rectangle in rectangles:
        if rectangleArea(rectangle) > largestRectangleArea:
            continue

        largestRectangle = rectangle
        largestRectangleArea = rectangleArea(rectangle)
    
    return largestRectangle


def xywhTotrblRectangle(rectangle: List[int]) -> _dlib_pybind11.rectangle:
    """
    Given a rectangle in the x, y, widht, height format it will be converted to the top-left and bottom-right coordinates.

    Args:
        rectangle (Tuple[int]): A list of the x, y, width, and height for the rectangle.

    Returns:
        _dlib_pybind11.rectangle: The top-left and bottom-right rectangle.
    """

    return dlib.rectangle(rectangle[0],
                          rectangle[1],
                          rectangle[0]+rectangle[2],
                          rectangle[1]+rectangle[3])
