from PIL import Image, ImageDraw, ImageFont
import random as rd


def get_rand_input_sites(num_sites):
    sites = []
    for __ in range(0, num_sites):
        a = rd.uniform(0, 1920)
        b = rd.uniform(0, 1920)
        if (a, b) not in sites:
            sites.append((a, b))
    return sites


def get_data_from_file(input_path, num_bonus_point=0):
    sites = get_rand_input_sites(num_bonus_point)
    with open(input_path) as f:
        lines = f.readlines()
        for line in lines[1:len(lines)]:
            coords = line.split(" ")
            if (float(coords[0])*1920, float(coords[1])*1920) not in sites:
                sites.append(
                    (float(coords[0])*1920, float(coords[1])*1920))
        print("Datas are got from:", input_path)
    return sites


def save_txt_file(sites, voronoi, output_path):
    with open(output_path + '/voronoi.diagram', 'w') as f:
        f.write(str(len(sites)) + '\n')
        f.write(str(len(sites)) + '\n')
        v_vertex_list = []
        cell_lines = []
        for site in voronoi.voronoi_vertex:
            s = str(len(voronoi.voronoi_vertex[site]))
            for vertex in voronoi.voronoi_vertex[site]:
                ver_as_tuple = (vertex.x, vertex.y)
                if ver_as_tuple not in v_vertex_list:
                    v_vertex_list.append(ver_as_tuple)
                s = s + ' ' + str(v_vertex_list.index(ver_as_tuple))
            cell_lines.append(s)
        f.write(str(len(v_vertex_list)) + '\n')
        for v in v_vertex_list:
            f.write(str(v[0]) + ' ' + str(v[1]) + '\n')
        for line in cell_lines:
            f.write(line + '\n')


def save_png_file(sites, voronoi, lines, output_path):
    image = Image.new('RGBA', (1920, 1920), color=(255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    for site in sites:
        draw.ellipse((site[0] - 10, site[1] - 10, site[0] +
                      10, site[1] + 10), fill='black')
    for line in lines:
        draw.line(line, fill='blue', width=10)
    for site in voronoi.voronoi_vertex:
        for v_vertex in voronoi.voronoi_vertex[site]:
            draw.ellipse((v_vertex.x - 10, v_vertex.y - 10,
                          v_vertex.x + 10, v_vertex.y + 10), fill='red')
    # PIL indexing of y is up to down, so we must flip it
    image = image.rotate(180)
    image.save(output_path + '/voronoi.png')
