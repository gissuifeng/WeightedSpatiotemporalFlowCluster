
from WSTFP import filePrepare
import numpy as np
import time

start_time = time.time()
max_cityId = 361        # Maximum number of city
max_dateId = 364        # Maximum number of date
STENGTH = 0.009
NUM = 20

date_num_dict, num_data_dict = filePrepare.get_date_dataNum_dict()
city_nei_dict = filePrepare.get_city_nei_dict()
flowMat = filePrepare.readFlowData(date_num_dict)
in_city, city_out = filePrepare.cal_sum_in_out_city(flowMat)


def cal_strength(flow1, flow2):
    (dn1, i1, j1), (dn2, i2,j2)= flow1, flow2
    num1, num2 = flowMat[dn1, i1, j1], flowMat[dn2, i2, j2]
    o1, o2 = city_out[dn1,i1], city_out[dn2,i2]
    d1, d2 = in_city[dn1,j1], in_city[dn2,j2]
    strength = (num1+num2)**2 / ((o1+o2)*(d1+d2))
    return strength



def find_nei_flow(flow):
    dn,i,j = flow
    nei_flow_set = set()
    o_nei_set, d_nei_set = city_nei_dict.get(i), city_nei_dict.get(j)
    if o_nei_set==None or d_nei_set==None:
        return nei_flow_set


    if flowMat[dn - 1, i, j] > 0:
        strength = cal_strength((dn, i, j), (dn - 1, i, j))
        if strength > STENGTH:
            nei_flow_set.add((dn - 1, i, j))
    if dn + 1 < max_dateId - 2 and flowMat[dn + 1, i, j] > 0:
        strength = cal_strength((dn, i, j), (dn + 1, i, j))
        if strength > STENGTH:
            nei_flow_set.add((dn + 1, i, j))

    for oid in o_nei_set:
        for did in d_nei_set:
            if dn-1 >= 0:
                if flowMat[dn-1,oid,did] > 0:
                    strength = cal_strength((dn, i, j), (dn-1, oid, did))
                    if strength > STENGTH:
                        nei_flow_set.add((dn-1, oid, did))
            if dn+1 < max_dateId :
                if flowMat[dn+1,oid,did] > 0:
                    strength = cal_strength((dn, i, j), (dn+1, oid, did))
                    if strength > STENGTH:
                        nei_flow_set.add((dn+1, oid, did))
            if flowMat[dn,oid,did] > 0:
                strength = cal_strength((dn,i, j), (dn,oid, did))
                if strength > STENGTH:
                    nei_flow_set.add((dn, oid, did))
    return nei_flow_set


def traverse_flows():
    visited_mat = np.zeros((max_dateId+1, max_cityId+1, max_cityId+1))
    all_cluster = []
    for dn in range(max_dateId+1):
    # for dn in range(3):
        for i in range(max_cityId+1):
            for j in range(max_cityId+1):
                if visited_mat[dn,i,j] == 1:
                    continue
                if flowMat[dn][i][j] == 0:
                    visited_mat[dn,i,j] = 1
                    continue
                visited_mat[dn,i,j] = 1
                one_cluster = cluster_flow([dn,i,j], visited_mat)
                if len(one_cluster) > NUM:
                    all_cluster.append(one_cluster)
    analysis_all_cluster(all_cluster)
    return all_cluster


def cluster_flow(flow, visited_mat):
    dn,i,j = flow
    one_cluster = [(dn,i,j)]
    cadidate_nei_set = find_nei_flow((dn,i,j))
    all_cadidate_nei_set = cadidate_nei_set.copy()
    while len(cadidate_nei_set) > 0:
        item = cadidate_nei_set.pop()
        if visited_mat[item] == 1:
            continue
        visited_mat[item] = 1
        nei_set = find_nei_flow(item)
        cadidate_nei_set.update(nei_set)
        all_cadidate_nei_set.update(nei_set)
        one_cluster.append(item)
    return one_cluster

