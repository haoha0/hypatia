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

import exputil
import networkload
import random

local_shell = exputil.LocalShell()

# Clean-up for new a fresh run
local_shell.remove_force_recursive("runs")
local_shell.remove_force_recursive("pdf")
local_shell.remove_force_recursive("data")

for traffic_mode in ["specific", "general"]:
    for movement in ["static", "moving"]:

        # Prepare run directory
        # run_dir = "runs/run_" + traffic_mode + "_tm_pairing_kuiper_isls_" + movement
        run_dir = "runs/run_" + traffic_mode + "_tm_pairing_starlink_isls_" + movement
        local_shell.remove_force_recursive(run_dir)
        local_shell.make_full_dir(run_dir)

        # config_ns3.properties
        local_shell.copy_file("templates/template_config_ns3.properties", run_dir + "/config_ns3.properties")
        local_shell.sed_replace_in_file_plain(
            run_dir + "/config_ns3.properties",
            "[SATELLITE-NETWORK-FORCE-STATIC]",
            "true" if movement == "static" else "false"
        )

        # Make logs_ns3 already for console.txt mapping
        local_shell.make_full_dir(run_dir + "/logs_ns3")

        # .gitignore (legacy reasons)
        local_shell.write_file(run_dir + "/.gitignore", "logs_ns3")

        # Traffic selection
        if traffic_mode == "specific":

            # Create the initial random reciprocal pairing with already one pair known (1174, 1229)
            random.seed(123456789)
            random.randint(0, 100000000)  # Legacy reasons
            seed_from_to = random.randint(0, 100000000)
            # liu:
            # Rio de Janeiro (1174) to St. Petersburg (1229)
            # Itaboraí(133) to Kaunas(116) with only ISLs on Starlink
            # 1296 + 133 = 1429     1296 + 116 = 1412

            # a = set(range(1156, 1256))
            # a.remove(1174)
            # a.remove(1229)
            # initial_list_from_to = [(1174, 1229), (1229, 1174)]

            # liu:
            a = set(range(1296, 1460)) # 1296 + 165 = 1461
            a.remove(1429)
            a.remove(1412)
            initial_list_from_to = [(1429, 1412), (1412, 1429)]
            initial_list_from_to = initial_list_from_to + networkload.generate_from_to_reciprocated_random_pairing(
                list(a),
                seed_from_to
            )
            # liu: ValueError: Must have an even amount of servers

            # Find all source and destination satellites of 1174 and 1229 by going over all its paths
            satellite_conflicts_set = set()
            with open(
                "../../satgenpy_analysis/data/"
                # "kuiper_630_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls/100ms_for_200s/"
                # "manual/data/networkx_path_1174_to_1229.txt", "r"
                # liu:
                "starlink_550_isls_plus_grid_ground_stations_starlink_algorithm_free_one_only_over_isls/100ms_for_200s/"
                "manual/data/networkx_path_1429_to_1412.txt", "r"
            ) as f_in:

                # Every reachable path, add to the set the source and destination
                # satellite (index 1, and second to last)   # 路径中与地面站连接的两个卫星的下标分别是1和-2
                for line in f_in:
                    line = line.strip() # 返回字符串的副本，去掉前导和尾部的空白。
                    path_str = line.split(",")[1]
                    if path_str != "Unreachable":
                        path = path_str.split("-")
                        satellite_conflicts_set.add(int(path[1]))
                        satellite_conflicts_set.add(int(path[-2]))
            satellite_conflicts = list(satellite_conflicts_set)

            # Now we need to remove the pairs which are sharing at any
            # point the source / destination satellite of a path between 1174 and 1229
            # liu: 现在，我们需要删除在1174和1229之间的路径的任何一点上共享源/目标卫星的对
            conflicting_pairs = []
            # non_conflicting_pairs = [(1174, 1229), (1229, 1174)]
            # liu:
            non_conflicting_pairs = [(1429, 1412), (1412, 1429)]
            local_shell.make_full_dir("extra_satgenpy_analysis_data")
            for p in initial_list_from_to[2:]:  # Of course excluding the starting (1174, 1229) and (1229, 1174) pairs

                # Resulting path filename
                resulting_path_filename = (
                        "extra_satgenpy_analysis_data/"
                        # "kuiper_630_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls/"
                        # liu:
                        "starlink_550_isls_plus_grid_ground_stations_starlink_algorithm_free_one_only_over_isls/"
                        "100ms_for_200s/manual/data/networkx_path_" + str(p[0]) + "_to_" + str(p[1]) + ".txt"
                )

                # Generate the path file if it does not exist yet (expensive)
                if not local_shell.file_exists(resulting_path_filename):
                    local_shell.perfect_exec(
                        "cd ../../../satgenpy; python -m satgen.post_analysis.main_print_routes_and_rtt "
                        "../paper/ns3_experiments/traffic_matrix/extra_satgenpy_analysis_data "
                        "../paper/satellite_networks_state/gen_data/"
                        # "kuiper_630_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls "
                        # liu:
                        "starlink_550_isls_plus_grid_ground_stations_starlink_algorithm_free_one_only_over_isls "
                        "100 200 " + str(p[0]) + " " + str(p[1])
                    )

                # Open the path file
                with open(resulting_path_filename, "r") as f_in:

                    # If any of its paths have a source or destination satellite which is one of the conflicts,
                    # then it is a conflict and the pair is not added
                    conflict = False
                    for line in f_in:
                        path_str = line.split(",")[1]
                        if path_str != "Unreachable\n": # 我这里输出的要加一个\n但是不知道原来的代码为啥可以正常跑
                            try:
                                path = path_str.split("-")
                                if int(path[1]) in satellite_conflicts or int(path[-2]) in satellite_conflicts:
                                    conflict = True
                            except:
                                print("error in %s." % resulting_path_filename)
                                print("path: %s." % path_str)
                    if conflict:
                        conflicting_pairs.append(p)
                    else:
                        non_conflicting_pairs.append(p)

            #Final prints
            # print("Original pairs (%d):" % len(initial_list_from_to))
            # print(initial_list_from_to)
            # print("")
            # print("Conflicting pairs (%d/%d):" % (len(conflicting_pairs), len(initial_list_from_to)))
            # print(conflicting_pairs)
            # print("")
            # print("Final non-conflicting pairs (%d/%d):" % (len(non_conflicting_pairs), len(initial_list_from_to)))
            # print(non_conflicting_pairs)
            # print("")

            # Check it matches the legacy expectation
            if non_conflicting_pairs != [
                # (1174, 1229), (1229, 1174), (1214, 1166), (1166, 1214), (1205, 1251), (1251, 1205), (1165, 1213),
                # (1213, 1165), (1244, 1196), (1196, 1244), (1157, 1253), (1253, 1157), (1220, 1167), (1167, 1220),
                # (1212, 1197), (1197, 1212), (1178, 1217), (1217, 1178), (1250, 1199), (1199, 1250), (1202, 1163),
                # (1163, 1202), (1247, 1198), (1198, 1247), (1238, 1187), (1187, 1238), (1239, 1164), (1164, 1239),
                # (1241, 1181), (1181, 1241), (1248, 1184), (1184, 1248), (1173, 1221), (1221, 1173), (1195, 1254),
                # (1254, 1195), (1193, 1243), (1243, 1193), (1249, 1185), (1185, 1249), (1207, 1162), (1162, 1207),
                # (1226, 1209), (1209, 1226), (1227, 1176), (1176, 1227), (1210, 1245), (1245, 1210), (1188, 1200),
                # (1200, 1188), (1233, 1231), (1231, 1233), (1208, 1255), (1255, 1208), (1204, 1189), (1189, 1204),
                # (1201, 1228), (1228, 1201), (1206, 1186), (1186, 1206), (1169, 1237), (1237, 1169), (1222, 1194),
                # (1194, 1222), (1223, 1218), (1218, 1223), (1190, 1211), (1211, 1190), (1236, 1158), (1158, 1236),
                # (1182, 1203), (1203, 1182), (1172, 1235), (1235, 1172), (1242, 1224), (1224, 1242), (1191, 1216),
                # (1216, 1191), (1171, 1168), (1168, 1171), (1240, 1170), (1170, 1240), (1230, 1219), (1219, 1230),
                # (1192, 1160), (1160, 1192), (1161, 1232), (1232, 1161)
                (1429, 1412), (1412, 1429), (1413, 1410), (1410, 1413), (1316, 1391), (1391, 1316), (1315, 1406), 
                (1406, 1315), (1373, 1299), (1299, 1373), (1415, 1313), (1313, 1415), (1401, 1371), (1371, 1401),
                (1334, 1402), (1402, 1334), (1374, 1378), (1378, 1374), (1310, 1457), (1457, 1310), (1369, 1439), 
                (1439, 1369), (1351, 1440), (1440, 1351), (1309, 1296), (1296, 1309), (1337, 1448), (1448, 1337), 
                (1342, 1335), (1335, 1342), (1326, 1347), (1347, 1326), (1366, 1355), (1355, 1366), (1409, 1400), 
                (1400, 1409), (1331, 1361), (1361, 1331), (1307, 1388), (1388, 1307), (1365, 1430), (1430, 1365), 
                (1389, 1322), (1322, 1389), (1363, 1422), (1422, 1363), (1332, 1441), (1441, 1332), (1349, 1455), 
                (1455, 1349), (1394, 1390), (1390, 1394), (1442, 1437), (1437, 1442), (1359, 1418), (1418, 1359), 
                (1354, 1333), (1333, 1354), (1345, 1425), (1425, 1345), (1382, 1350), (1350, 1382), (1328, 1404), 
                (1404, 1328), (1428, 1312), (1312, 1428), (1395, 1357), (1357, 1395), (1424, 1408), (1408, 1424), 
                (1364, 1393), (1393, 1364), (1447, 1301), (1301, 1447), (1344, 1375), (1375, 1344), (1407, 1298), 
                (1298, 1407), (1330, 1454), (1454, 1330), (1392, 1423), (1423, 1392), (1367, 1340), (1340, 1367), 
                (1376, 1436), (1436, 1376), (1397, 1348), (1348, 1397), (1325, 1370), (1370, 1325), (1435, 1443), 
                (1443, 1435), (1352, 1304), (1304, 1352), (1308, 1398), (1398, 1308), (1368, 1329), (1329, 1368), 
                (1386, 1360), (1360, 1386), (1320, 1321), (1321, 1320), (1384, 1302), (1302, 1384), (1387, 1362), 
                (1362, 1387), (1297, 1427), (1427, 1297), (1456, 1414), (1414, 1456), (1420, 1346), (1346, 1420), 
                (1306, 1450), (1450, 1306), (1449, 1336), (1336, 1449), (1426, 1396), (1396, 1426), (1300, 1416), 
                (1416, 1300), (1419, 1319), (1319, 1419), (1303, 1338), (1338, 1303), (1459, 1311), (1311, 1459), 
                (1399, 1451), (1451, 1399), (1358, 1383), (1383, 1358), (1421, 1353), (1353, 1421), (1356, 1305), 
                (1305, 1356), (1372, 1381), (1381, 1372), (1341, 1318), (1318, 1341), (1327, 1343), (1343, 1327), 
                (1445, 1452), (1452, 1445), (1403, 1444), (1444, 1403), (1380, 1324), (1324, 1380), (1323, 1453), 
                (1453, 1323), (1458, 1314), (1314, 1458), (1379, 1339), (1339, 1379), (1417, 1317), (1317, 1417)    
            ]:
                raise ValueError("Final generated non-conflicting pairs is not what was expected")

            # Final from-to list
            list_from_to = non_conflicting_pairs

        elif traffic_mode == "general":

            # Create a random reciprocal pairing with already one pair known (1174, 1229)
            random.seed(123456789)
            random.randint(0, 100000000)  # Legacy reasons
            seed_from_to = random.randint(0, 100000000)
            # a = set(range(1156, 1256))
            # a.remove(1174)
            # a.remove(1229)
            # list_from_to = [(1174, 1229), (1229, 1174)]
            
            # liu::
            a = set(range(1296, 1460))
            a.remove(1429)
            a.remove(1412)
            list_from_to = [(1429, 1412), (1412, 1429)]
            list_from_to = list_from_to + networkload.generate_from_to_reciprocated_random_pairing(
                list(a),
                seed_from_to
            )

        else:
            raise ValueError("Unknown traffic mode: " + traffic_mode)

        # Write the schedule
        networkload.write_schedule(
            run_dir + "/schedule_starlink_550.csv",
            len(list_from_to),
            list_from_to,
            [1000000000000] * len(list_from_to),
            [0] * len(list_from_to)
        )

# Finished successfully
print("Success")
