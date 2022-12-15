from WSTFP_AnyTime import filePrepare
from datetime import timedelta,datetime
import time
import numpy as np



# artifical_dataset - 9 flows
TIMEGAP = 60*60
MINNUM = 2
STENGTH = 0.0009
Neighbors_data = r"./dataSet/artifical_data_9/test_Neighbors_data.csv"
OD_data = r"./dataSet/artifical_data_9/test_OD_data.csv"



#artifical_dataset-5800 flows
# TIMEGAP = 10*60
# MINNUM = 20
# STENGTH = 0.0009
# Neighbors_data = r"./dataSet/artifical_data-5800/artifical_Neighbors_data.csv"
# OD_data = r"./dataSet/artifical_data-5800/artificial_OD_data.csv"


# real dataset
# TIMEGAP = 24*60*60
# MINNUM = 20
# STENGTH = 0.0009
# Neighbors_data = r"./dataSet/real-data/real_Neighbors_data.csv"
# OD_data = r"./dataSet/real-data/real_OD_data_1.csv"       #real_OD_data_1.csv contains one month data(217906 flows); real_OD_data.csv contains 12 months data(2640394 flows)



start_time = time.time()
ot_standard, dt_standard, ot_dict, dt_dict, flow_list = filePrepare.readFlowData(OD_data, TIMEGAP)
city_nei_dict = filePrepare.get_city_nei_dict(Neighbors_data)


def traverse_flows():
    visited_np = np.zeros(len(flow_list)+2)
    all_cluster = []
    for flow in flow_list:

        (fid, ot, oid, dt, did, num) = flow
        if visited_np[fid] == 1:
            continue
        visited_np[flow[0]] = 1
        one_cluster = cluster_flow(flow, visited_np)
        if len(one_cluster) > MINNUM:
            # print("Number of flows in the current cluster：", len(one_cluster))
            all_cluster.append(one_cluster)
    return all_cluster

#对当前flow进行扩展
def cluster_flow(flow, visited_np):
    one_cluster = list((flow,))
    candidate_nei_set = find_nei_flow(flow, city_nei_dict, ot_dict, dt_dict)
    candidate_nei_set.add(flow)
    all_cadidate_nei_set = candidate_nei_set.copy()
    while len(candidate_nei_set) > 0:
        item = candidate_nei_set.pop()
        if visited_np[item[0]] == 1:
            continue
        visited_np[item[0]] = 1         #
        nei_set = find_nei_flow(item,city_nei_dict, ot_dict, dt_dict)
        nei_set = nei_set - all_cadidate_nei_set
        candidate_nei_set.update(nei_set)
        all_cadidate_nei_set.update(nei_set)
        one_cluster.append(item)


    return one_cluster


def analysis_all_cluster(all_cluster):
    fw1 = open(r"./result/result_flow.csv", 'w')
    fw2 = open(r"./result/result_visual.csv", 'w')
    fw3 = open(r"./result/result_region.csv", 'w')
    fw1.write("cid,oid,did,o_start_time,o_end_time,d_start_time,d_end_time,o_during,d_during,v_value,s_value,c_value,o_set_len,d_set_len\n")
    fw2.write("cid,oset,dest,o_start_time,o_end_time,d_start_time,d_end_time,v_value,s_value,c_value\n")
    fw3.write("cid,region_type,region_id,regionNum,o_start_time,o_end_time,d_start_time,d_end_time,o_during,d_during,v_value,s_value,c_value,o_set_len,d_set_len\n")
    fw1.close()
    fw2.close()
    fw3.close()
    for cid,one_cluster in enumerate(all_cluster):
        v_value,a_value,c_value = analysis_one_cluster(one_cluster)
        wirte_to_file_flow(one_cluster,cid,v_value,a_value,c_value)
        wirte_to_file_region(one_cluster,cid,v_value,a_value,c_value)
        wirte_to_file_visual(one_cluster,cid,v_value,a_value,c_value)
        pass


def analysis_one_cluster(one_cluster):
    sum_flow = 0
    sum_o_out, sum_d_in = 0,0
    sum_ALL = 0
    o_set, d_set = set(),set()
    one_flow = one_cluster[0]
    o_start_time, o_end_time, d_start_time, d_end_time = one_flow[1],one_flow[1],one_flow[3],one_flow[3]

    for (fid, ot, oid, dt, did, num) in one_cluster:
        o_set.add(oid)
        d_set.add(did)
        if ot < o_start_time:
            o_start_time = ot
        if ot > o_end_time:
            o_end_time = ot
        if dt < d_start_time:
            d_start_time = dt
        if dt > d_end_time:
            d_end_time = dt
        sum_flow += num


    for o_id in o_set:
        sum_o_out += get_pid_all(o_id,o_start_time,o_end_time,"ot_dict")

    for d_id in d_set:
        sum_d_in += get_pid_all(d_id,d_start_time,d_end_time,"dt_dict")

    all_city = city_nei_dict.keys()
    for city in all_city:
        sum_ALL += get_pid_all(city,o_start_time,o_end_time,"ot_dict")
        sum_ALL += get_pid_all(city,d_start_time,d_end_time,"dt_dict")

    v_value = round(sum_flow/sum_ALL,5)
    a_value = round(sum_ALL * sum_flow / (sum_d_in*sum_o_out),5)
    c_value = round((v_value*a_value) ** 0.5,5)

    return v_value,a_value,c_value

