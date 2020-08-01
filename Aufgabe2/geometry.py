"""
Geschrieben für die 2. Runde des 37. Bundeswettbewerb Informatik
Autor: Florian Rädiker
Teilnahme-ID: 48302

Aufgabe 2: Dreiecksbeziehungen

WRITTEN IN PYTHON3

Dieses Modul stellt alle geometrischen Funktionen bereit: Dreieck, platziertes Dreieck, Gruppe, ... .
"""
import itertools
import math
import random
from typing import Iterator, Tuple, Iterable, List, Optional

import svgwrite.shapes
import svgwrite.container
import svgwrite.text


class Point:
    """
    Represents one point in a 2D coordinate system.
    """
    __slots__ = ("x", "y")

    def __init__(self, x: float, y: float):
        """
        Initializes a point
        :param x: x coord
        :param y: y coord
        """
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return "P({x:3.0f}|{y:3.0f})".format(x=self.x, y=self.y)

    def get_distance(self, other: "Point") -> float:
        """
        Calculates the distance between this point and 'other'
        :param other: some other Point
        :return: distance between the two points
        """
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    def to_tuple(self) -> Tuple[float, float]:
        """
        :return: a tuple containing the x and the y coordinate: (x, y)
        """
        return self.x, self.y

    def to_tuple_round(self) -> Tuple[float, float]:
        """
        :return: like Point.to_tuple, but the coordinates are rounded (round(x), round(y))
        """
        return round(self.x), round(self.y)

    def get_angle(self, other: "Point") -> float:
        """
        Calculates the angle to another point in degree.
        0°: other point is shifted in positive x-direction,
        90°: other point is shifted in positive y-direction,
        180°: other point is shifted in negative x-direction,
        270°: other point is shifted in negative y-direction
        :param other: some other Point
        :return: angle between the two points
        """
        return math.degrees((math.atan2(other.x - self.x, self.y - other.y) - math.pi/2) % (2*math.pi))

    def __sub__(self, other: "Point") -> "Point":
        """
        self-other
        :param other: some other Point
        :return: a new Point with the other Point's coordinates subtracted from the coordinates of this point
        """
        return Point(self.x - other.x, self.y - other.y)

    def rotate_around(self, origin: "Point", angle: float):
        """
        Rotates this point around 'origin' by 'angle' degree.
        :param origin: the origin (a Point) for the rotation
        :param angle: in degree
        """
        angle = math.radians(angle)
        p = self-origin
        self.x = p.x*math.cos(angle) - p.y*math.sin(angle) + origin.x
        self.y = p.y*math.cos(angle) + p.x*math.sin(angle) + origin.y


