import tkinter as tk
from math import sin, cos, radians, pi, atan, tan
from inspect import getsourcefile
from os.path import abspath
import json
import urllib.request
from pyproj import Proj, transform
from geomag.geomag import GeoMag
import UI_Code
from Google_API_Key import google_key

"""  pyprog Copyright (c) 2006 by Jeffrey Whitaker.
Permission to use, copy, modify, and distribute this software
and its documentation for any purpose and without fee is hereby
granted, provided that the above copyright notice appear in all
copies and that both the copyright notice and this permission
notice appear in supporting documentation. THE AUTHOR DISCLAIMS
ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING ALL
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT
SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, INDIRECT OR
CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE."""

# per http://spatialreference.org/ref/epsg/
# EPSG Projection List
wissouth_ft = Proj(init='epsg:3700')
    # NAD83(NSRS2007) / Wisconsin South (ftUS)
wisouth_m = Proj(init='epsg:3699')
    # NAD83(NSRS2007) / Wisconsin South
wgs84 = Proj(proj='latlong', datum='WGS84')
M2FT = 3.2808399
FT2M = (1.0 / M2FT)
sensor_w = 12.833  # DJI P4P
sensor_h = 8.8  # DJI P4P
focal_length = 8.6  # DJI P4P


def point_declination(lat, lon):
    mag = GeoMag().GeoMag(lat, lon)
    declination = mag.dec
    return float(declination)


def point_elevation(lat, lon):
    # API Key service: https://console.developers.google.com/apis/api/
    # elevation-backend.googleapis.com/
    apikey = google_key
    url = "https://maps.googleapis.com/maps/api/elevation/json"
    request = urllib.request.urlopen(
        url + "?locations=" + str(lat) + "," + str(lon) + "&key=" + apikey
    )
    results = json.load(request).get('results')
    elevation = results[0].get('elevation')
    return elevation * M2FT


def path_elevation(lat_p1, lon_p1, lat_p2, lon_p2, samples):
    # API Key service: https://console.developers.google.com/apis/api/
    # elevation-backend.googleapis.com/
    apikey = google_key
    url = "https://maps.googleapis.com/maps/api/elevation/json"
    request = urllib.request.urlopen(
        url + "?path=" + str(lat_p1) + "," + str(lon_p1) + "|" + str(lat_p2)
        + "," + str(lon_p2) + "&samples=" + str(samples) + "&key=" + apikey
    )
    results = json.load(request).get('results')
    elevationArray = []
    for resultset in results:
        elevationArray.append(float(resultset['elevation']))
    max_elevation = max(elevationArray)
    return max_elevation * M2FT


def point_pos(x, y, d, theta):
    theta_rad = pi / 2 - radians(theta)
    return x + d * cos(theta_rad), y + d * sin(theta_rad)


def get_plane_coordinates(lat, lon):
    x, y, z = transform(wgs84, wisouth_m, lon, lat, 0.0)
    return x * M2FT, y * M2FT


def get_geo_coordinates(x, y):
    lat, lon, depth = transform(wisouth_m, wgs84, x * FT2M, y * FT2M, 0.0)
    return lon, lat


