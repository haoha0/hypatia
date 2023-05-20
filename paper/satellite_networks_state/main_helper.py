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

import sys
sys.path.append("../../satgenpy")
import satgen
import os


class MainHelper:
    def __init__(
            self,
            BASE_NAME,  # 名称
            NICE_NAME,
            ECCENTRICITY,   # 离心率
            ARG_OF_PERIGEE_DEGREE,  # 近地点角
            PHASE_DIFF, # 相位偏移
            MEAN_MOTION_REV_PER_DAY,    # 每天环绕地球的圈数
            ALTITUDE_M, # 高度
            MAX_GSL_LENGTH_M,   # 最大GSL长度
            MAX_ISL_LENGTH_M,   # 最大ISL长度
            NUM_ORBS,   # 轨道面数
            NUM_SATS_PER_ORB,   # 每面轨道卫星数
            INCLINATION_DEGREE, # 轨道倾角
    ):
        self.BASE_NAME = BASE_NAME
        self.NICE_NAME = NICE_NAME
        self.ECCENTRICITY = ECCENTRICITY
        self.ARG_OF_PERIGEE_DEGREE = ARG_OF_PERIGEE_DEGREE
        self.PHASE_DIFF = PHASE_DIFF
        self.MEAN_MOTION_REV_PER_DAY = MEAN_MOTION_REV_PER_DAY
        self.ALTITUDE_M = ALTITUDE_M
        self.MAX_GSL_LENGTH_M = MAX_GSL_LENGTH_M
        self.MAX_ISL_LENGTH_M = MAX_ISL_LENGTH_M
        self.NUM_ORBS = NUM_ORBS
        self.NUM_SATS_PER_ORB = NUM_SATS_PER_ORB
        self.INCLINATION_DEGREE = INCLINATION_DEGREE

    # 生成所需数据
    def calculate(
            self,
            output_generated_data_dir,
            duration_s,
            time_step_ms,
            isl_selection,            
            gs_selection,             
            dynamic_state_algorithm,  
            num_threads
    ):

        # Add base name to setting
        name = self.BASE_NAME + "_" + isl_selection + "_" + gs_selection + "_" + dynamic_state_algorithm

        # Create output directories
        if not os.path.isdir(output_generated_data_dir):
            os.makedirs(output_generated_data_dir, exist_ok=True)
        if not os.path.isdir(output_generated_data_dir + "/" + name):
            os.makedirs(output_generated_data_dir + "/" + name, exist_ok=True)

        # Ground stations
        # liu:
        # 这里的地面站是基于人口分布的top100城市，之后需要用师兄之前的那个地面站
        # def extend_ground_stations(filename_ground_stations_basic_in, filename_ground_stations_out):
        # 调用了函数geodetic2cartesian：大地坐标转换为笛卡尔坐标
        # 将不带位置格式的ground_stations转换为带位置格式的ground_stations
        print("Generating ground stations...")
        if gs_selection == "ground_stations_top_100":
            satgen.extend_ground_stations(
                "input_data/ground_stations_cities_sorted_by_estimated_2025_pop_top_100.basic.txt",
                output_generated_data_dir + "/" + name + "/ground_stations.txt"
            )
        elif gs_selection == "ground_stations_paris_moscow_grid":
            satgen.extend_ground_stations(
                "input_data/ground_stations_paris_moscow_grid.basic.txt",
                output_generated_data_dir + "/" + name + "/ground_stations.txt"
            )
        # liu: 新增starlink地面站
        elif gs_selection == "ground_stations_starlink":
            satgen.extend_ground_stations(
                "input_data/ground_stations_starlink.txt",
                output_generated_data_dir + "/" + name + "/ground_stations.txt"
            )
        else:
            raise ValueError("Unknown ground station selection: " + gs_selection)

        # TLEs
        # liu:
        # 调用函数generate_tles_from_scratch_manual()，位于satgen/tles/
        # 函数要用的参数都在MainHelper类中定义了
        # 这里filename_out="output_generated_data_dir + "/" + name + "/tles.txt"
        # gen_data/ self.BASE_NAME + "_" + isl_selection + "_" + gs_selection + "_" + dynamic_state_algorithm /tles.txt
        # 对于StarLink，用的是shell1，仅有1584颗卫星(72x22)
        print("Generating TLEs...")
        satgen.generate_tles_from_scratch_manual(
            output_generated_data_dir + "/" + name + "/tles.txt",
            self.NICE_NAME,
            self.NUM_ORBS,
            self.NUM_SATS_PER_ORB,
            self.PHASE_DIFF,
            self.INCLINATION_DEGREE,
            self.ECCENTRICITY,
            self.ARG_OF_PERIGEE_DEGREE,
            self.MEAN_MOTION_REV_PER_DAY
        )

        # ISLs
        # liu:
        # 如果isl_selection="isls_plus_grid"，表面有ISLs，如果isl_selection="isls_none"，表面没有ISLs
        # 有：调用函数generate_plus_grid_isls()，位于satgen/isls/
        # 无：调用函数generate_empty_isls()，位于satgen/isls/
        """
        def generate_plus_grid_isls(output_filename_isls, n_orbits, n_sats_per_orbit, isl_shift, idx_offset=0):
        Generate plus grid ISL file.

        :param output_filename_isls     Output filename
        :param n_orbits:                Number of orbits
        :param n_sats_per_orbit:        Number of satellites per orbit
        :param isl_shift:               ISL shift between orbits (e.g., if satellite id in orbit is X,
                                        does it also connect to the satellite at X in the adjacent orbit)
        :param idx_offset:              Index offset (e.g., if you have multiple shells)
        """
        print("Generating ISLs...")
        if isl_selection == "isls_plus_grid":
            satgen.generate_plus_grid_isls(
                output_generated_data_dir + "/" + name + "/isls.txt",
                self.NUM_ORBS,
                self.NUM_SATS_PER_ORB,
                isl_shift=0,
                idx_offset=0
            )
        elif isl_selection == "isls_none":
            satgen.generate_empty_isls(
                output_generated_data_dir + "/" + name + "/isls.txt"
            )
        else:
            raise ValueError("Unknown ISL selection: " + isl_selection)

        # Description
        # liu:
        # 调用函数generate_description()，位于satgen/description/
        print("Generating description...")
        satgen.generate_description(
            output_generated_data_dir + "/" + name + "/description.txt",
            self.MAX_GSL_LENGTH_M,
            self.MAX_ISL_LENGTH_M
        )

        # GSL interfaces
        # liu:
        # 调用函数read_ground_stations_extended()，位于satgen/ground_stations/
        # read_ground_stations.py:包含两个方法，一个是read_ground_stations_basic，一个是read_ground_stations_extended
        # 这里是从上面ground_stations部分生成的ground_stations.txt中读取地面站的信息
        # 进一步根据dynamic_state_algorithm的不同，确定不同的gsl_interfaces_per_satellite
        # 这里的GSL interfaces per satellite还不太懂：
        # 对应hypatia文档中提到的，卫星和地面站有几个接口，前两种算法是1，后面一种是有# of ground stations个接口
        # 具体可能还得看一下论文//TODO
        ground_stations = satgen.read_ground_stations_extended(
            output_generated_data_dir + "/" + name + "/ground_stations.txt"
        )
        if dynamic_state_algorithm == "algorithm_free_one_only_gs_relays" \
                or dynamic_state_algorithm == "algorithm_free_one_only_over_isls":
            gsl_interfaces_per_satellite = 1
        elif dynamic_state_algorithm == "algorithm_paired_many_only_over_isls":
            gsl_interfaces_per_satellite = len(ground_stations)
        else:
            raise ValueError("Unknown dynamic state algorithm: " + dynamic_state_algorithm)

        print("Generating GSL interfaces info..")
        # liu:
        # 调用函数generate_simple_gsl_interfaces_info()，位于satgen/interfaces/
        """
        def generate_simple_gsl_interfaces_info(filename_gsl_interfaces_info, number_of_satellites, number_of_ground_stations,
                                        num_gsl_interfaces_per_satellite, num_gsl_interfaces_per_ground_station,
                                        agg_max_bandwidth_satellite, agg_max_bandwidth_ground_station):
        Read for each node the GSL interface information.

        Note: the unit of the aggregate max bandwidth per satellite is not known, but they both must be the same unit.

        :param filename_gsl_interfaces_info: Filename of GSL interfaces info file to write to
                                            (typically /path/to/gsl_interfaces_info.txt)
                                            Line format: <node id>,<number of interfaces>,<aggregate max. bandwidth Mbit/s>
        :param number_of_satellites:                    Number of satellites
        :param number_of_ground_stations:               Number of ground stations
        :param num_gsl_interfaces_per_satellite:        Number of GSL interfaces per satellite
        :param num_gsl_interfaces_per_ground_station:   Number of (GSL) interfaces per ground station
        :param agg_max_bandwidth_satellite:             Aggregate bandwidth of all interfaces on a satellite
        :param agg_max_bandwidth_ground_station:        Aggregate bandwidth of all interfaces on a ground station

        """
        satgen.generate_simple_gsl_interfaces_info(
            output_generated_data_dir + "/" + name + "/gsl_interfaces_info.txt",
            self.NUM_ORBS * self.NUM_SATS_PER_ORB,
            len(ground_stations),
            gsl_interfaces_per_satellite,  # GSL interfaces per satellite
            1,  # (GSL) Interfaces per ground station
            1,  # Aggregate max. bandwidth satellite (unit unspecified)
            1   # Aggregate max. bandwidth ground station (same unspecified unit)
        )

        # Forwarding state
        # liu:
        # 调用函数help_dynamic_state()，位于satgen/dynamic_state/
        # 还不太懂，再说...
        print("Generating forwarding state...")
        import time
        start_time = time.time()
        satgen.help_dynamic_state(
            output_generated_data_dir,
            num_threads,  # Number of threads
            name,
            time_step_ms,
            duration_s,
            self.MAX_GSL_LENGTH_M,
            self.MAX_ISL_LENGTH_M,
            dynamic_state_algorithm,
            True
        )
        end_time = time.time()
        run_time = end_time - start_time
        print("Start Time: " + str(start_time))
        print("End Time: " + str(end_time))
        print("Run Time: " + str(run_time))
