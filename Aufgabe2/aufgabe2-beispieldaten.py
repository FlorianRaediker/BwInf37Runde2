#!/usr/bin/env python3
"""
Geschrieben für die 2. Runde des 37. Bundeswettbewerb Informatik
Autor: Florian Rädiker
Teilnahme-ID: 48302

Aufgabe 2: Dreiecksbeziehungen

WRITTEN IN PYTHON3

Dieses Skript führt den in der Dokumentation beschriebenen Algorithmus für alle Beispieldaten im Ordner "beispieldaten"
aus und speichert die Ergebnisse in jeweiligen SVG-Dateien im Pfad "dreiecke{}.svg".
"""
import time
import trianglearranger


def create_output(filename, groups):
    print("""
{filename}
Gesamtabstand: {distance:.0f}m
Dreiecke: """.format(filename=filename, distance=groups[-1].origin.x))
    for group in groups:
        for triangle in (group.placed_triangles[::-1] if group.direction == "counter-clockwise" else
                         group.placed_triangles):
            print("D{t.original_triangle.triangle_id:>2} "
                  "({t.origin.x:4.0f}|{t.origin.y:4.0f}) "
                  "({t.upper_arm_point.x:4.0f}|{t.upper_arm_point.y:4.0f}) "
                  "({t.lower_arm_point.x:4.0f}|{t.lower_arm_point.y:4.0f})".format(t=triangle))
    print("\n")


print("ALLE WERTE AUF METER GERUNDET\n")
for i in range(1, 6):
    print("######\ndreiecke{}.txt".format(i))
    triangles = trianglearranger.parse_file("beispieldaten/dreiecke{}.txt".format(i))
    print("ALL TRIANGLES: ")
    for triangle in triangles:
        print("  ID{t.triangle_id:>2} shortest line:{t.shortest_line:5.1f} longest line:{t.longest_line:5.1f} "
              "smallest angle:{t.shortest_line_angle:4.1f}".format(t=triangle))
    t1 = time.perf_counter()
    best_distance, best_groups = trianglearranger.search_arrangement(triangles)
    t2 = time.perf_counter()
    print("whole time: {:.4f}".format(t2-t1))
    trianglearranger.save_svg("dreiecke{}.svg".format(i), best_groups)
    create_output("dreiecke{}.txt".format(i), best_groups)