def calculate_points(lat, lat_h, lon, lon_h, altitude, heading_input, length_p,
                     length_h, overlap, sample, direction, mode, output_file, contour,
                     north):
    fov_w = 2 * atan(sensor_w / (2 * focal_length))
    fov_h = 2 * atan(sensor_h / (2 * focal_length))
    range_w = 2 * altitude * tan(fov_w / 2)
    range_h = 2 * altitude * tan(fov_h / 2)
    half_dist_col = range_w * (1 - overlap / 100) / 2
    half_dist_row = range_h * (1 - overlap / 100) / 2
    # calculate heading
    declination = point_declination(lat, lon)
    if north == 1:
        heading = heading_input + declination
    else:
        heading = heading_input
    # Calculate columns, distance between columns and actual overlap
    columns_t = int(length_p / (2 * half_dist_col))
    half_dist_pt = length_p / (2 * columns_t)
    a_overlap_pt = 100 * (range_w - 2 * half_dist_pt) / range_w
    if a_overlap_pt < overlap * 0.9:
        columns = int(length_p / (2 * half_dist_pt)) + 1
        half_dist_p = length_p / (2 * columns)  # Half distance perp to heading
    else:
        columns = int(length_p / (2 * half_dist_pt))
        half_dist_p = length_p / (2 * columns)
    a_overlap_p = 100 * (range_w - 2 * half_dist_p) / range_w
    # Calculate rows, distance between row waypoints and actual overlap
    rows_t = int(length_h / (2 * half_dist_row))
    half_dist_ht = length_h / (2 * rows_t)
    a_overlap_ht = 100 * (range_h - 2 * half_dist_ht) / range_h
    if a_overlap_ht < overlap * 0.9:
        rows = int(length_h / (2 * half_dist_ht)) + 1
        half_dist_h = length_h / (2 * rows)
    else:
        rows = int(length_h / (2 * half_dist_ht))
        half_dist_h = length_h / (
            2 * rows)  # Half distance in direction of heading
    a_overlap_h = 100 * (range_h - 2 * half_dist_h) / range_h
    # Convert location of first corner and home to plane coordinates
    x0, y0 = get_plane_coordinates(lat, lon)
    xh, yh = get_plane_coordinates(lat_h, lon_h)
    # Calculate flight distance to first and last points and the route length
    col_offset = half_dist_p
    x1_out, y1_out = point_pos(x0, y0, col_offset, (heading + 90 * direction))
    row_offset = half_dist_h
    x2_out, y2_out = point_pos(x1_out, y1_out, row_offset, heading)

    col_offset = half_dist_p * (2 * columns - 1)
    x1_in, y1_in = point_pos(x0, y0, col_offset, (heading + 90 * direction))
    if columns % 2:  # Column is Odd
        row_offset = length_h - half_dist_h
    else:  # Column is Even
        row_offset = half_dist_h
    x2_in, y2_in = point_pos(x1_in, y1_in, row_offset, heading)

    distance_out = (abs(x2_out - xh) ** 2 + abs(y2_out - yh) ** 2) ** 0.5
    distance_in = (abs(x2_in - xh) ** 2 + abs(y2_in - yh) ** 2) ** 0.5
    route_length = (columns * (length_h - 2 * half_dist_h) + 2 * half_dist_p *
                    (columns - 1) + distance_out + distance_in)
    # Calculate corner locations of the defined area
    bx2, by2 = point_pos(x0, y0, length_h, heading)
    bx3, by3 = point_pos(bx2, by2, length_p, heading + 90 * direction)
    bx4, by4 = point_pos(bx3, by3, length_h, heading + 180 * direction)
    lat_b1, lon_b1 = get_geo_coordinates(x0, y0)
    lat_b2, lon_b2 = get_geo_coordinates(bx2, by2)
    lat_b3, lon_b3 = get_geo_coordinates(bx3, by3)
    lat_b4, lon_b4 = get_geo_coordinates(bx4, by4)

    return lat_h, lon_h, altitude, heading, columns, half_dist_p, \
           half_dist_h, direction, rows, x0, y0, mode, length_h, length_p, \
           a_overlap_h, a_overlap_p, output_file, lat, lon, contour, \
           lat_b1, lon_b1, lat_b2, lon_b2, lat_b3, lon_b3, lat_b4, lon_b4, \
           route_length, north, declination, sample