class Triangle:
    """
    This class stores information for one triangle by saving the side lengths, the angles and the triangle's ID.
    """
    __slots__ = (
        "shortest_line", "middle_line", "longest_line",
        "shortest_line_angle", "longest_line_angle", "middle_line_angle",
        "triangle_id"
    )

    def __init__(self, lineA: float, lineB: float, lineC: float, triangle_id=-1):
        """
        Initializes a Triangle-object.
        The shortest side length is stored in Triangle.shortest_line, the other sides are called *arms*.
        The shortest arm length is stored in Triangle.middle_line while the other arm's length is stored in
        Triangle.longest_line.
        Triangle.shortest_line_angle stores the angle opposite of shortest_line,
        Triangle.longest_line_angle stores the angle opposite of longest_line and
        Triangle.middle_line_angle stores the angle opposite of middle_line.
        The triangle ID is stored in Triangle.triangle_id
        :param lineA: length of one side
        :param lineB: length of one side
        :param lineC: length of one side
        :param triangle_id: the triangle's ID
        """
        # shortest_line is the smallest side, longest_line is the longest side
        self.shortest_line, self.middle_line, self.longest_line = sorted((lineA, lineB, lineC))

        # uses the law of cosines to calculate two angles:
        #           b² + c² - a²
        # A = acos( ------------ )
        #               2bc
        self.shortest_line_angle = math.degrees(
            math.acos(
                (self.middle_line ** 2 + self.longest_line ** 2 - self.shortest_line ** 2) /
                (2 * self.middle_line * self.longest_line)
            )
        )
        self.longest_line_angle = math.degrees(
            math.acos(
                (self.middle_line ** 2 + self.shortest_line ** 2 - self.longest_line ** 2) /
                (2 * self.middle_line * self.shortest_line)
            )
        )
        self.middle_line_angle = 180 - self.shortest_line_angle - self.longest_line_angle

        self.triangle_id = triangle_id

    @staticmethod
    def from_points(pointA: Point, pointB: Point, pointC: Point, triangle_id=-1) -> "Triangle":
        """
        Initializes a Triangle by calculating the distances between the given points.
        :param pointA: some Point
        :param pointB: some Point
        :param pointC: some Point
        :param triangle_id: the triangle's ID
        :return: a 'Triangle' object
        """
        return Triangle(pointB.get_distance(pointC),
                        pointA.get_distance(pointC),
                        pointA.get_distance(pointB), triangle_id)

    @staticmethod
    def from_str(line: str, triangle_id=-1) -> "Triangle":
        """
        Initializes a Triangle with the given line.
        :param line: a line from an example file (like "3 x1 y1 x2 y2 x3 y3")
        :param triangle_id: the triangle's ID
        :return: a 'Triangle' object
        """
        if not line.startswith("3"):
            try:
                raise ValueError("Expected '3' as first character in line, got '{}'".format(line[0]))
            except IndexError:
                # line[0] threw an IndexError because 'line' is empty
                raise ValueError("given line is empty")
        nums = [int(num) for num in line.split(" ")]  # all numbers in the line (7 numbers, the first one is 3)
        if len(nums) != 7:
            raise ValueError("expected 7 numbers in line, got {} (line='{}')".format(len(nums), line))
        points = (Point(nums[i], nums[i+1]) for i in range(1, 6, 2))
        return Triangle.from_points(*points, triangle_id=triangle_id)

    @staticmethod
    def from_lengths_str(line: str, triangle_id=-1) -> "Triangle":
        """
        Initializes a triangle with the given line, where the line is in the format "a b c" and a, b and c represent the
        three side lengths.
        :param line: a text line
        :param triangle_id: the triangle's ID
        :return: a 'Triangle' object
        """
        lengths = (float(x) for x in line.split(" "))
        return Triangle(*lengths, triangle_id=triangle_id)

    @staticmethod
    def random(side_min: float = 50, side_max: float = 300) -> "Triangle":
        """
        Generates a random Triangle.
        :param side_min: The minimum length of a side
        :param side_max: THe maximum length of a side
        :return: a 'Triangle' object
        """
        lineA = random.randint(side_min, side_max)
        lineB = random.randint(side_min, side_max)
        # calculates the last line so that triangle inequality is not possible
        lineC = random.randint(max(abs(lineA-lineB) + 1, side_min), min(lineA + lineB - 1, side_max))
        return Triangle(lineA, lineB, lineC)

    def to_str(self) -> str:
        """
        Used by geometry.write_file
        :return: a string containing all side lengths.
        """
        return "{} {} {}".format(self.shortest_line, self.middle_line, self.longest_line)

    def __str__(self) -> str:
        return "Triangle({t.triangle_id}, {t.shortest_line}, {t.longest_line:.0f}, {t.shortest_line_angle:.0f}°)"\
            .format(t=self)
    
    def __repr__(self):
        return str(self)
    
    def get_origin_angle(self, placement: str) -> float:
        """
        Returns the angle of the triangle's angles which will touch a TriangleGroup's origin with the given placement
        :param placement: "lsb"/"slb" or "lbs"/"bls" or "sbl"/"bsl"
        :raise ValueError: unknown placement
        :return: an angle, for "lsb"/"slb" the smallest, for "lbs"/"bls" middle_line_angle,
                 for "sbl"/"bsl" longest_line_angle
        """
        if placement == "lsb" or placement == "slb":
            return self.shortest_line_angle
        if placement == "lbs" or placement == "bls":
            return self.middle_line_angle
        elif placement == "sbl" or placement == "bsl":
            return self.longest_line_angle
        raise ValueError("Unknown placement '{}'".format(placement))