#cid,oid,did,o_start_time,o_end_time,d_start_time,d_end_time,o_during,d_during,v_value,a_value,c_value,o_set_len,d_set_len
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
        v_value, s_value, c_value, dn_start, dn_end, i_during, o_set, d_set = analysis_one_cluster(one_cluster)
        if len(o_set)<2 or len(d_set)<2:
            continue
        wirte_to_file_flow(cid,v_value,s_value,c_value,dn_start,dn_end,i_during, o_set, d_set,one_cluster)
        wirte_to_file_region(cid,v_value,s_value,c_value,dn_start,dn_end,i_during, o_set, d_set)
        wirte_to_file_visual(cid,v_value,s_value,c_value,dn_start,dn_end,i_during, o_set, d_set)
        pass


def analysis_one_cluster(one_cluster):
    sum_flow = 0
    sum_o_out, sum_d_in = 0,0
    sum_ALL_day = 0
    dn_set, dn_i_set, dn_j_set = set(),set(),set()
    o_set, d_set = set(), set()

    for (dn,i,j) in one_cluster:
        dn_set.add(dn)
        dn_i_set.add((dn,i))
        dn_j_set.add((dn,j))
        o_set.add(i)
        d_set.add(j)
        sum_flow += flowMat[dn, i, j]

    i_start = min(list(dn_i_set))[0]
    i_end = max(list(dn_i_set))[0]
    j_start = min(list(dn_j_set))[0]
    j_end = max(list(dn_j_set))[0]
    i_during = i_end - i_start  + 1

    dn_start = num_data_dict.get(i_start)
    dn_end = num_data_dict.get(i_end)

    for dn,i in dn_i_set:
        sum_o_out += city_out[dn, i]

    for dn,j in dn_j_set:
        sum_d_in += in_city[dn, j]

    for dn in dn_set:
        sum_ALL_day += np.sum(flowMat[dn])
    v_value = round(sum_flow/sum_ALL_day,5)
    a_value = round(sum_ALL_day * sum_flow / (sum_d_in*sum_o_out),5)
    c_value = round((v_value*a_value) ** 0.5,5)
    return v_value,a_value,c_value,dn_start,dn_end,i_during,o_set,d_set


def wirte_to_file_flow(cid,v_value,s_value,c_value,dn_start,dn_end,i_during, o_set, d_set,one_cluster):
    fw = open(r"./result/result_flow.csv",'a')
    for (fid, oid, did) in one_cluster:
        fw.write(str(cid)+","+str(oid)+","+str(did)+","+str(dn_start) + "," + str(dn_end) + "," + str(dn_start) + "," + str(dn_end) + "," + str(i_during) + "," + str(i_during) +","
                 +str(v_value)+","+str(s_value)+","+str(c_value)+","+str(len(o_set))+","+str(len(d_set))+"\n")
    fw.flush()
    fw.close()



def wirte_to_file_region(cid,v_value,s_value,c_value,dn_start,dn_end,i_during, o_set, d_set):
    fw = open(r"./result/result_region.csv",'a')

    for oid in o_set:
        fw.write(str(cid) + ",type_O," + str(oid) + "," + str(len(o_set)) + "," + str(dn_start) + "," + str(dn_end) + "," + str(dn_start) + "," + str(dn_end) + "," + str(i_during) + "," + str(i_during) + ","
                 + str(v_value) + "," + str(s_value) + "," + str(c_value) + "," + str(len(o_set)) + "," + str(len(d_set)) + "\n")
    for did in d_set:
        fw.write(str(cid) + ",type_D," + str(did) + "," + str(len(d_set)) + "," + str(dn_start) + "," + str(dn_end) + "," + str(dn_start) + "," + str(dn_end) + "," + str(i_during) + "," + str(i_during) + ","
                 + str(v_value) + "," + str(s_value) + "," + str(c_value) + "," + str(len(o_set)) + "," + str(len(d_set)) + "\n")
    fw.flush()
    fw.close()



def wirte_to_file_visual(cid,v_value,s_value,c_value,dn_start,dn_end,i_during, o_set, d_set):
    fw = open(r"./result/result_visual.csv",'a')
    fw.write(str(cid)+","+str(o_set)+","+str(d_set)+","+str(dn_start)+","+ str(dn_end)+","+ str(dn_start)+","+ str(dn_end)+","+str(v_value)+","+str(s_value)+","+str(c_value)+"\n")
    fw.flush()
    fw.close()



















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

if __name__ == "__main__":
    traverse_flows()
    end_time = time.time()
    print("Running time of the program:",end_time-start_time)