def get_timeGap_for_oneCluster(one_cluster):
    one_flow = one_cluster[0]
    o_start_time, o_end_time, d_start_time, d_end_time = one_flow[1], one_flow[1], one_flow[3], one_flow[3]
    for (fid, ot, oid, dt, did, num) in one_cluster[1:]:
        if ot < o_start_time:
            o_start_time = ot
        if ot > o_end_time:
            o_end_time = ot
        if dt < d_start_time:
            d_start_time = dt
        if dt > d_end_time:
            d_end_time = dt
    return o_start_time,o_end_time,d_start_time,d_end_time


def wirte_to_file_flow(one_cluster,cid,v_value,a_value,c_value):
    o_start_time, o_end_time, d_start_time, d_end_time = get_timeGap_for_oneCluster(one_cluster)
    o_during = (o_end_time-o_start_time).seconds//60
    d_during = (d_end_time-d_start_time).seconds//60
    o_start_time_str = o_start_time.strftime("%Y-%m-%d %H:%M:%S")
    o_end_time_str = o_end_time.strftime("%Y-%m-%d %H:%M:%S")
    d_start_time_str = d_start_time.strftime("%Y-%m-%d %H:%M:%S")
    d_end_time_str = d_end_time.strftime("%Y-%m-%d %H:%M:%S")
    fw = open(r"./result/result_flow.csv",'a')
    o_set, d_set = set(), set()
    for (fid, ot, oid, dt, did, num) in one_cluster:
        o_set.add(oid)
        d_set.add(did)
    for (fid, ot, oid, dt, did, num) in one_cluster:
        fw.write(str(cid)+","+str(oid)+","+str(did)+","+o_start_time_str+","+ o_end_time_str+","+ d_start_time_str+","+ d_end_time_str+","+str(o_during)+","+str(d_during)+","
                 +str(v_value)+","+str(a_value)+","+str(c_value)+","+str(len(o_set))+","+str(len(d_set))+"\n")
    fw.flush()
    fw.close()

def wirte_to_file_region(one_cluster,cid,v_value,a_value,c_value):
    o_start_time, o_end_time, d_start_time, d_end_time = get_timeGap_for_oneCluster(one_cluster)
    o_during = (o_end_time-o_start_time).seconds//60
    d_during = (d_end_time-d_start_time).seconds//60
    o_start_time_str = o_start_time.strftime("%Y-%m-%d %H:%M:%S")
    o_end_time_str = o_end_time.strftime("%Y-%m-%d %H:%M:%S")
    d_start_time_str = d_start_time.strftime("%Y-%m-%d %H:%M:%S")
    d_end_time_str = d_end_time.strftime("%Y-%m-%d %H:%M:%S")
    fw = open(r"./result/result_region.csv",'a')
    o_set, d_set = set(), set()
    for (fid, ot, oid, dt, did, num) in one_cluster:
        o_set.add(oid)
        d_set.add(did)
    for oid in o_set:
        fw.write(str(cid) + ",type_O," + str(oid) + "," + str(len(o_set)) + "," +o_start_time_str+","+ o_end_time_str+","+ d_start_time_str+","+ d_end_time_str+","+str(o_during)+","+str(d_during)+","
                 + str(v_value) + "," + str(a_value) + "," + str(c_value)+","+str(len(o_set))+","+str(len(d_set)) + "\n")
    for did in d_set:
        fw.write(str(cid) + ",type_D," + str(did) + "," + str(len(d_set)) + "," +o_start_time_str+","+ o_end_time_str+","+ d_start_time_str+","+ d_end_time_str+","+str(o_during)+","+str(d_during)+","
                 + str(v_value) + "," + str(a_value) + "," + str(c_value)+","+str(len(o_set))+","+str(len(d_set)) + "\n")


    fw.flush()
    fw.close()

