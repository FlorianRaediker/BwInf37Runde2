#!/usr/bin/env python3
"""
Geschrieben für die 2. Runde des 37. Bundeswettbewerb Informatik
Autor: Florian Rädiker
Teilnahme-ID: 48302

Aufgabe 1: Lisa rennt

WRITTEN IN PYTHON3

Dises Skript führt für die Beispieldaten im Ordner "beispieldaten" die Berechnung für Lisas Weg aus.
"""
import time
import datetime
import traceback
import math

from way_searcher import WaySearcher


for i in range(1, 6):
    try:
        with open("beispieldaten/lisarennt{}.txt".format(i), "r") as f:
            searcher = WaySearcher.from_str(f.read())
        t1_vis = time.perf_counter()
        searcher.create_visibility_graph()
        t2_vis = time.perf_counter()
        t1_dij = time.perf_counter()
        way, way_length, way_time = searcher.dijkstra()
        t2_dij = time.perf_counter()
        bus_time = way[-1].y / searcher.bus_speed
        print("""########
lisarennt{i}.txt
Vis. Graph time: {vis_time}
Dijkstra   time: {dij_time}""".format(i=i, vis_time=t2_vis - t1_vis, dij_time=t2_dij - t1_dij))
        if way[0].last_time == -math.inf:
            print("\nEs konnte kein Weg gefunden werden. ")
        else:
            print("""
Startzeit: {start_time.hour}:{start_time.minute:02}:{start_time.second:02} Uhr (abgerundet)
Zielzeit:  {y_time.hour}:{y_time.minute:02}:{y_time.second:02} Uhr (abgerundet)
y-Koord:   {y_bus:.0f}
Wegdauer:  {way_time.minute} Minuten {way_time.second} Sekunden (abgerundet)
Weglänge:  {way_length:.0f}m
WEG:
Starte beim Haus ({house.x}|{house.y}) (ID: 'L')""".format(
                    start_time=datetime.datetime(100, 1, 1, hour=7, minute=30) +
                               datetime.timedelta(seconds=way[0].last_time),
                    y_time=datetime.datetime(100, 1, 1, hour=7, minute=30) + datetime.timedelta(seconds=bus_time),
                    y_bus=way[-1].y,
                    way_time=datetime.datetime(100, 1, 1) + datetime.timedelta(seconds=way_time),
                    way_length=way_length,
                    house=way[0]
                )
            )
        for p in way[1:]:
            print("gehe zu ({way_point.x:3.0f}|{way_point.y:3.0f}) (ID: {id})"
                  .format(way_point=p,
                          id="'P" + str(p.polygon_id) + "'" if p.polygon_id is not None else "keine (Endpunkt)"))
        print("\n")
        try:
            with open("beispieldaten-svg/lisarennt{}.svg".format(i), "r") as src, \
                    open("solutions/solution{}.svg".format(i), "w") as f:
                while True:
                    line = src.readline()
                    if not line:  # end of file
                        break
                    if "polyline" in line:
                        # replace this line with way
                        line = '      <polyline id="R" points="{points}" ' \
                               'fill="none" stroke="#000080" stroke-width="4"/>\n'\
                            .format(points=" ".join("{p.x:.2f},{p.y:.2f}".format(p=p) for p in way))
                        f.write(line)
                        break
                    f.write(line)
                f.write(src.read())  # write rest to f
        except FileNotFoundError:
            pass
    except FileNotFoundError: 
        print("Die Datei 'beispieldaten/lisarennt{}.txt' konnte nicht gefunden werden. Stellen Sie "
              "sicher, dass sich der 'beispieldaten'-Ordner im Arbeitsverzeichnis befindet. ".format(i))
    except Exception as e:
        print("Leider ist folgender Fehler aufgetreten und lisarennt{}.txt konnte nicht oder nicht vollständig "
              "bearbeitet werden. ".format(i))
        traceback.print_exc()
