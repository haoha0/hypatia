# Satgenpy analysis

Given that you have generated the satellite network state data over time in `satellite_networks_state`,
here you can there is an analysis of the constellations, for it both as a whole, as well as for a
few particular pairs.


## Getting started

1. Make sure you have all dependencies installed as prescribed in `<hypatia>/satgenpy/README.md`

2. Perform the full analysis (takes some time):
   ```
   python perform_full_analysis.py
   ```

3. The analysis for each constellation is now in `data/<satellite network name>`


##### liu note:
Satgenpy anapysis是用satellite_networks_state产生的数据，进行分析，生成的数据在data中，这个data本来是没有的，直接下载的数据解压后会有。(实际就是通过下面这个脚本产生的)
perform_full_analysis.py实现细节：
操作了好几条命令：
```
# eg. command1:
# Rio de Janeiro to St. Petersburg with only ISLs on Kuiper
commands_to_run.append("cd ../../satgenpy; python -m satgen.post_analysis.main_print_routes_and_rtt "
                       "../paper/satgenpy_analysis/data ../paper/satellite_networks_state/gen_data/"
                       "kuiper_630_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls "
                       "100 200 1174 1229 "
                       "> ../paper/satgenpy_analysis/data/command_logs/manual_kuiper_isls_1174_to_1229.log 2>&1")
'''
这里首先是进入到satgenpy文件夹，然后调用子文件夹satgen下面的一系列脚本
eg.
python -m satgen.post_analysis.main_print_routes_and_rtt
报错提示：
Must supply exactly six arguments
Usage: python -m satgen.post_analysis.main_print_routes_and_rtt.py 
[data_dir] [satellite_network_dir] [dynamic_state_update_interval_ms] [end_time_s] [src] [dst]

这条指令需要6个参数：
对应上面指令的：
../paper/satgenpy_analysis/data
../paper/satellite_networks_state/gen_data/kuiper_630_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls
100
200
1174
1229

最后有一个输出重定向：
> ../paper/satgenpy_analysis/data/command_logs/manual_kuiper_isls_1174_to_1229.log 2>&1
2>&1是将标准错误重定向到标准输出
linux输入输出重定向：
https://www.cnblogs.com/liuhaidon/p/12179028.html

这里有几个不同的py脚本，产生对应的结果存到log文件中：
# 1. Manual(为手动选择的端点对生成命令(随时间打印路由和RTT))
# 要看一下main_print_routes_and_rtt 和 main_print_graphical_routes_and_rtt的区别：TODO
脚本：main_print_routes_and_rtt 
对应输出：paper/satgenpy_analysis/data/command_logs/manual_{kuiper, starlink}_{isls, gs_relay}_xxxx_to_xxxx.log

脚本：main_print_graphical_routes_and_rtt
对应输出：paper/satgenpy_analysis/data/command_logs/manual_graphical_{kuiper, starlink}_{isls, gs_relay}_xxxx_to_xxxx.log

# 2. Constellation comparison(生成星座比较命令)
三层for循环，选定satgenpy_generated_constellation -> duration_s -> list_update_interval_ms
   从三个方面实验：Path, RTT, Time step path:
   脚本：main_analyze_path, main_analyze_rtt, main_analyze_time_step_path
   对应输出：
   paper/satgenpy_analysis/data/command_logs/constellation_comp_path_%s_%dms_for_%ds.log
   paper/satgenpy_analysis/data/command_logs/constellation_comp_rtt_%s_%dms_for_%ds.log
   paper/satgenpy_analysis/data/command_logs/constellation_comp_time_step_path_%s_%ds.log

'''
```