def wirte_to_file_visual(one_cluster,cid,v_value,a_value,c_value):
    o_start_time, o_end_time, d_start_time, d_end_time = get_timeGap_for_oneCluster(one_cluster)
    o_start_time_str = o_start_time.strftime("%Y-%m-%d %H:%M:%S")
    o_end_time_str = o_end_time.strftime("%Y-%m-%d %H:%M:%S")
    d_start_time_str = d_start_time.strftime("%Y-%m-%d %H:%M:%S")
    d_end_time_str = d_end_time.strftime("%Y-%m-%d %H:%M:%S")
    fw = open(r"./result/result_visual.csv",'a')
    o_set, d_set = set(), set()
    for (fid, ot, oid, dt, did, num) in one_cluster:
        o_set.add(oid)
        d_set.add(did)
    # print(str(cid)+","+str(o_set)+","+str(d_set)+","+o_start_time_str+","+ o_end_time_str+","+ d_start_time_str+","+ d_end_time_str+","+str(v_value)+","+str(a_value)+","+str(c_value))
    fw.write(str(cid)+","+str(o_set)+","+str(d_set)+","+o_start_time_str+","+ o_end_time_str+","+ d_start_time_str+","+ d_end_time_str+","+str(v_value)+","+str(a_value)+","+str(c_value)+"\n")
    fw.flush()
    fw.close()


def find_nei_flow(flow, city_nei_dict, ot_dict, dt_dict):
    (fid, ot, oid, dt, did, num) = flow
    ot_standard_cur = filePrepare.get_t_standard_cur(ot_standard, ot, TIMEGAP)
    ot_standard_pre = ot_standard_cur - timedelta(seconds=TIMEGAP)
    ot_standard_aft = ot_standard_cur + timedelta(seconds=TIMEGAP)

    dt_standard_cur = filePrepare.get_t_standard_cur(dt_standard, dt, TIMEGAP)
    dt_standard_pre = dt_standard_cur - timedelta(seconds=TIMEGAP)
    dt_standard_aft = dt_standard_cur + timedelta(seconds=TIMEGAP)
    o_nei_id_list, d_nei_id_list = city_nei_dict.get(oid, list()), city_nei_dict.get(did, list())
    if len(o_nei_id_list) ==0:
        print(str(oid),"has no neighbors")
        return set()
    if len(d_nei_id_list)==0:
        print(str(did),"has no neighbors")
        return set()

    candi_o_nei_flow,  candi_d_nei_flow= set(), set()
    for o_nei_id in o_nei_id_list:
        candi_o_nei_flow.update(ot_dict.get(ot_standard_cur,dict()).get(o_nei_id,set()))
        candi_o_nei_flow.update(ot_dict.get(ot_standard_pre,dict()).get(o_nei_id,set()))
        candi_o_nei_flow.update(ot_dict.get(ot_standard_aft,dict()).get(o_nei_id,set()))
    candi_o_nei_flow.update(ot_dict.get(ot_standard_pre, dict()).get(oid, set()))
    candi_o_nei_flow.update(ot_dict.get(ot_standard_aft, dict()).get(oid, set()))

    for d_nei_id in d_nei_id_list:
        candi_d_nei_flow.update(dt_dict.get(dt_standard_pre,dict()).get(d_nei_id, set()))
        candi_d_nei_flow.update(dt_dict.get(dt_standard_cur,dict()).get(d_nei_id, set()))
        candi_d_nei_flow.update(dt_dict.get(dt_standard_aft,dict()).get(d_nei_id, set()))
    candi_d_nei_flow.update(dt_dict.get(dt_standard_pre, dict()).get(did, set()))
    candi_d_nei_flow.update(dt_dict.get(dt_standard_aft, dict()).get(did, set()))

    all_o_nei_flow, all_d_nei_flow= set(), set()
    for o_nei in candi_o_nei_flow:
        (id, nei_o_time, oid, num) = o_nei
        if (ot>nei_o_time and (ot - nei_o_time).seconds < TIMEGAP) or (ot<nei_o_time and (nei_o_time-ot).seconds<TIMEGAP):
            all_o_nei_flow.add(o_nei)
    for d_nei in candi_d_nei_flow:
        (id, nei_d_time, did, num) = d_nei
        if (dt > nei_d_time and (dt-nei_d_time).seconds<TIMEGAP) or (dt<nei_d_time and (nei_d_time-dt).seconds<TIMEGAP):
            all_d_nei_flow.add(d_nei)
    all_nei_flow_set = set()
    for (id1, nei_o_time, oid, num1) in all_o_nei_flow:
        for (id2, nei_d_time, did, num2) in all_d_nei_flow:
            if id1 == id2:
                flow1 = (id1, nei_o_time, oid, nei_d_time, did, num1)
                if cal_strength(flow, flow1) >= STENGTH:
                    all_nei_flow_set.add((id1,nei_o_time,oid, nei_d_time, did, num1))
    return all_nei_flow_set




