# The MIT License (MIT)
#
# Copyright (c) 2020 ETH Zurich
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


def generate_plus_grid_isls(output_filename_isls, n_orbits, n_sats_per_orbit, isl_shift, idx_offset=0):
    """
    Generate plus grid ISL file.

    :param output_filename_isls     Output filename
    :param n_orbits:                Number of orbits
    :param n_sats_per_orbit:        Number of satellites per orbit
    :param isl_shift:               ISL shift between orbits (e.g., if satellite id in orbit is X,
                                    does it also connect to the satellite at X in the adjacent orbit)
    :param idx_offset:              Index offset (e.g., if you have multiple shells)
    """

    if n_orbits < 3 or n_sats_per_orbit < 3:
        raise ValueError("Number of x and y must each be at least 3")

    list_isls = []
    for i in range(n_orbits):
        for j in range(n_sats_per_orbit):
            # 对于最后一个轨道，0和1278距离太远，超出星间链路最大长度，同时不满足预期构型
            # 查看TLEs文件，与0号卫星最近的为1287，平近点角为347.5000，相位差为12.5°，正好为一个delta_f
            # 因此对于最后一个轨道增加一个isl_shift，使得0号卫星与1287号卫星相连
            if i == n_orbits - 1: # 最后一个轨道
                isl_shift = 9

            sat = i * n_sats_per_orbit + j  # 第i个轨道上第j颗卫星

            # 与相邻卫星建立链路
            sat_same_orbit = i * n_sats_per_orbit + ((j + 1) % n_sats_per_orbit)
            sat_adjacent_orbit = ((i + 1) % n_orbits) * n_sats_per_orbit + ((j + isl_shift) % n_sats_per_orbit)

            # 同轨链路
            list_isls.append((idx_offset + min(sat, sat_same_orbit), idx_offset + max(sat, sat_same_orbit)))

            # 异轨链路
            list_isls.append((idx_offset + min(sat, sat_adjacent_orbit), idx_offset + max(sat, sat_adjacent_orbit)))

    with open(output_filename_isls, 'w+') as f:
        for (a, b) in list_isls:
            f.write(str(a) + " " + str(b) + "\n")

    return list_isls
