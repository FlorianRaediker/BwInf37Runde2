"""
Geschrieben für die 2. Runde des 37. Bundeswettbewerb Informatik
Autor: Florian Rädiker
Teilnahme-ID: 48302

Aufgabe 1: Lisa rennt

WRITTEN IN PYTHON3

Dieses Modul stellt alle Klassen bereit, die nötig sind, um Punkte, Nodes oder Lines (Strecken bzw. Kanten)
darzustellen und Berechnungen (Distanz, Schnittpunkt usw.) anzustellen.
"""
import math
from typing import List


class Point:
    """
    Represents one point in a 2d coordinate system.
    """
    __slots__ = ["x", "y"]

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "P({x:.2f}|{y:.2f})".format(x=self.x, y=self.y)

    def to_tuple(self):
        """
        Creates a tuple containing the two values for x and y
        :return: (round(self.x, 2), round(self.y, 2))
        """
        return round(self.x, 2), round(self.y, 2)

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

    def get_distance(self, other):
        """
        Calculates the distance between this point and 'other'
        :param other: some Point
        :return: distance (as decimal.Decimal)
        """
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def has_same_point(self, other: "Point"):
        """
        Compares this Point (or Node) with 'other' (Point or Node) concerning the x/y-position.
        This is especially useful to find out if different Nodes are actually on the same position.
        :param other: Point (or Node) to compare with
        :return: bool (True -> same position, False -> different position)
        """
        return math.isclose(self.x, other.x) and math.isclose(self.y, other.y)


class Node(Point):
    def __init__(self, x: float, y: float,
                 neighbors: List["Node"] = None, edges: List["Edge"] = None, polygon_id=None):
        """
        Creates a 'Node'-object. Beside the x/y-position, other parameters can be used to link with other Nodes,
        Segments or Polygons.
        Every Node has an attribute 'Node.last_time' as well, which stores the time when Lisa should pass this
        Node to get her bus (used by the Dijkstra-Algorithm). The 'parent' attribute saves the parent Node, which should
        be passed next.
        :param x: x-coordinate
        :param y: y-coordinate
        :param neighbors: Optional. Specify (all) the visible Nodes here.
        :param edges: Optional. Specify the two polygon-edges which have this Node as an end point.
        :param polygon_id: Optional. Specify to which polygon this Node belongs with an ID. Used to exclude points from
        the same polygon.
        """
        super().__init__(x, y)
        self.last_time = -math.inf
        if not neighbors:
            self.neighbors = []
        else:
            self.neighbors = neighbors
        self.polygon_neighbors = []
        if not edges:
            self.edges = set()
        else:
            assert len(edges) == 2
            self.edges = edges
        self.parent = None
        self.polygon = None
        self.polygon_id = polygon_id

    def __repr__(self):
        return "Node({x:.2f}|{y:.2f})".format(x=self.x, y=self.y)

    def get_rotated_on_y_axis(self, angle: float = 30):
        """
        Creates a Node on the y-axis (x=0) 'degree' degrees above this point.
        (Imagine a right-angled triangle where the first leg is on the y-axis, the second leg goes straight from this
        point to the y-axis and the hypotenuse goes from this point to the returned Node.
        The given angle is between the hypotenuse and the second leg. )
        This Node should be in the first quadrant (positive x/y) for sensible results.
        :param angle: Should be greater or equal to 0 and smaller than 90.
        :return: a Node on the y-axis
        """
        return Node(0, self.y + (math.tan(math.radians(angle)) * self.x))
    
    def reload_last_time(self, new_parent: "Node", speed: float):
        """
        Reloads the 'last_time' attribute when a new, possibly better parent for this Node was found.
        If the resulting time is better (later), then the new parent and time are set.
        :param new_parent: new parent Node
        :param speed: Lisa's speed in meters per second
        """
        new_time = new_parent.last_time - self.get_distance(new_parent) / speed
        if new_time > self.last_time:
            self.parent = new_parent
            self.last_time = new_time


class LineSegment:
    """
    Represents a line segment from 'LineSegment.p1' to 'LineSegment.p2'
    """

    def __init__(self, point1: Point, point2: Point):
        """
        Creates a new 'LineSegment'. Additionally, the attributes 'length' and 'angle' (with the first point as origin)
        are calculated.
        :param point1: The one end of the line segment.
        :param point2: The other end of the line segment.
        """
        self.p1 = point1
        self.p2 = point2
        self.length = self.p1.get_distance(self.p2)
        self.angle = (math.atan2(self.p2.x - self.p1.x, self.p2.y - self.p1.y) + math.pi)  # line down is 0 rad, to
                                                                                           # left is 1/2pi rad, ...

    def __repr__(self):
        return "Segment({p1},{p2})".format(p1=self.p1, p2=self.p2)

    def in_range(self, point: Point):
        """
        Returns True if the given point is in range of this segment, comparing the x-values (or, if the line is
        vertical, the y-values)
        :param point: Some point of type 'Point'
        :return: bool (True or False)
        """
        if self.p1.x == self.p2.x:
            # vertical
            return (self.p1.y <= point.y <= self.p2.y) or (self.p2.y <= point.y <= self.p1.y)
        return (self.p1.x <= point.x <= self.p2.x) or (self.p2.x <= point.x <= self.p1.x)