def cal_strength(flow1, flow2):
    (id1, ot1, oid1, dt1, did1, num1) = flow1
    (id2, ot2, oid2, dt2, did2, num2) = flow2
    if ot1 > ot2:
        ot_max, ot_min = ot1, ot2
    else:
        ot_max, ot_min = ot2, ot1
    if dt1 > dt2:
        dt_max, dt_min = dt1, dt2
    else:
        dt_max, dt_min = dt2, dt1

    o_sum, d_sum = 0, 0
    o_sum += get_t_pid_all(ot1, oid1, ot_min, ot_max,"ot_dict")
    o_sum += get_t_pid_all(ot2, oid2, ot_min, ot_max,"ot_dict")
    d_sum += get_t_pid_all(dt1, did1, dt_min, dt_max, "dt_dict")
    d_sum += get_t_pid_all(dt2, did2, dt_min, dt_max, "dt_dict")

    strength = (num1+num2)**2 / (o_sum*d_sum)
    return strength

def get_pid_all(pid,t_min,t_max,dict_falg):
    if dict_falg == "ot_dict":
        t_dict = ot_dict
        t_standard = ot_standard
    else:
        t_dict = dt_dict
        t_standard = dt_standard

    candi_nei_flow = set()
    t_min_cur = filePrepare.get_t_standard_cur(t_standard, t_min, TIMEGAP)
    t_min_pre = t_min_cur - timedelta(seconds=TIMEGAP)
    t_min_aft = t_min_cur + timedelta(seconds=TIMEGAP)

    t_max_cur = filePrepare.get_t_standard_cur(t_standard, t_max, TIMEGAP)
    t_max_pre = t_max_cur - timedelta(seconds=TIMEGAP)
    t_max_aft = t_max_cur + timedelta(seconds=TIMEGAP)

    candi_nei_flow.update(t_dict.get(t_min_pre, dict()).get(pid, set()))
    candi_nei_flow.update(t_dict.get(t_min_cur, dict()).get(pid, set()))
    candi_nei_flow.update(t_dict.get(t_min_aft, dict()).get(pid, set()))
    candi_nei_flow.update(t_dict.get(t_max_pre, dict()).get(pid, set()))
    candi_nei_flow.update(t_dict.get(t_max_cur, dict()).get(pid, set()))
    candi_nei_flow.update(t_dict.get(t_max_aft, dict()).get(pid, set()))

    # 当t_min_aft < t_max_pre时，需要遍历中间的时间层
    t_mid = t_min_aft
    while t_mid + timedelta(seconds=TIMEGAP) < t_max_pre:
        t_mid += timedelta(seconds=TIMEGAP)
        candi_nei_flow.update(t_dict.get(t_mid, dict()).get(pid,set()))
    sum = 0
    for (fid, time, pid, num) in candi_nei_flow:
        sum += num
    return sum


def get_t_pid_all(pt,pid,t_min,t_max,dict_falg):
    if dict_falg == "ot_dict":
        t_dict = ot_dict
        t_standard = ot_standard
    else:
        t_dict = dt_dict
        t_standard = dt_standard

    candi_nei_flow = set()
    t_min_cur = filePrepare.get_t_standard_cur(t_standard, t_min, TIMEGAP)
    t_min_pre = t_min_cur - timedelta(seconds=TIMEGAP)
    t_min_aft = t_min_cur + timedelta(seconds=TIMEGAP)

    t_max_cur = filePrepare.get_t_standard_cur(t_standard, t_max, TIMEGAP)
    t_max_pre = t_max_cur - timedelta(seconds=TIMEGAP)
    t_max_aft = t_max_cur + timedelta(seconds=TIMEGAP)

    candi_nei_flow.update(t_dict.get(t_min_pre, dict()).get(pid, set()))
    candi_nei_flow.update(t_dict.get(t_min_cur, dict()).get(pid, set()))
    candi_nei_flow.update(t_dict.get(t_min_aft, dict()).get(pid, set()))
    candi_nei_flow.update(t_dict.get(t_max_pre, dict()).get(pid, set()))
    candi_nei_flow.update(t_dict.get(t_max_cur, dict()).get(pid, set()))
    candi_nei_flow.update(t_dict.get(t_max_aft, dict()).get(pid, set()))

    t_mid = t_min_aft
    while t_mid + timedelta(seconds=TIMEGAP) < t_max_pre:
        t_mid += timedelta(seconds=TIMEGAP)
        candi_nei_flow.update(t_dict.get(t_mid, dict()).get(pid,set()))

    sum = 0
    for (fid, time, pid, num) in candi_nei_flow:
        if (time >= pt and (time-pt).seconds<=TIMEGAP) or (time<=pt and (pt-time).seconds<=TIMEGAP):
            sum += num
    return sum


if __name__ ==  "__main__":
    all_cluster = traverse_flows()
    analysis_all_cluster(all_cluster)
    dur_time = time.time()-start_time
    print("The program has been running for ：",dur_time,"s")