class PlacedTriangle:
    """
    This class represents a triangle which is already placed in some TriangleGroup.
    """
    __slots__ = (
        "original_triangle",
        "origin", "origin_angle",
        "upper_arm_length", "upper_arm_point", "upper_arm_angle",
        "lower_arm_length", "lower_arm_point", "lower_arm_angle",
        "color"
    )

    def __init__(self, original_triangle: Triangle, origin: Point, origin_angle: float,
                 lower_arm_length: float, lower_arm_point: Point, lower_arm_angle: float,
                 upper_arm_length: float, upper_arm_point: Point, upper_arm_angle: float):
        """
        Initializes a PlacedTriangle object.
        :param original_triangle: the original 'Triangle' object from which this PlacedTriangle is derived
        :param origin: the point of the triangle which is the same as the TriangleGroup's origin
        :param origin_angle: the angle this triangle has on its origin
                             (for triangles which are not base triangles, it's the smallest angle)
        :param lower_arm_length: the length of the first arm of this Triangle in the TriangleGroup
        :param lower_arm_point: the point where the lower arm ends
        :param lower_arm_angle: the angle between the lower arm and the side from arm point to arm point
        :param upper_arm_length: the length of the arm which is placed above the lower arm
        :param upper_arm_point: the point where the upper arm ends
        :param upper_arm_angle: the angle between the upper arm and the side from arm point to arm point
        """
        self.original_triangle = original_triangle
        self.origin = origin
        self.origin_angle = origin_angle
        self.upper_arm_length = upper_arm_length
        self.upper_arm_point = upper_arm_point
        self.upper_arm_angle = upper_arm_angle
        self.lower_arm_length = lower_arm_length
        self.lower_arm_point = lower_arm_point
        self.lower_arm_angle = lower_arm_angle

        self.color = "black"  # saves the color of this triangle (for svg-graphic)

    def __repr__(self) -> str:
        return "PlacedTriangle({t.original_triangle.triangle_id}, {t.original_triangle.longest_line})".format(t=self)

    @staticmethod
    def place_triangle(triangle: Triangle, x_pos: float, angle: float, direction: str = "counter-clockwise",
                       placement: str = "lsb") -> Tuple[float, Optional["PlacedTriangle"]]:
        """
        Places a triangle with the origin on the given 'x_pos' with 'angle' degrees from the x-axis
        in 'direction' direction.
        :param triangle: The 'Triangle' object which should be placed
        :param x_pos: the origin's x-coordinate (y=0, on the x-axis)
        :param angle: angle on which the lower arm of the triangle should be placed
        :param direction: direction ("counter-clockwise" or "clockwise")
        :param placement: "lsb"/"slb" or "lbs"/"bls" or "sbl"/"bsl"
        :return: tuple containing the origin angle of the triangle and
                 an initialized 'PlacedTriangle' object or None if there isn't enough space (>180°)
        """
        origin_angle = triangle.get_origin_angle(placement)

        bottom_angle = angle
        top_angle = angle + origin_angle
        if top_angle > 180 and not math.isclose(top_angle, 180):
            return origin_angle, None

        origin = Point(x_pos, 0)

        if placement[0] == "l":
            bottom_length = triangle.longest_line
        elif placement[0] == "s":
            bottom_length = triangle.middle_line
        else:
            assert placement[0] == "b"
            bottom_length = triangle.shortest_line

        if placement[1] == "l":
            top_length = triangle.longest_line
        elif placement[1] == "s":
            top_length = triangle.middle_line
        else:
            assert placement[1] == "b"
            top_length = triangle.shortest_line

        if direction == "clockwise":
            bottom_angle = 180 - bottom_angle
            top_angle = 180 - top_angle

        lower_arm_point = Point(x_pos + bottom_length, 0)
        lower_arm_point.rotate_around(origin, bottom_angle)
        upper_arm_point = Point(x_pos + top_length, 0)
        upper_arm_point.rotate_around(origin, top_angle)
        return origin_angle, PlacedTriangle(triangle, origin, origin_angle,
                                            bottom_length, lower_arm_point, bottom_angle,
                                            top_length, upper_arm_point, top_angle,)

    def midpoint(self) -> Point:
        """
        Calculates the centroid of the triangle. Used for showing information (ID, ...) on triangle in svg-graphic
        :return: centroid as a 'Point'-object
        """
        x_sum = self.origin.x + \
                self.lower_arm_point.x + \
                self.upper_arm_point.x
        y_sum = self.origin.y + \
                self.lower_arm_point.y + \
                self.upper_arm_point.y
        return Point(x_sum/3, y_sum/3)

    def set_x(self, new_x_pos: float):
        """
        Sets the x-coordinate of this triangle's origin to 'new_x_pos'
        :param new_x_pos: new x-coordinate for the origin (the other two points are shifted)
        """
        x_diff = new_x_pos - self.origin.x
        self.origin.x = new_x_pos
        self.lower_arm_point.x += x_diff
        self.upper_arm_point.x += x_diff

    def svg(self, labels: bool = True, color_id="black") -> svgwrite.container.Group:
        """
        Returns the PlacedTriangle as an svg-graphic.
        :param labels: if True, adds labels for the ID and the points
        :param color_id: the color for the ID-text
        :return: an svg-Group
        """
        group = svgwrite.container.Group()
        group.add(svgwrite.shapes.Polygon(
            (self.origin.to_tuple(), self.lower_arm_point.to_tuple(), self.upper_arm_point.to_tuple()),
            fill=self.color, stroke="black", id="D"+str(self.original_triangle.triangle_id)))
        if labels:
            group_text = svgwrite.container.Group()
            group_text.scale(1, -1)
            pos = self.midpoint()
            group_text.translate(0, -2*pos.y)
            group_text.add(svgwrite.text.Text(str(self.original_triangle.triangle_id), pos.to_tuple(),
                                              fill=color_id, text_anchor="middle"))
            group.add(group_text)
        return group


