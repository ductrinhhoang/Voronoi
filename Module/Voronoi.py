import math
from collections import defaultdict
from Module import DifProcesses
# import timeit
import time
from Module import DifClasses
import os


class Voronoi:
    def __init__(self, points):
        self.HalfEdges = []  # half edges
        self.arc = None  # binary tree
        self.circle_events = DifClasses.Queue()
        self.voronoi_vertex = defaultdict(list)
        self.inf_x = 0
        self.sup_x = 1920
        self.inf_y = 0
        self.sup_y = 1920
        self.points = DifClasses.Queue()
        for pts in points:
            point = DifClasses.Point(pts[0], pts[1])
            self.points.push(point)

    def process(self):
        while not self.points.empty():
            if not self.circle_events.empty() and (self.circle_events.top().x <= self.points.top().x):
                self.process_circle_event()
            else:
                self.process_site_event()

        while not self.circle_events.empty():
            self.process_circle_event()

        self.finish_edges()

    def process_site_event(self):
        site = self.points.pop()
        self.arc_insert(site)

    def process_circle_event(self):
        event = self.circle_events.pop()

        if event.valid:
            s = DifClasses.HalfEdge(event.point)
            self.HalfEdges.append(s)

            arc = event.arc
            self.voronoi_vertex[arc.site].append(event.point)
            if arc.pprev is not None:
                self.voronoi_vertex[arc.pprev.site].append(event.point)
                arc.pprev.pnext = arc.pnext
                arc.pprev.HalfEdge1 = s
            if arc.pnext is not None:
                self.voronoi_vertex[arc.pnext.site].append(event.point)
                arc.pnext.pprev = arc.pprev
                arc.pnext.HalfEdge0 = s

            if arc.HalfEdge0 is not None:
                arc.HalfEdge0.finish(event.point)
            if arc.HalfEdge1 is not None:
                arc.HalfEdge1.finish(event.point)

            if arc.pprev is not None:
                self.check_circle_event(arc.pprev, event.x)
            if arc.pnext is not None:
                self.check_circle_event(arc.pnext, event.x)

    def arc_insert(self, site):
        if self.arc is None:
            self.arc = DifClasses.Arc(site)
        else:
            arc_at_site = self.arc
            while arc_at_site is not None:
                flag, z = self.intersect(site, arc_at_site)
                if flag:
                    flag, __ = self.intersect(site, arc_at_site.pnext)
                    if (arc_at_site.pnext is not None) and (not flag):
                        arc_at_site.pnext.pprev = DifClasses.Arc(
                            arc_at_site.site, arc_at_site, arc_at_site.pnext)
                        arc_at_site.pnext = arc_at_site.pnext.pprev
                    else:
                        arc_at_site.pnext = DifClasses.Arc(
                            arc_at_site.site, arc_at_site)
                    arc_at_site.pnext.HalfEdge1 = arc_at_site.HalfEdge1

                    # add p between i and i.pnext
                    arc_at_site.pnext.pprev = DifClasses.Arc(
                        site, arc_at_site, arc_at_site.pnext)
                    arc_at_site.pnext = arc_at_site.pnext.pprev

                    arc_at_site = arc_at_site.pnext

                    seg = DifClasses.HalfEdge(z)
                    self.HalfEdges.append(seg)
                    arc_at_site.pprev.HalfEdge1 = arc_at_site.HalfEdge0 = seg

                    seg = DifClasses.HalfEdge(z)
                    self.HalfEdges.append(seg)
                    arc_at_site.pnext.HalfEdge0 = arc_at_site.HalfEdge1 = seg

                    self.check_circle_event(arc_at_site, site.x)
                    self.check_circle_event(arc_at_site.pprev, site.x)
                    self.check_circle_event(arc_at_site.pnext, site.x)

                    return

                arc_at_site = arc_at_site.pnext

    def check_circle_event(self, arc, x0):
        if (arc.e is not None) and (arc.e.x != x0):
            arc.e.valid = False
        arc.e = None

        if (arc.pprev is None) or (arc.pnext is None):
            return

        flag, point_O, max_coord_x = self.circle(
            arc.pprev.site, arc.site, arc.pnext.site)
        if flag and (max_coord_x > x0):
            arc.e = DifClasses.CircleEvent(max_coord_x, point_O, arc)
            self.circle_events.push(arc.e)

    def circle(self, point_A, point_B, point_C):
        '''
        Parameter:
            each point in 3 points has structure: 2 property x, y
        Output:
            max coord of x of point in circle
            center of circle include 3 points point_A, point_B, point_C
        '''
        if ((point_B.x - point_A.x)*(point_C.y - point_A.y) - (point_C.x - point_A.x)*(point_B.y - point_A.y)) > 0:
            return False, None, None

        if (point_B.x-point_A.x)*(point_C.y - point_B.y) == (point_B.y-point_A.y)*(point_C.x - point_B.x):
            return False, None, None  # Points are co-linear

        # epression support to caculate center of circle and max coord x
        expr_1 = point_B.x - point_A.x
        expr_2 = point_B.y - point_A.y
        expr_3 = point_C.x - point_A.x
        expr_4 = point_C.y - point_A.y
        expr_5 = expr_1*(point_A.x + point_B.x) + \
            expr_2*(point_A.y + point_B.y)
        expr_6 = expr_3*(point_A.x + point_C.x) + \
            expr_4*(point_A.y + point_C.y)
        expr_7 = 2*(expr_1*(point_C.y - point_B.y) -
                    expr_2*(point_C.x - point_B.x))

        # point_O is the center of the circle
        point_O = DifClasses.Point(
            (expr_4*expr_5 - expr_2*expr_6) / expr_7, (expr_1*expr_6 - expr_3*expr_5) / expr_7)

        # max_cood_x = o.x + radius
        max_cood_x = point_O.x + math.sqrt((point_A.x-point_O.x)
                                           ** 2 + (point_A.y-point_O.y)**2)

        return True, point_O, max_cood_x

    def intersect(self, point, arc):
        # check whether a new parabola at point p intersect with arc
        if arc is None:
            return False, None
        if arc.site.x == point.x:
            return False, None

        a = 0.0
        b = 0.0

        if arc.pprev is not None:
            a = (self.intersection(arc.pprev.site, arc.site, point.x)).y
        if arc.pnext is not None:
            b = (self.intersection(arc.site, arc.pnext.site, point.x)).y

        if ((arc.pprev is None) or (a <= point.y)) and ((arc.pnext is None) or (point.y <= b)):
            py = point.y
            px = 1.0 * ((arc.site.x) ** 2 + (arc.site.y - py) **
                        2 - point.x ** 2) / (2 * arc.site.x - 2 * point.x)
            res = DifClasses.Point(px, py)
            return True, res
        return False, None

    def intersection(self, p0, p1, l):
        # get the intersection of two parabolas
        p = p0
        if p0.x == p1.x:
            py = (p0.y + p1.y) / 2.0
        elif p1.x == l:
            py = p1.y
        elif p0.x == l:
            py = p0.y
            p = p1
        else:
            z0 = 2.0 * (p0.x - l)
            z1 = 2.0 * (p1.x - l)

            a = 1.0/z0 - 1.0/z1
            b = -2.0 * (p0.y/z0 - p1.y/z1)
            c = 1.0 * (p0.y**2 + p0.x**2 - l**2) / z0 - \
                1.0 * (p1.y**2 + p1.x**2 - l**2) / z1

            py = 1.0 * (-b-math.sqrt(b*b - 4*a*c)) / (2*a)

        px = 1.0 * (p.x**2 + (p.y-py)**2 - l**2) / (2*p.x-2*l)
        res = DifClasses.Point(px, py)
        return res

    def finish_edges(self):
        l = self.sup_x + (self.sup_x - self.inf_x) + (self.sup_y - self.inf_y)
        i = self.arc
        while i.pnext is not None:
            if i.HalfEdge1 is not None:
                p = self.intersection(i.site, i.pnext.site, l*2.0)
                i.HalfEdge1.finish(p)
            i = i.pnext

    def get_output(self):
        res = []
        for o in self.HalfEdges:
            p0 = o.start
            p1 = o.end
            res.append((p0.x, p0.y, p1.x, p1.y))
        return res


def run(input_path, output_path="Output"):
    try:
        sites = DifProcesses.get_data_from_file(input_path)
        vor = Voronoi(sites)
        start = time.time()
        vor.process()
        end = time.time()
        lines = vor.get_output()

        if not os.path.exists(output_path):
            os.mkdir(output_path)

        print("Output is written to:", output_path)
        DifProcesses.save_to_txt_file(sites, vor, output_path)
        DifProcesses.save_to_png_file(sites, vor, lines, output_path)

        print('Running time: {0:.2f} s'.format(end - start))
    except:
        print("Has bug. Please check")
