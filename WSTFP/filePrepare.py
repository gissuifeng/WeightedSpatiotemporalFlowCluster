import numpy as np
np.set_printoptions(suppress=True)

max_cityId = 361
max_dateId = 364

def readFlowData(date_num_dict):
    flowMat = np.zeros((max_dateId+2, max_cityId+2, max_cityId+2))
    with open(r"./dataSet/flow_data.csv", 'r') as fr:
        fr.readline()
        for line in fr:
            lst = line.strip().split(",")
            dateNum = date_num_dict[lst[1]]
            id1, id2 = int(lst[2]), int(lst[4]);
            fnum = int(lst[5])
            flowMat[dateNum,id1,id2] = fnum;
    return flowMat


def get_date_dataNum_dict():
    date_num_dict = dict()
    num_data_dict = dict()
    with open(r"./dataSet/date_dateNum.csv", 'r') as fr:
        fr.readline()
        for line in fr:
            lst = line.strip().split(",")
            date_num_dict[lst[0]] = int(lst[1])
            num_data_dict[int(lst[1])] = lst[0]
    return date_num_dict, num_data_dict



def get_city_nei_dict():
    city_nei_dict = dict()
    with open(r"./dataSet/OD_Neighbor.csv", 'r') as fr:
        fr.readline()
        for line in fr:
            lst = line.strip().split(",")
            id1 = int(lst[0])
            neighbors = set()
            for i in lst[1:]:
                neighbors.add(int(i))
            city_nei_dict[id1] = neighbors
    return city_nei_dict


def cal_sum_in_out_city(flowMat):
    in_city = np.sum(flowMat,axis=1)
    city_out = np.sum(flowMat,axis=2)
    return in_city, city_out


if __name__ == "__main__":
    date_num_dict, num_data_dict = get_date_dataNum_dict()
    city_nei_dict = get_city_nei_dict()
    flowMat = readFlowData(date_num_dict)
    in_city, city_out = cal_sum_in_out_city()


















