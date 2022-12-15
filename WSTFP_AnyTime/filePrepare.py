from datetime import timedelta,datetime



def get_t_standard_cur(t_standard, t, TIMEGAP):#// TIMEGAP
    if t == t_standard:
        return t_standard
    elif t < t_standard:
        s = (t_standard - t).seconds
        d = (t_standard - t).days
        n = (d*24*60*60 + s) // TIMEGAP
        t_standard_cur = t_standard - timedelta(seconds=n * TIMEGAP)
    else:
        s2 = (t - t_standard).seconds
        d2 = (t - t_standard).days
        n2 = (d2*24*60*60 + s2) // TIMEGAP
        if (d2*24*60*60 + s2) % TIMEGAP == 0:
            t_standard_cur = t_standard+ timedelta(seconds=(n2) * TIMEGAP)
        else:
            t_standard_cur = t_standard + timedelta(seconds=(n2+1) * TIMEGAP)
    return t_standard_cur


def readFlowData(flow_data, TIMEGAP):
    ot_dict,dt_dict = dict(),dict()
    flow_list = []
    with open(flow_data, 'r') as fr:
        fr.readline()
        lst = fr.readline().strip().split(",")
        fid, oid, did, num = int(lst[0]), int(lst[2]), int(lst[4]), int(lst[5])
        ot_standard, dt_standard = datetime.strptime(lst[1], '%Y-%m-%d %H:%M:%S'), datetime.strptime(lst[3], '%Y-%m-%d %H:%M:%S')
        oid_dict, did_dict = {oid:{(fid, ot_standard,oid, num)}}, {did: {(fid, dt_standard, did, num)}}
        ot_dict[ot_standard], dt_dict[dt_standard] = oid_dict, did_dict
        flow_list.append((fid, ot_standard,oid,dt_standard,did,num))
        for line in fr:
            lst = line.strip().split(",")
            ot, dt = datetime.strptime(lst[1], '%Y-%m-%d %H:%M:%S'), datetime.strptime(lst[3], '%Y-%m-%d %H:%M:%S')
            fid, oid, did, num = int(lst[0]), int(lst[2]), int(lst[4]), int(lst[5])
            flow_list.append((fid,ot,oid,dt,did,num))
            ot_standard_cur = get_t_standard_cur(t_standard=ot_standard, t=ot, TIMEGAP=TIMEGAP)
            ot_standard_cur_dict = ot_dict.get(ot_standard_cur, dict())
            o_id_num_set = ot_standard_cur_dict.get(oid, set())
            o_id_num_set.add((fid,ot,oid, num))
            ot_standard_cur_dict[oid] = o_id_num_set
            ot_dict[ot_standard_cur] = ot_standard_cur_dict
            dt_standard_cur = get_t_standard_cur(dt_standard, dt, TIMEGAP)
            dt_standard_cur_dict = dt_dict.get(dt_standard_cur, dict())
            d_id_num_set = dt_standard_cur_dict.get(did, set())
            d_id_num_set.add((fid, dt,did, num))

            dt_standard_cur_dict[did] = d_id_num_set
            dt_dict[dt_standard_cur] = dt_standard_cur_dict

    return ot_standard, dt_standard, ot_dict, dt_dict, flow_list




def get_city_nei_dict(test_Neighbors_data):
    city_nei_dict = dict()
    with open(test_Neighbors_data, 'r') as fr:
        fr.readline()
        for line in fr:
            lst = line.strip().split(",")
            id1 = int(lst[0])
            neighbors = set()
            for i in lst[1:]:
                neighbors.add(int(i))
            city_nei_dict[id1] = neighbors
    return city_nei_dict

















