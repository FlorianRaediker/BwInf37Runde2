"""
Geschrieben für die 2. Runde des 37. Bundeswettbewerb Informatik
Autor: Florian Rädiker
Teilnahme-ID: 48302

Aufgabe 2: Dreiecksbeziehungen

WRITTEN IN PYTHON3

Dieses Modul ist für das Anordnen der Dreiecke zuständig. Die Funktion "search_arrangement" ordnet die Dreiecke mithilfe
der anderen in diesem Modul enthaltenen Funktionen und dem Modul "geometry" platzsparend an.
"""
import itertools
import math
import os
import sys
import time
from typing import List, Tuple, Iterator, Optional

# include site-packages folder
cwd = os.path.dirname(__file__)
sys.path.append(os.path.join(cwd, "./site-packages/"))
os.chdir(cwd)

from geometry import *

# CONSTANTS
TRIANGLE_SUBSET_FINDER_TOLERANCE = 0.2
BASE_TRIANGLES_ANGLE_TOLERANCE_FACTOR = 1.2


def search_arrangement(triangles: List[Triangle]) -> \
        Tuple[Optional[float], Optional[List[TriangleGroup]]]:
    """
    This function searches for a good arrangement for the given triangles by calling the functions 'arrange_triangles'
    and 'arrange_triangles_with_smallest' for the base triangle combinations from function 'base_triangles_generator'.
    :param triangles: all triangles
    :return: a tuple containing the distance and the (placed) instances of the calculated 'TriangleGroup's
    """
    angle_sum = sum(t.shortest_line_angle for t in triangles)

    print("Smallest angle sum = {:.2f}".format(angle_sum))
    if angle_sum <= 360:
        # the triangles can be placed in two groups
        print("Angle sum <= 360°")
        t1 = time.perf_counter()
        best_groups, best_distance = arrange_triangles_lt360(triangles, angle_sum)
        t2 = time.perf_counter()
        print("  time: {:.4f}".format(t2-t1))
        print("  BEST {:.2f}".format(best_distance))
    else:
        best_distance = math.inf
        best_groups = None
    for base_triangles, remaining_triangles, base_distance in base_triangles_generator(triangles, angle_sum):
        print("BASE len:{:2} distance:{:.3f}".format(len(base_triangles), base_distance))
        if base_distance >= best_distance:
            print("  new base distance too long: {:.3f} >= {:.3f}".format(base_distance, best_distance))
            break
        t1 = time.perf_counter()
        groups_normal, distance_normal = arrange_triangles(base_triangles, remaining_triangles)
        t2 = time.perf_counter()
        time_normal = t2-t1
        print("  time normal:   {:.4f}".format(time_normal))
        if distance_normal == base_distance:
            print("  skipping smallest because 'base distance' equals 'distance normal'")
            groups_smallest = None
            distance_smallest = math.inf
        else:
            t1 = time.perf_counter()
            groups_smallest, distance_smallest = arrange_triangles_with_smallest(base_triangles, remaining_triangles)
            t2 = time.perf_counter()
            time_with_smallest = t2-t1
            print("  time smallest: {:.4f}".format(time_with_smallest))
        print("  distance normal:   {:.2f}\n  distance smallest: {:.2f}".format(distance_normal, distance_smallest))
        if distance_normal < distance_smallest:
            new_distance = distance_normal
            new_groups = groups_normal
        else:
            new_distance = distance_smallest
            new_groups = groups_smallest
        if new_distance < best_distance:
            print("  BEST {:.2f}".format(new_distance))
            best_groups = new_groups
            best_distance = new_distance
    return best_distance, best_groups


