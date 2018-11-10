from Module.Voronoi import Voronoi
import timeit
from Module import Support
import random as rd

if __name__ == "__main__":
    sites = Support.get_rand_input_sites(1000)
    Support.from_file(sites)
    vor = Voronoi(sites)
    print('Computing voronoi diagram for ' + str(len(sites)) + ' sites')
    strt = timeit.default_timer()
    vor.process()
    end = timeit.default_timer()
    print('Time: ', end - strt)
    lines = vor.get_output()
    Support.save_txt_file(sites, vor)
    Support.save_png_file(sites, vor, lines)
