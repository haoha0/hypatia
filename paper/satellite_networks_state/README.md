# Satellite networks' state

This directory shows how to generate the satellite network state. It makes use of the
`satgenpy` or `satgen` Python module, which is located at the root of Hypatia.

For each satellite network defined in here (Kuiper-630, Starlink-550, Telesat-1015),
it generates for a ranging set of scenarios the following static state:

* List of satellites which are encoded using TLEs (_tles.txt_)
* List of ISLs (_isls.txt_)
* List of ground stations (_ground_stations.txt_)
* Description of the maximum GSL and ISL length in meters (_description.txt_)
* Number of GSL interfaces each node (satellite and ground station) has, 
  and their total bandwidth sum (_gsl_interfaces_info.txt_)
  
... and the following dynamic state in discrete time steps:

* Forwarding state (`fstate_<time in ns>.txt`)
* GSL interface bandwidth (`gsl_if_bandwidth_<time in ns>.txt`)

This state is all essential for perform analyses and packet-level simulations.

Each Python file here adds that folder to its Python path. If you want your
editor to highlight things, you need to add `satgenpy` to your editor's 
Python path.

## Getting started

1. Make sure you have all dependencies installed as prescribed in 
   `<hypatia>/satgenpy/README.md`

2. Run from the main folder for the satellite networks used in the paper:
   ```
   bash generate_all_local.sh
   # Or if you have remote machines to distribute the workloads:
   # python generate_all_remote.py
   ```
   
3. ... which will generate:
   ```
   gen_data
   |-- 25x25_algorithm_free_one_only_over_isls
   |-- kuiper_630_isls_none_ground_stations_paris_moscow_grid_algorithm_free_one_only_gs_relays
   |-- kuiper_630_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls
   |-- starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls
   |-- telesat_1015_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls
   ```

#### liu note:
Step 1: satellite_networks_state 产生gen_data数据
bash generate_all_local.sh具体调用 generate_for_papaer.sh根据给定参数进一步调用main_xxx.py，其核心是main_helper.py中的MainHelper类。
MainHelper类：
属性：星座相关参数
方法：calculate() //通过此方法产生gen_data数据，用于后续的satgenpy_analysis

```
# 五种数据输入：
   # Ground stations
   # liu:
   # 这里的地面站是基于人口分布的top100城市，之后需要用师兄之前的那个地面站
   # def extend_ground_stations(filename_ground_stations_basic_in, filename_ground_stations_out):
   # 调用了函数geodetic2cartesian：大地坐标转换为笛卡尔坐标
   # 将不带位置格式的ground_stations转换为带位置格式的ground_stations
   
   # TLEs
   # liu:
   # 调用函数generate_tles_from_scratch_manual()，位于satgen/tles/
   # 函数要用的参数都在MainHelper类中定义了
   # 对于StarLink，用的是shell1，仅有1584颗卫星(72x22)

   # ISLs
   # liu:
   # 如果isl_selection="isls_plus_grid"，表面有ISLs，如果isl_selection="isls_none"，表面没有ISLs
   # 有：调用函数generate_plus_grid_isls()，位于satgen/isls/
   # 无：调用函数generate_empty_isls()，位于satgen/isls/
   
   # Description
   # liu:
   # 调用函数generate_description()，位于satgen/description/

   # GSL interfaces
   # liu:
   # 调用函数read_ground_stations_extended()，位于satgen/ground_stations/
   # read_ground_stations.py:包含两个方法，一个是read_ground_stations_basic，一个是read_ground_stations_extended
   # 这里是从上面ground_stations部分生成的ground_stations.txt中读取地面站的信息
   # 进一步根据dynamic_state_algorithm的不同，确定不同的gsl_interfaces_per_satellite
   # 这里的GSL interfaces per satellite：
   # 对应hypatia文档中提到的，卫星和地面站有几个接口，前两种算法是1，后面一种是有# of ground stations个接口
   # 具体可能还得看一下论文//TODO

   # Forwarding state
   # liu:
   # 调用函数help_dynamic_state()，位于satgen/dynamic_state/
   # 还不太懂，再说...TODO
```