def arrange_triangles(base_triangles: List[Triangle], triangles: List[Triangle]) -> Tuple[List[TriangleGroup], float]:
    """
    Arranges the given base triangles 'base_triangles' and other triangles 'triangles'.
    :param base_triangles: all base triangles
    :param triangles: all triangles that are no base triangles
    :return: a tuple containing a list of all triangle groups ('TriangleGroup') and the distance
    """
    best_distance = math.inf
    best_groups = None
    for first_base_triangle in base_triangles:
        for placement_base_triangle in ("bsl", "bls"):
            remaining_triangles = triangles.copy()  # do not modify the original list
            remaining_base_triangles = base_triangles.copy()
            remaining_base_triangles.remove(first_base_triangle)
            first_group = TriangleGroup(first_base_triangle, placement_base_triangle=placement_base_triangle)
            _, new_triangles = get_triangle_sum_subset(remaining_triangles, 180 - first_group.angle)
            first_group.extend(new_triangles)
            for t in list(new_triangles):
                remaining_triangles.remove(t)
            groups = [first_group]
            last_group_angle = first_group.base_triangle_outer_angle  # angle on the right side of the last group
            while remaining_base_triangles:  # add all base triangles
                diffs = []  # the results for all base triangles
                # search the best base triangle so it can be added next
                for base_triangle in remaining_base_triangles:
                    space = 180 - last_group_angle - base_triangle.middle_line_angle
                    s, group_triangles = get_triangle_sum_subset(remaining_triangles, space)
                    # diffs element contains: (remaining space, placement method, base triangle,
                    #                          other triangles for this group)
                    diffs.append((space - s, "bls", base_triangle, group_triangles))
                    space = 180 - last_group_angle - base_triangle.longest_line_angle
                    s, group_triangles = get_triangle_sum_subset(remaining_triangles, space)
                    diffs.append((space - s, "bsl", base_triangle, group_triangles))
                # take the base triangle with the smallest remaining space
                _, placement, best_base_triangle, best_next_triangles = min(diffs, key=lambda x: x[0])
                new_group = TriangleGroup(best_base_triangle, placement_base_triangle=placement)
                new_group.extend(best_next_triangles)
                groups.append(new_group)
                last_group_angle = new_group.base_triangle_outer_angle
                for t in list(best_next_triangles):
                    remaining_triangles.remove(t)
                remaining_base_triangles.remove(best_base_triangle)
            # all base triangles are placed, if there are triangles left, place them on the right side
            if remaining_triangles:
                space = 180 - last_group_angle  # space for the last group
                s, group_triangles = get_triangle_sum_subset(remaining_triangles, space)
                group = TriangleGroup()
                group.extend(group_triangles)
                groups.append(group)
                for t in list(group_triangles):
                    remaining_triangles.remove(t)
            # if there are still triangles left, insert them in the existing groups
            if remaining_triangles:
                try:
                    insert_remaining_triangles(groups, remaining_triangles)
                except ValueError:
                    # ValueError means there is not enough space in the existing groups, so skip this
                    continue
            place_groups(groups)
            distance = groups[-1].origin.x  # "Gesamtabstand"
            if distance < best_distance:
                best_distance = distance
                best_groups = groups
    return best_groups, best_distance