def write_file(calculated_points):
    lat_h = calculated_points[0]
    lon_h = calculated_points[1]
    altitude = calculated_points[2]
    heading = calculated_points[3]
    columns = calculated_points[4]
    half_dist_p = calculated_points[5]
    half_dist_h = calculated_points[6]
    direction = calculated_points[7]
    rows = calculated_points[8]
    x0 = calculated_points[9]
    y0 = calculated_points[10]
    mode = calculated_points[11]
    length_h = calculated_points[12]
    length_p = calculated_points[13]
    a_overlap_h = calculated_points[14]
    a_overlap_p = calculated_points[15]
    output_file = calculated_points[16]
    lat = calculated_points[17]
    lon = calculated_points[18]
    contour = calculated_points[19]
    lat_b1 = calculated_points[20]
    lon_b1 = calculated_points[21]
    lat_b2 = calculated_points[22]
    lon_b2 = calculated_points[23]
    lat_b3 = calculated_points[24]
    lon_b3 = calculated_points[25]
    lat_b4 = calculated_points[26]
    lon_b4 = calculated_points[27]
    route_length = calculated_points[28]
    north = calculated_points[29]
    declination = calculated_points[30]
    samples = calculated_points[31]
    profile_file = output_file + '.prf' + '.csv'
    p = open(profile_file, 'w')
    p.write("Count,Elevation,Flight El.,Max_elevation,Elevation_adj,Point_adj,Max_adj,Drone,Max_Elevation_back\n")
    count = 0
    # Write the file header
    f = open(output_file, 'w')
    f.write("latitude,longitude,altitude(ft),heading(deg),curvesize(ft),"
            "rotationdir,gimbalmode,gimbalpitchangle,actiontype1,actionparam1,"
            "actiontype2,actionparam2,actiontype3,actionparam3,actiontype4,"
            "actionparam4,actiontype5,actionparam5,actiontype6,actionparam6,"
            "actiontype7,actionparam7,actiontype8,actionparam8,actiontype9,"
            "actionparam9,actiontype10,actionparam10,actiontype11,"
            "actionparam11,actiontype12,actionparam12,actiontype13,"
            "actionparam13,actiontype14,actionparam14,actiontype15,"
            "actionparam15\n")
    # Write the Home Position
    elevation_home = point_elevation(lat_h, lon_h)
    #f.write(",".join([str(lat_h), str(lon_h), str(altitude), str(heading)]))
    #f.write(",0,0,2,-90,1,0,-1,0,-1,0,-1,0,-1,0,-1,0,-1,0,-1,0,-1,0,-1,0,"
    #        "-1,0,-1,0,-1,0,-1,0,-1,0\n")
    # Calculate waypoint positions
    lat1 = lat_h
    lon1 = lon_h
    max_elevation = 0
    max_elevation_back = 0
    point_adj = 0
    max_adj = 0
    for col in range(0, columns):
        col_offset = half_dist_p * (2 * col + 1)
        x1, y1 = point_pos(x0, y0, col_offset, (heading + 90 * direction))
        if mode > 0:  # Photo mode
            for row in range(0, rows):
                if col % 2:  # Column is Odd
                    row_offset = half_dist_h * ((rows - row) * 2 - 1)
                else:  # Column is Even
                    row_offset = half_dist_h * (2 * row + 1)
                x2, y2 = point_pos(x1, y1, row_offset, heading)
                lat2, lon2 = get_geo_coordinates(x2, y2)
                elevation = point_elevation(lat1, lon1)
                if contour == 1:
                    max_elevation = path_elevation(lat1, lon1, lat2, lon2,
                                                   samples)
                    point_adj = elevation - elevation_home
                    if max(max_elevation, max_elevation_back) > elevation:
                        max_adj = max(max_elevation, max_elevation_back) - elevation
                    else:
                        max_adj = 0
                    elevation_adj = point_adj + max_adj
                else:
                    elevation_adj = 0

                # write flight profile file
                count = count + 1
                p.write(",".join(
                    [str(count), str(elevation), str(elevation_home + altitude
                     + elevation_adj), str(max_elevation), str(elevation_adj),
                     str(point_adj), str(max_adj),
                     str(altitude + elevation_adj), str(max_elevation_back)])+"\n")

                # write the computed values
                f.write(",".join(
                    [str(lat1), str(lon1), str(altitude + elevation_adj),
                     str(heading)]))
                # write the hardcoded values - set gimbel pitch to interpolate
                #  and gimbel angle to straight down, add action to take photo
                f.write(",0,0,2,-90,1,0,-1,0,-1,0,-1,0,-1,0,-1,0,-1,0,-1,0,"
                        "-1,0,-1,0,-1,0,-1,0,-1,0,-1,0,-1,0\n")

                lat1 = lat2
                lon1 = lon2
                max_elevation_back = max_elevation

        else:  # Video mode
            for row in range(2):
                if col % 2:  # Column is Odd
                    row_offset = half_dist_h + (length_h - 2 * half_dist_h) * \
                    (1 - row)
                else:  # Column is Even
                    row_offset = half_dist_h + (length_h - 2 * half_dist_h) * row
                x2, y2 = point_pos(x1, y1, row_offset, heading)
                lat2, lon2 = get_geo_coordinates(x2, y2)
                if contour == 1:
                    elevation_adj = elevation - elevation_home
                else:
                    elevation_adj = 0

                # write the computed values
                f.write(",".join(
                    [str(lat2), str(lon2), str(altitude + elevation_adj),
                     str(heading)]))
                # write the hardcoded values - set gimbel pitch to interpolate
                #  and gimbel angle to straight down, add action to take photo
                f.write(",0,0,2,-90,1,0,-1,0,-1,0,-1,0,-1,0,-1,0,-1,0,-1,0,"
                        "-1,0,-1,0,-1,0,-1,0,-1,0,-1,0,-1,0\n")

    # write last point
    count = count + 1
    if contour == 1:
        elevation = point_elevation(lat1, lon1)
        max_elevation = path_elevation(lat1, lon1, lat_h, lon_h, samples)
        point_adj = elevation - elevation_home
        if max(max_elevation, max_elevation_back) > elevation:
            max_adj = max(max_elevation, max_elevation_back) - elevation
        else:
            max_adj = 0
        elevation_adj = point_adj + max_adj
    else:
        elevation_adj = 0

    p.write(",".join(
        [str(count), str(elevation), str(elevation_home + altitude
        + elevation_adj), str(max_elevation), str(elevation_adj),
         str(point_adj), str(max_adj), str(altitude + elevation_adj),
         str(max_elevation_back)]) + "\n")

    f.write(",".join(
        [str(lat1), str(lon1), str(altitude + elevation_adj), str(heading)]))
    f.write(",0,0,2,-90,1,0,-1,0,-1,0,-1,0,-1,0,-1,0,-1,0,-1,0,-1,0,-1,0,"
        "-1,0,-1,0,-1,0,-1,0,-1,0\n")

    # write the Home Position+
    p.write(",".join(
        [str(count), str(elevation_home), str(elevation_home + altitude
        + elevation_adj), str(max_elevation), str(elevation_adj),
         str(point_adj), str(max_adj), str(altitude + elevation_adj),
         str(max_elevation_back)]))
    f.write(",".join(
        [str(lat_h), str(lon_h), str(altitude + elevation_adj), str(heading)]))
    f.write(",0,0,2,-90,1,0,-1,0,-1,0,-1,0,-1,0,-1,0,-1,0,-1,0,-1,0,-1,0,"
            "-1,0,-1,0,-1,0,-1,0,-1,0\n")

    # write the corners of the defined area
    f.write(",".join([str(lat_b1), str(lon_b1), str(altitude), str(heading)]))
    f.write(",0,0,2,-90,1,0,-1,0,-1,0,-1,0,-1,0,-1,0,-1,0,-1,0,-1,0,-1,0,"
            "-1,0,-1,0,-1,0,-1,0,-1,0\n")
    f.write(",".join([str(lat_b2), str(lon_b2), str(altitude), str(heading)]))
    f.write(",0,0,2,-90,1,0,-1,0,-1,0,-1,0,-1,0,-1,0,-1,0,-1,0,-1,0,-1,0,"
            "-1,0,-1,0,-1,0,-1,0,-1,0\n")
    f.write(",".join([str(lat_b3), str(lon_b3), str(altitude), str(heading)]))
    f.write(",0,0,2,-90,1,0,-1,0,-1,0,-1,0,-1,0,-1,0,-1,0,-1,0,-1,0,-1,0,"
            "-1,0,-1,0,-1,0,-1,0,-1,0\n")
    f.write(",".join([str(lat_b4), str(lon_b4), str(altitude), str(heading)]))
    f.write(",0,0,2,-90,1,0,-1,0,-1,0,-1,0,-1,0,-1,0,-1,0,-1,0,-1,0,-1,0,"
            "-1,0,-1,0,-1,0,-1,0,-1,0\n")
    f.close()
    p.close()

    # Print inputs and outputs to a text file
    output_txt_file = output_file + '.txt'
    if direction == 1:
        direction_str = 'To Right'
    else:
        direction_str = 'To Left'
    if mode == 1:
        mode_str = 'Photo'
    else:
        mode_str = 'Video'
    if contour == 1:
        contour_str = 'Follow Contour'
    else:
        contour_str = 'Constant Altitude'
    if north == 1:
        north_str = 'True North'
    else:
        north_str = 'Magnetic North'

    f = open(output_txt_file, 'w')
    f.write(f'Output File: {output_file}\n')
    f.write(f'columns: {columns}\n')
    f.write(f'Rows: {rows}\n')
    f.write(f'Area Covered: {round(length_p * length_h / 43560, 1)} acres\n')
    f.write(f'Route Length: {round(route_length/5280,1)} miles\n')
    f.write(f'Actual Overlap in Columns: {round(a_overlap_p, 1)} %\n')
    f.write(f'Actual Overlap in Rows: {round(a_overlap_h, 1)} %\n')
    f.write(f'Altitude Above Home Point: {altitude} feet\n')
    f.write(f'Initial Heading: {heading} degrees\n')
    f.write(f'Length Perpendicular to Heading: {length_p} feet\n')
    f.write(f'Length in Direction of Heading: {length_h} feet\n')
    f.write(f'Column Direction: {direction_str} of Heading\n')
    f.write(f'Camera Mode: {mode_str}\n')
    f.write(f'Altitude Mode: {contour_str}\n')
    f.write(f'True or Magnetic North: {north_str}\n')
    f.write(f'Home Point:    {round(lat_h, 6)} {round(lon_h, 6)}\n')
    f.write(f'Start Corner:  {round(lat, 6)} {round(lon, 6)}\n')
    f.write(f'Second Corner: {round(lat_b2, 6)} {round(lon_b2, 6)}\n')
    f.write(f'Third Corner:  {round(lat_b3, 6)} {round(lon_b3, 6)}\n')
    f.write(f'Fourth Corner: {round(lat_b4,6)} {round(lon_b4,6)}\n')
    f.write('\n')
    f.write(str(abspath(getsourcefile(lambda: 0))))
    f.close()

    # Print inputs and outputs to the console
    print('File:', output_file)
    print('Columns:', columns, '  Rows:', rows)
    print('Area:', round(length_p * length_h / 43560, 1), 'acres')
    print('Route Length:', round(route_length / 5280, 1), 'miles')
    print('Actual Overlap in Columns:', round(a_overlap_p, 1), '%')
    print('Actual Overlap in Rows:', round(a_overlap_h, 1), '%')
    print('Home point:    ', round(lat_h, 6), round(lon_h, 6))
    print('Start corner:  ', round(lat, 6), round(lon, 6))
    print('Second corner: ', round(lat_b2, 6), round(lon_b2, 6))
    print('Third corner:  ', round(lat_b3, 6), round(lon_b3, 6))
    print('Fourth corner: ', round(lat_b4, 6), round(lon_b4, 6))
    print('Declination: ', round(declination, 4), 'degrees')


if __name__ == '__main__':
    root_window = tk.Tk()
    parameters_ui = UI_Code.GridInputUI(root_window)
    root_window.mainloop()