class TriangleGroup:
    """
    This class stores multiple triangles which all have one origin on the x-axis
    """
    COLOR_GENERATOR = itertools.cycle([("#FF0000", "#FF8080", "#00FFFF"), ("#FFFF00", "#FFFF80", "#0000FF"),
                                       ("#FF00FF", "#FF80FF", "#00FF00"), ("#00FF00", "#80FF80", "#FF00FF"),
                                       ("#00FFFF", "#80FFFF", "#FF0000")])
    __slots__ = (
        "base_triangle",
        "placement_base_triangle",
        "direction",
        "triangles",
        "angle",
        "origin",
        "pre_group",
        "next_group",
        "points", "outer_lines",
        "relevant_points", "relevant_lines",
        "base_triangle_outer_angle",
        "placed_triangles",
        "outer_angle",
        "color_base_triangle", "color_triangles", "color_info"
    )

    def __init__(self, base_triangle: Triangle = None, direction: str = "counter-clockwise",
                 placement_base_triangle: str = "bsl"):
        """
        Initializes a TriangleGroup
        :param base_triangle: the triangle which should be placed first on the x-axis with 'placement_base_triangle'
                              if None, there is no base_triangle for this group
        :param direction: "counter-clockwise" or "clockwise". Defines the rotation of the group.
                          "counter-clockwise" means that the base_triangle's left point on the x-axis is the origin and
                          all triangles are added in counter-clockwise direction
        :param placement_base_triangle: the placement for 'base_triangle': "lsb"/"slb" or "lbs"/"bls" or "sbl"/"bsl"
        """
        # the following attributes are for collision detection when placing a group
        self.points = None  # all points from this group that are not the origin (2 per triangle)
        self.outer_lines = None  # all sides lying opposite of the origin (1 per triangle)
        self.relevant_points = None  # all points that are relevant for collision detection on the right side
                                                # the left that are relevant
        self.relevant_lines = None  # all lines that are relevant for collison detection on the right side

        self.origin = Point(0, 0)
        self.pre_group = None  # the group before this group
        self.next_group = None  # the group after this group
        self.direction = direction

        self.triangles = []  # all triangles (class 'Triangle') in this group
        self.placed_triangles = []  # all triangles (class 'PlacedTriangle') in this group
        self.placement_base_triangle = placement_base_triangle
        self.base_triangle = base_triangle
        self.outer_angle = None  # the angle from the outer point of the base triangle to the point which is most
                                 # outside (which has the greatest x-coord)
        self.color_base_triangle, self.color_triangles, self.color_info = next(self.COLOR_GENERATOR)
        if self.base_triangle is None:
            self.angle = 0
            self.base_triangle_outer_angle = None  # the base triangle's other angle on the x-axis that does not touch
                                                   # the origin
        else:
            self.angle = self.base_triangle.get_origin_angle(self.placement_base_triangle)
            if self.placement_base_triangle == "lsb" or self.placement_base_triangle == "bsl":
                self.base_triangle_outer_angle = self.base_triangle.middle_line_angle
            elif self.placement_base_triangle == "lbs" or self.placement_base_triangle == "sbl":
                self.base_triangle_outer_angle = self.base_triangle.shortest_line_angle
            elif self.placement_base_triangle == "slb" or self.placement_base_triangle == "bls":
                self.base_triangle_outer_angle = self.base_triangle.longest_line_angle

    def has_overlapping_point(self) -> bool:
        """
        Returns True when a triangle's point goes over the outer line of the base triangle.
        The outer line of the bases triangle is the line opposite of the origin.
        This information is used for determining how the triangles in the next group should be arranged (see
        get_sorted_triangles).
        :return: True (a point overlaps) or False
        """
        # line_point1 and line_point2 define the line of the base triangle opposite of the origin
        line_point1 = self.placed_triangles[0].lower_arm_point
        line_point2 = self.placed_triangles[0].upper_arm_point
        for point in self.points:
            if point != line_point2 and point != line_point1:
                # d is the outer product of AB and AX (A=line_point1, B=line_point2, X=point) (the cross product)
                d = (point.x - line_point1.x) * (line_point2.y - line_point1.y) - \
                    (point.y - line_point1.y) * (line_point2.x - line_point1.x)
                if d > 0:  # point lies on the right side of the line
                    return True
        return False

    def get_sorted_triangles(self) -> Iterator[Tuple[Triangle, str]]:
        """
        Sorts the triangles and gives information on how to place the triangles for a minimum of space usage.
        :return: a list containing tuples which contain a Triangle and the triangle's placement
        """
        if self.next_group is None or self.direction == "clockwise":
            # if self.next_group is None, this is the last group (with no base triangle), so the largest triangles
            # should be placed first and every triangle should place the smallest arm to the left side ("lsb")
            # if the direction is clockwise, this is the first group (usually for two group with the angle sum <
            # 180°) and the triangles should also be sorted from biggest to smallest
            return zip(sorted(self.triangles, key=lambda t: -t.middle_line), itertools.repeat("lsb"))
        elif self.pre_group is None:
            # this is the first group with no pre_group, so the shortest triangles should be placed first
            # the triangle's smallest arm should be on the right (lower arm) as defined by "slb"
            return zip(sorted(self.triangles, key=lambda t: t.middle_line), itertools.repeat("slb"))
        elif self.pre_group.base_triangle_outer_angle+self.angle > 180 or self.pre_group.has_overlapping_point():
            # either this group's angle is larger than the angle on the pre_group's right side
            # or a point in pre_group overlaps
            # the smallest triangle is placed on the right, the second smallest triangle is placed on the left,
            # the third smallest is placed on the right and so on
            # so that there are small triangles on the right and on the left
            triangles = sorted(self.triangles, key=lambda t: t.middle_line)
            start = triangles[::2]  # all triangles which should be placed on the right
            if len(triangles) % 2 == 1:
                # if the count of triangles is odd-numbered, it starts two triangles from the last (-2),
                # otherwise one (-1)
                end = triangles[-2::-2]  # all triangles which should be placed on the left
            else:
                end = triangles[-1::-2]
            # in the following line, all triangles get a placement so that the smalelst side is showing to the right
            # or left
            return zip(start+end, ["slb"]*len(start) + ["lsb"]*len(end))
        else:
            # there is no overlapping and this group's angle is not too large, so the smallest triangle is placed
            # first to give the next group a lot of space
            return zip(sorted(self.triangles, key=lambda t: t.middle_line), itertools.repeat("slb"))

    def __str__(self) -> str:
        return "TriangleGroup{}({}, {})".format(repr(self), repr(self.pre_group), repr(self.next_group))

    def copy(self) -> "TriangleGroup":
        """
        Copies this group. The base triangle, all triangles, the direction, the placement of the base triangle are
        copied. Placed triangles or the origin, points, outer_lines, ... are not copied.
        :return: a new 'TriangleGroup' object
        """
        group = TriangleGroup(self.base_triangle, self.direction, self.placement_base_triangle)
        group.extend(self.triangles)
        return group

    def __copy__(self) -> "TriangleGroup":
        return self.copy()

    def __deepcopy__(self, memodict=None) -> "TriangleGroup":
        return self.copy()

    def _place_triangle(self, triangle: Triangle, color: str, angle: float, placement: str) -> float:
        """
        Places a triangle with the given color, angle and placement.
        Adds the outer points and the outer line to self.points and self.outer_lines
        :param triangle: a 'Triangle' object to be placed
        :param color: a valid svg-color
        :param angle: an angle in degree
        :param placement: "lsb"/"slb" or "lbs"/"bls" or "sbl"/"bsl"
        :return: the origin angle of the placed triangle
        """
        additional_angle, placed_triangle = PlacedTriangle.place_triangle(triangle, 0, angle, self.direction, placement)
        if placed_triangle is None:
            raise ValueError("not enough space: Can't add {add}° to {a}° ({a}°+{add}°={sum}° > 180°".format(
                add=additional_angle, a=angle, sum=additional_angle+angle))
        placed_triangle.color = color
        self.points.append(placed_triangle.upper_arm_point)
        self.points.append(placed_triangle.lower_arm_point)
        self.outer_lines.append(tuple(sorted((placed_triangle.upper_arm_point, placed_triangle.lower_arm_point),
                                             key=lambda t: t.y)))
        self.placed_triangles.append(placed_triangle)
        return additional_angle

    def place(self, pre_group: Optional["TriangleGroup"], next_group: Optional["TriangleGroup"]):
        """
        Placed this group after pre_group (on the right side).
        :param pre_group: The group before this group
        :param next_group: The group after this group
        """
        self.pre_group = pre_group
        self.next_group = next_group
        self.points = [self.origin]
        self.outer_lines = []
        self.placed_triangles = []
        # PLACE THE TRIANGLES
        if self.base_triangle:
            # place base triangle
            angle = self._place_triangle(self.base_triangle, self.color_base_triangle, 0, self.placement_base_triangle)
        else:
            angle = 0
        if self.direction == "counter-clockwise":
            if self.pre_group:
                pre_group_outer_angle = self.pre_group.outer_angle
            else:
                pre_group_outer_angle = 0
            space = 180 - pre_group_outer_angle - self.angle
            if space > 0:
                angle += space
        if self.triangles:
            # place all triangles
            sorted_triangles = self.get_sorted_triangles()
            for triangle_and_placement in sorted_triangles:
                triangle, placement = triangle_and_placement
                angle += self._place_triangle(triangle, self.color_triangles, angle, placement)
        if self.pre_group:
            # place after self.pre_group
            def get_x(vertex, edge_bottom, edge_top, own_vertex=True):
                """
                Calculates an x-coordinate for the group with the given combination of a point and an edge.
                The point is 'vertex', the edge is defined by its endpoints edge_bottom and edge_top, where edge_top.y
                is greater than edge_bottom.y. 'own_vertex' must be True if the given vertex belongs to this group,
                otherwise False (when it belongs to the other group)
                """
                if edge_bottom.y <= vertex.y <= edge_top.y:  # the vertex must be able to hit the edge
                    if math.isclose(edge_bottom.y, edge_top.y, abs_tol=0.1):
                        # the edge is (nearly) horizontally aligned, so the vertex would collide with the end of the
                        # edge
                        if not own_vertex:
                            # the edge belongs to this group, so the end is on the left (smaller x-coord)
                            return min(edge_bottom.x, edge_top.x) - vertex.x
                        else:
                            # the edge belongs to the other group, so the end is on the right (greatest x-coord)
                            return max(edge_bottom.x, edge_top.x) - vertex.x
                    else:
                        # intersection_x is the x-coordinate of the intersection
                        # intersection_x is calculated by multiplying the height of the vertex relative to the height
                        # of the lower endpoint of the edge with the slope of the edge. To get an absolute value (not
                        # relative to edge_bottom.x), edge_bottom.x is added.
                        intersection_x = ((vertex.y - edge_bottom.y) *   # height of vertex relative to edge
                                          ((edge_top.x - edge_bottom.x) / (edge_top.y - edge_bottom.y)) +  # slope
                                          edge_bottom.x
                                          )
                        if own_vertex:
                            return intersection_x - vertex.x
                        else:
                            return vertex.x - intersection_x
                return None

            if not (self.direction == "counter-clockwise" and self.pre_group.direction == "clockwise" and
                    self.angle + self.pre_group.angle < 180):
                # go through all point-edge combinations and take the greatest x-pos
                max_x = -math.inf
                # the following loop tests all points with the belonging group's origin (all lines from the origin)
                for own in self.points:
                    for other, other_origin in self.pre_group.relevant_points:
                        new_x = get_x(own, other_origin, other, True)
                        if new_x is not None and new_x > max_x:
                            max_x = new_x
                        new_x = get_x(other, Point(0, 0), own, False)
                        if new_x is not None and new_x > max_x:
                            max_x = new_x
                # the following loop tests all own points with the pre_group's lines
                for own in self.points:
                    for other_line, _ in self.pre_group.relevant_lines:  # origin (_) not needed
                        new_x = get_x(own, other_line[0], other_line[1], True)
                        if new_x is not None and new_x > max_x:
                            max_x = new_x
                # the following loop tests all own outer lines with the pre_group's points
                for own_line in self.outer_lines:
                    for other, _ in self.pre_group.relevant_points:  # origin (_) not needed
                        new_x = get_x(other, own_line[0], own_line[1], False)
                        if new_x is not None and new_x > max_x:
                            max_x = new_x
                self.set_x(max_x)
            else:
                # the two groups do not overlap in any way, so this group's x-pos is the same as the pre_group's x-pos
                self.set_x(self.pre_group.origin.x)

        # CALCULATE ALL RELEVANT POINTS FOR PLACEMENT OF NEXT GROUP
        min_y = -1  # the minimum y-coordinate a point must have to be relevant
        self.relevant_points = []
        self.relevant_lines = []
        # add all relevant points from this group's triangles
        for outer_line in (self.outer_lines if self.direction == "counter-clockwise" else self.outer_lines[::-1]):
            if outer_line[1].y > min_y:  # outer_line[1] is the point with the greatest y-coord of the line
                if outer_line[0].y > min_y:
                    self.relevant_points.append((outer_line[0], self.origin))
                min_y = outer_line[1].y
                self.relevant_points.append((outer_line[1], self.origin))
                # one point (outer_line[1]) is relevant, so the whole line is relevant
                self.relevant_lines.append((outer_line, self.origin))
        if self.pre_group:
            # add all relevant points from pre_group
            for line, origin in self.pre_group.relevant_lines:
                if line[1].y > min_y:  # outer_line[1] is the point with the greatest y-coord of the line
                    if line[0].y > min_y:
                        self.relevant_points.append((line[0], origin))
                    min_y = line[1].y
                    self.relevant_points.append((line[1], origin))
                    # one point (outer_line[1]) is relevant, so the whole line is relevant
                    self.relevant_lines.append((line, origin))
        
        outer_point = self.placed_triangles[0].lower_arm_point if self.placed_triangles[0].lower_arm_point.y == 0 \
                        else self.origin
        self.outer_angle = 180 - outer_point.get_angle(
            min(self.relevant_points,
                key=lambda p: (outer_point.get_angle(p[0]) if p[0] != outer_point else math.inf))[0])

    def set_x(self, new_x_pos: float):
        """
        Sets the x coordinate of the origin to 'new_x_pos'. All other points are shifted.
        :param new_x_pos: the new x pos for the origin
        """
        self.origin.x = new_x_pos
        for triangle in self.placed_triangles:
            triangle.set_x(new_x_pos)

    def append(self, triangle: Triangle):
        """
        Adds a triangle to the group. The triangle is only added, not placed. Place all triangles with
        TriangleGroup.place.
        :param triangle: the new triangle
        :raise ValueError: the smallest angle of the triangle would make the angle of the group greater than 180°
        """
        new_angle = self.angle + triangle.shortest_line_angle
        if new_angle <= 180:
            self.angle = new_angle
            self.triangles.append(triangle)
        else:
            raise ValueError("not enough space {} > 180".format(new_angle))

    def extend(self, triangles: Iterable[Triangle]):
        """
        Adds
        :param triangles: Adds all triangles in 'triangles' to this group by calling TriangleGroup.append.
        :raise ValueError: see 'TriangleGroup.append'
        """
        for triangle in triangles:
            self.append(triangle)

    def svg(self, labels: bool = True, relevant_lines: bool = True) -> svgwrite.container.Group:
        """
        :param labels: if True, adds labels to the triangles for ID and points (passed to 'PlacedTriangle.svg')
        :param relevant_lines: if True, adds lines for the relevant lines and points to the groups
        :return: an SVG-Group containing the svg-representations of the placed triangles and all relevant points.
        """
        group = svgwrite.container.Group()
        for t in self.placed_triangles:
            group.add(t.svg(labels, color_id=self.color_info))
        if relevant_lines:
            for p, _ in self.relevant_points:
                group.add(svgwrite.shapes.Circle(p.to_tuple(), 3, fill=self.color_info))
            for line, _ in self.relevant_lines:
                group.add(svgwrite.shapes.Line(line[0].to_tuple(), line[1].to_tuple(), stroke=self.color_info,
                                               stroke_width=2.5))
        return group