def arrange_triangles_with_smallest(base_triangles: List[Triangle], triangles: List[Triangle]) -> \
        Tuple[List[TriangleGroup], float]:
    """
    Arranges the given base triangles 'base_triangles' and other triangles 'triangles'.
    Like 'arrange_triangles', but tries to include one small triangle in every group.
    :param base_triangles: all base triangles
    :param triangles: all triangles that are no base triangles
    :return: a tuple containing a list of all triangle groups ('TriangleGroup') and the distance
    """
    def get_smallest_triangle(remaining_smallest_triangles: List[Triangle], max_angle: float) -> Optional[Triangle]:
        """
        Searches for the biggest possible triangle in 'remaining_smallest_triangles'. The triangle's smallest angle
        should not be greater than 'max_angle'. Returns none if there is no triangle small enough for 'max_angle' or if
        'remaining_smallest_triangles' is empty.
        """
        for smallest_triangle in remaining_smallest_triangles:
            if smallest_triangle.shortest_line_angle <= max_angle:
                return smallest_triangle
        return None

    triangles = triangles.copy()  # do not modify the original list
    # smallest_triangles contains the smallest triangles from 'triangles' (by middle line), sorted by the smallest
    # angle. There is one triangle for every group (one for every base triangle + one for the last group)
    smallest_triangles = sorted(sorted(triangles, key=lambda t: t.middle_line)[:len(base_triangles)+1],
                                key=lambda t: -t.shortest_line_angle)
    for t in smallest_triangles:
        triangles.remove(t)

    best_distance = math.inf
    best_groups = None
    for first_base_triangle in base_triangles:
        for placement_base_triangle in ("bsl", "bls"):
            remaining_smallest_triangles = smallest_triangles.copy()  # do not modify the original list
            remaining_triangles = triangles.copy()  # do not modify the original list

            first_group = TriangleGroup(first_base_triangle, placement_base_triangle=placement_base_triangle)
            new_smallest_triangle = get_smallest_triangle(remaining_smallest_triangles, 180 - first_group.angle)
            if new_smallest_triangle is not None:
                _, new_triangles = get_triangle_sum_subset(
                    remaining_triangles,
                    180 - first_group.angle - new_smallest_triangle.shortest_line_angle
                )
                remaining_smallest_triangles.remove(new_smallest_triangle)
                first_group.append(new_smallest_triangle)
                first_group.extend(new_triangles)
            else:
                _, new_triangles = get_triangle_sum_subset(remaining_triangles, 180 - first_group.angle)
                first_group.extend(new_triangles)
                remaining_triangles.append(remaining_smallest_triangles.pop(0))

            for t in list(new_triangles):
                remaining_triangles.remove(t)
            groups = [first_group]
            last_group_angle = first_group.base_triangle_outer_angle  # angle on the right side of the last group
            remaining_base_triangles = base_triangles.copy()
            remaining_base_triangles.remove(first_base_triangle)
            while remaining_base_triangles:  # add all base triangles
                diffs = []  # the results for all base triangles
                # search the best base triangle so it can be added next
                for base_triangle in remaining_base_triangles:
                    space = 180 - last_group_angle - base_triangle.middle_line_angle
                    new_smallest_triangle = get_smallest_triangle(remaining_smallest_triangles, space)
                    if new_smallest_triangle is not None:
                        space -= new_smallest_triangle.shortest_line_angle
                    s, group_triangles = get_triangle_sum_subset(remaining_triangles, space)
                    if new_smallest_triangle is not None and space - s > 1:
                        space += new_smallest_triangle.shortest_line_angle
                        new_smallest_triangle = None
                        s, group_triangles = get_triangle_sum_subset(remaining_triangles, space)
                    # diffs element contains: (remaining space, placement method, base triangle,
                    #                          other triangles for this group, a smallest triangle if there is one
                    #                                                          (otherwise None))
                    diffs.append((space - s, "bls", base_triangle, group_triangles, new_smallest_triangle))

                    space = 180 - last_group_angle - base_triangle.longest_line_angle
                    new_smallest_triangle = get_smallest_triangle(remaining_smallest_triangles, space)
                    if new_smallest_triangle is not None:
                        space -= new_smallest_triangle.shortest_line_angle
                    s, group_triangles = get_triangle_sum_subset(remaining_triangles, space)
                    if new_smallest_triangle is not None and space - s > 1:
                        space += new_smallest_triangle.shortest_line_angle
                        new_smallest_triangle = None
                        s, group_triangles = get_triangle_sum_subset(remaining_triangles, space)
                    diffs.append((space - s, "bsl", base_triangle, group_triangles, new_smallest_triangle))
                # take the base triangle with the smallest remaining space
                _, placement, best_base_triangle , best_group_triangles, new_smallest_triangle = min(diffs,
                                                                                                     key=lambda x: x[0])
                new_group = TriangleGroup(best_base_triangle, placement_base_triangle=placement)
                new_group.extend(best_group_triangles)
                if new_smallest_triangle is None:
                    # one triangle in remaining_smallest_triangles is not needed anymore (there is one group that does
                    # not need a smallest_triangle/there is not enough space for the base triangle)
                    try:
                        remaining_triangles.append(remaining_smallest_triangles.pop(0))
                    except IndexError:
                        pass  # when remaining_smallest_triangles is already empty
                else:
                    new_group.append(new_smallest_triangle)
                    remaining_smallest_triangles.remove(new_smallest_triangle)
                groups.append(new_group)
                last_group_angle = new_group.base_triangle_outer_angle
                for t in list(best_group_triangles):
                    remaining_triangles.remove(t)
                remaining_base_triangles.remove(best_base_triangle)
            remaining_triangles.extend(remaining_smallest_triangles)
            # all base triangles are placed, if there are triangles left, place them on the right side
            if remaining_triangles:
                space = 180 - last_group_angle  # space for the last group
                s, group_triangles = get_triangle_sum_subset(remaining_triangles, space)
                group = TriangleGroup()
                group.extend(group_triangles)
                groups.append(group)
                for t in list(group_triangles):
                    remaining_triangles.remove(t)
            # if there are still triangles left, insert them in the existing groups
            if remaining_triangles:
                try:
                    insert_remaining_triangles(groups, remaining_triangles)
                except ValueError:
                    # ValueError means there is not enough space in the existing groups, so skip this
                    continue
            place_groups(groups)
            distance = groups[-1].origin.x  # "Gesamtabstand"
            if distance < best_distance:
                best_distance = distance
                best_groups = groups
    return best_groups, best_distance