class Edge(LineSegment):
    def __init__(self, point1: Node, point2: Node):
        """
        An 'Edge' is similar to 'LineSegment', but the resulting segment between the two Nodes is added automatically
        as an edge to both Nodes. Additionally, both Nodes are connected by adding the other Node respectively as a
        neighbor.
        :param point1: Some Node.
        :param point2: Some Node.
        """
        super().__init__(point1, point2)
        self.p1.edges.add(self)
        self.p1.polygon_neighbors.append(self.p2)
        self.p2.edges.add(self)
        self.p2.polygon_neighbors.append(self.p1)


class Polygon:
    def __init__(self, vertices: List[Node], polygon_id=None, addition: List[Point] = None):
        self.original_points = vertices

        self.points = vertices
        for node in self.points:
            node.polygon = self
            node.polygon_id = polygon_id
        self.edges = [Edge(vertices[i], vertices[i-1]) for i in range(len(vertices))]
        self.small_polygons = []
        if addition:
            new_vertices = []
            for vertex in vertices:
                addition_points = [Node(vertex.x-point.x, vertex.y-point.y) for point in addition]
                self.small_polygons.append(addition_points)
                new_vertices.extend(point for point in addition_points if not self.point_in_polygon(point))
            midpoint = self.calc_midpoint()
            vertices = sorted(new_vertices, key=lambda p: midpoint.get_angle(p))
            new_edges = [LineSegment(vertices[i], vertices[i - 1]) for i in range(len(vertices))]
            first_overlapping = True
            for edge in self.edges:
                if get_intersection(new_edges[0], edge):
                    break
            else:
                first_overlapping = False
            last_overlapping = first_overlapping
            for i in range(len(vertices)-1, -1, -1):
                for edge in self.edges:
                    if get_intersection(new_edges[i], edge):
                        break
                else:
                    last_overlapping = False
                    continue
            
                if last_overlapping:
                    del vertices[i]
                last_overlapping = True
            if last_overlapping and first_overlapping:
                del vertices[0]
            self.edges = [Edge(vertices[i], vertices[i - 1]) for i in range(len(vertices))]
            self.points = vertices
            for node in self.points:
                node.polygon = self
                node.polygon_id = polygon_id

    @staticmethod
    def from_str(text: str, polygon_id=None, minkowski_add=None) -> "Polygon":
        numbers = text.strip().split(" ")
        number_count = int(numbers[0])
        assert len(numbers) == number_count * 2 + 1  # text should be "n x1 y1 x2 y2 ... xn yn"
        vertices = [Node(int(numbers[i]), int(numbers[i + 1])) for i in range(1, len(numbers), 2)]
        return Polygon(vertices, polygon_id, minkowski_add)
    
    def calc_midpoint(self):
        return Point(sum(p.x for p in self.points)/len(self.points), sum(p.y for p in self.points)/len(self.points))

    def point_in_polygon(self, point: Point) -> bool:
        """
        Determines if 'point' lies in this polygon.
        :param point: a 'Point'
        :return: True if the point lies in this polygon otherwise False
        """
        # count the intersections to the y-axis
        line = LineSegment(point, Point(0, point.y))
        count = 0
        count_under = 0
        count_over = 0
        for edge in self.edges:
            intersection = get_intersection(line, edge)
            if intersection is None:
                continue
            if intersection.has_same_point(point):
                return True
            cond1 = intersection.has_same_point(edge.p1)  # intersection is on point edge.p1
            cond2 = intersection.has_same_point(edge.p2)  # intersection is on point edge.p2
            if (not cond1 and not cond2):
                count += 1
            elif (cond1 and edge.p2.y < line.p2.y) or (cond2 and edge.p1.y < line.p2.y):
                count_under += 1
            elif (cond1 and edge.p2.y > line.p2.y) or (cond2 and edge.p1.y > line.p2.y):
                count_over += 1
        if count_under%2 != count_over%2:
            return True
        return (count+count_under) % 2 == 1  # if number is odd, point lies in this polygon


def get_intersection(line1: LineSegment, line2: LineSegment):
    """
    Returns the intersection point of two lines 'lineA' and 'lineB'. Otherwise, if there is no intersection, returns
    None.
    The function looks for an intersection point between the two lines assuming that they are both unlimited (there is
    an intersection unless the two lines are parallel) and then checks if this intersection point is in range
    ('LineSegment.in_range') of both lines.
    :param line1: Some 'LineSegment'
    :param line2: Some 'LineSegment'
    :return: the intersection point of type 'Point' or 'None' if the lines do not intersect.
    """
    if line1.p1 == line2.p1 or line1.p1 == line2.p2 or line1.p2 == line2.p1 or line1.p2 == line2.p2:
        return None

    # get the intersection assuming that both lineA and lineB are unlimited lines
    x_diff = Point(line1.p1.x - line1.p2.x, line2.p1.x - line2.p2.x)
    y_diff = Point(line1.p1.y - line1.p2.y, line2.p1.y - line2.p2.y)

    def crossproduct(a, b):
        return (a.x) * (b.y) - (a.y) * (b.x)

    div = crossproduct(x_diff, y_diff)
    if div == 0:
        return None

    d = Point(crossproduct(line1.p1, line1.p2), crossproduct(line2.p1, line2.p2))
    x = crossproduct(d, x_diff) / div
    y = crossproduct(d, y_diff) / div
    intersection = Point(x, y)
    # verify that the calculated intersection is in range of both lines
    if line1.in_range(intersection) and line2.in_range(intersection):
        return intersection
    return None