def parse_file(path: str, validate: bool = True) -> List[Triangle]:
    """
    Parses a file specified by 'path'.
    :param path: file path
    :param validate: if True, checks that the file contains the right count of triangles (given in the first line)
    :return: a list of all triangles
    """
    with open(path, "r") as f:
        lines = f.readlines()
    if lines[0] == "type=lengths\n":
        # my own format, which contains only the side lengths of the triangles
        triangles = [Triangle.from_lengths_str(line, t_id) for t_id, line in enumerate(lines[1:], 1)]
    else:
        triangles = [Triangle.from_str(line.strip(), t_id) for t_id, line in enumerate(lines[1:], 1)]
        if validate:
            triangle_count = int(lines[0])
            triangle_length = len(triangles)
            if triangle_count != triangle_length:
                raise ValueError("Number of triangles in file is wrong. Expected '{}' (first line), got '{}'"
                                 .format(triangle_count, triangle_length))
    return triangles


def write_file(path: str, triangles: Iterable[Triangle]):
    """
    Writes a file containing 'triangles' in my own format (contains all side lengths)
    :param path: file path
    :param triangles: all triangles
    """
    with open(path, "w") as f:
        f.write("type=lengths")
        for t in triangles:
            f.write("\n" + t.to_str())


def save_svg(path: str, groups: Iterable[TriangleGroup], border_width: float = 5,
             labels: bool = True, relevant_lines: bool = False):
    """
    Saves the given 'groups' as an svg-graphic under 'path'.
    :param path: file path
    :param groups: all triangle groups
    :param border_width: specifies the size of a border which is added on all sides of the svg-graphic
    :param labels: if True, adds labels to the triangles for ID and points (passed to 'PlacedTriangle.svg')
    :param relevant_lines: if True, adds lines for the relevant lines and points to the groups
    """
    triangles = tuple(t for group in groups for t in group.placed_triangles)  # all triangles in all groups
    offset = (
        min(min(t.origin.x, t.lower_arm_point.x, t.upper_arm_point.x) for t in triangles) - border_width,
        min(min(t.origin.y, t.lower_arm_point.y, t.upper_arm_point.y) for t in triangles) - border_width,
    )
    size = (
        max(max(t.origin.x, t.lower_arm_point.x, t.upper_arm_point.x) for t in triangles) - offset[0] + border_width,
        max(max(t.origin.y, t.lower_arm_point.y, t.upper_arm_point.y) for t in triangles) - offset[1] + border_width
    )
    group = svgwrite.container.Group()
    # x-axis (green line)
    group.add(svgwrite.shapes.Line((offset[0], 0), (size[0] + offset[0], 0), stroke="green", stroke_width=3))
    group.scale(1, -1)
    group.translate(-offset[0], -size[1] - offset[1])
    for t in groups:
        group.add(t.svg(labels, relevant_lines))
    draw = svgwrite.Drawing(path, size)
    draw.add(group)
    draw.save(True)