def arrange_triangles_lt360(triangles: List[Triangle], angle_sum: float) -> Tuple[TriangleGroup, TriangleGroup]:
    """
    Arranges all triangles in 'triangles' which have the smallest angle sum 'angle_sum' in two groups (angle sum must be
    less than 360°).
    :param triangles: all triangles
    :param angle_sum: the sum of all the triangle's smallest angles
    :return: two TriangleGroups
    """
    _, triangles1 = get_triangle_sum_subset(triangles, angle_sum / 2)
    triangles1 = list(triangles1)
    triangles2 = [t for t in triangles if t not in triangles1]
    group1 = TriangleGroup(placement_base_triangle="lsb", direction="clockwise")
    group1.extend(triangles1)
    group2 = TriangleGroup(placement_base_triangle="lsb")
    group2.extend(triangles2)
    groups = [group1, group2]
    place_groups(groups)
    return groups, group2.origin.x


def place_groups(groups: List[TriangleGroup]):
    """
    Places all groups in 'groups' by calling 'TriangleGroup.place'
    :param groups: all groups
    """
    groups_mod = [None] + groups + [None]
    for i in range(1, len(groups) + 1):
        groups_mod[i].place(groups_mod[i - 1], groups_mod[i + 1])


def insert_remaining_triangles(groups: List[TriangleGroup], triangles: List[Triangle]):
    """
    Inserts all remaining triangles 'triangles' in the groups 'groups'.
    :param groups: all groups
    :param triangles: the remaining triangles
    :raise ValueError: there is not enough space for all triangles
    """
    for triangle in sorted(triangles, key=lambda t: -t.shortest_line_angle):
        # sort groups by space, try with group with the most space first
        for group in sorted(groups, key=lambda g: abs(90 - g.angle)):
            if 180 - group.angle >= triangle.shortest_line_angle:
                # there is enough space in this group
                group.append(triangle)
                break
        else:
            raise ValueError("not enough space for all triangles")


def base_triangles_generator(triangles: List[Triangle], angle_sum: float) -> \
        Iterator[Tuple[List[Triangle], List[Triangle], float]]:
    """
    Yields good base triangle combinations. The required distance for the base triangles increases with every
    combination.
    :param triangles: All available triangles
    :param angle_sum: the sum of the triangle's smallest angles
    :return: generator yields tuples containing the base triangles, all remaining triangles and the distance of the base
             triangle's smallest side
    """
    class SortMethod:
        def __init__(self, triangles: List[Triangle], sort_key):
            """
            A 'SortMethod' saves a certain sort method for a base triangle. One can retrieve the next available base
            triangle combination by calling 'SortMethod.get_next_combination'. The distance for the next available
            combination is saved in 'SortMethod.distance'. You can also compare instances of 'SortMethod' with "<" or
            ">". The instances are sorted by their next distance.
            You can access the available angle for the next combination with 'SortMethod.available_angle' and the angle
            of all remaining triangles (which are currently not included in the combination) in
            'SortMethod.remaining_angle'. The calculation of the available angle is described in the documentation.
            FOR FURTHER INFORMATION ON BASE TRIANGLE COMBINATIONS AND SORT METHODS, PLEASE SEE THE DOCUMENTATION.
            :param triangles: all triangles
            :param sort_key: sort key for selection of next base triangle combination
            """
            self.triangles = sorted(triangles, key=sort_key)
            self.count = 1
            self.next_distance = 0
            self.available_angle = (180 - self.triangles[0].longest_line_angle) + \
                                   (180 - self.triangles[0].middle_line_angle)
            self.remaining_angle = angle_sum - self.triangles[0].shortest_line_angle
        
        def __lt__(self, other):
            return self.next_distance < other.next_distance
        
        def __gt__(self, other):
            return self.next_distance > other.next_distance
        
        def get_next_combination(self):
            return self.triangles[:self.count], self.triangles[self.count:], self.next_distance
    # sort methods: sort by: less width (on x-axis), small triangles (by longest side), small angles on x-axis
    sort_methods = (lambda t: t.shortest_line, lambda t: t.longest_line, lambda t: -t.shortest_line_angle)
    methods = tuple(SortMethod(triangles, sort_key) for sort_key in sort_methods)
    last_distance = -1
    while True:
        method = min(methods)  # method with the smallest distance
        if method.next_distance == math.inf:
            # there are no base triangle combinations left
            break
        if method.remaining_angle < method.available_angle * BASE_TRIANGLES_ANGLE_TOLERANCE_FACTOR and \
                method.next_distance > last_distance:
            last_distance = method.next_distance
            yield method.get_next_combination()
        try:
            method.next_distance += method.triangles[method.count-1].shortest_line
            method.remaining_angle -= method.triangles[method.count].shortest_line_angle
            method.available_angle += 180 - method.triangles[method.count].middle_line_angle \
                                          - method.triangles[method.count].longest_line_angle
            method.count += 1
        except IndexError:
            method.next_distance = math.inf


def get_triangle_sum_subset(triangles: List[Triangle], required_sum: float):
    """
    Calculates a list containing all triangles from 'triangles' so that the smallest angles of the triangles sum up to
    'required_sum'.
    The 'TRIANGLE_SUBSET_FINDER_TOLERANCE' constant is used as tolerance for the sum.
    :param triangles: a list of triangles
    :param required_sum: the required sum for the subset in degree
    :return: a tuple containing the sum of the triangle's smallest angles and the triangles
    """
    if required_sum == 0 or not triangles:
        return 0, ()
    s = sum(t.shortest_line_angle for t in triangles)
    if s < required_sum:
        return s, triangles
    smallest_angle = min(triangles, key=lambda t: t.shortest_line_angle).shortest_line_angle
    greatest_angle = max(triangles, key=lambda t: t.shortest_line_angle).shortest_line_angle
    if smallest_angle > required_sum:
        # no triangle is small enough for required_sum
        return required_sum, []
    best_sum = -math.inf
    best_values = None
    min_triangle_count = math.floor(required_sum / greatest_angle)
    if min_triangle_count < 1:
        min_triangle_count = 1
    max_triangle_count = min(len(triangles), math.ceil(required_sum / smallest_angle))
    if max_triangle_count < min_triangle_count:
        max_triangle_count = min_triangle_count
    for i in range(min_triangle_count, max_triangle_count+1):
        for values in itertools.combinations(triangles, i):
            s = sum(t.shortest_line_angle for t in values)
            if best_sum <= s <= required_sum:
                best_sum = s
                best_values = values
                if math.isclose(s, required_sum, abs_tol=TRIANGLE_SUBSET_FINDER_TOLERANCE):
                    return best_sum, values
    return best_sum, best_values
