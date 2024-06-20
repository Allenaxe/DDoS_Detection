import csv
import random
import heapq
import math
import copy
import time
# 初始化空列表
data = []

"""
dictionary = {"Benign" : 0,
              "UDP" : 1,
              "MSSQL" : 2,
              "Syn" : 3,
              "UDP-lag" : 4,
              "UDPLag" : 4,
              "TFTP" : 5,
              "DrDoS_NTP" : 6,
              "LDAP" : 7,
              "NetBIOS" : 8,
              "DrDoS_DNS" : 9,
              "WebDDoS" : 10,
              "DrDoS_SNMP" : 11,
              "Portmap" : 12,
              "DrDoS_MSSQL" : 13,
              "DrDoS_UDP" : 14,
              "DrDoS_LDAP" : 15,
              "DrDoS_NetBIOS" : 16}
"""
attack_type = 17

generation_size = 10
K = 20
dimension = 78
ga_max_dimension = 10

# 讀取 CSV 文件並將數據存儲到雙重列表中
with open('cicddos2019_dataset.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    flag = 0
    for row in reader:
        if flag == 1:
            data.append(row)
        else:
            flag = 1

# 初始化 a, b, c 列表
a = []
b = []
c = []

# 將每行的數據隨機分割並存儲到對應的列表中
length = len(data)
indices = list(range(length))
random.shuffle(indices)

split_point1 = length // 3
split_point2 = 2 * length // 3

# 使用隨機索引將數據分配到 a, b, c
a_indices = indices[:split_point1]
b_indices = indices[split_point1:split_point2]
c_indices = indices[split_point2:]
for i in a_indices:
    a.append(data[i])
for i in b_indices:
    b.append(data[i])
for i in c_indices:
    c.append(data[i])

# 打印結果（可選）
print("List a:", len(a))
print("List b:", len(b))
print("List c:", len(c))


def find_distance(a, b, ga):
    square = 0
    for i,j in ga:
        #print("i = ", i , "j = " , j)
        #print("a = ", a)
        if a[i] == '':
            a[i] = 0
        if b[i] == '':
            b[i] = 0
        square += (float(a[i]) - float(b[i])) * (float(a[i]) - float(b[i])) * j
    return math.sqrt(square)

def heuristic(ga) -> float:
    random_numbersB = random.sample(range(1, len(b)), 100)
    random_numbersA = random.sample(range(1, len(a)), 100)
    correct = 0
    for i in random_numbersB:
        cnt = []
        for j in range(attack_type):
            cnt.append(0)
        test = b[i]
        #print("test = ", test)
        #print("b = " , b[i])
        #print(test[-1], b[i][-1], float(b[i][-1]))
        pq = [] # default min-heap
        heapq.heapify(pq)
        for j in random_numbersA:
            heapq.heappush(pq, [-find_distance(test, a[j], ga), float(a[j][0]), int(a[j][-1])])
            if len(pq) > K:
                heapq.heappop(pq)
        for j in range(len(pq)):
            #print("k :", pq[j][0], pq[j][1])
            cnt[pq[j][2]] += 1
        max = -1
        max_index = -1
        for j in range(attack_type):
            if cnt[j] > max:
                max = cnt[j]
                max_index = j
        predict = max_index
        #print(predict, int(b[i][-1]))
        if predict == int(b[i][-1]):
            correct += 1
    correct_rate = correct / len(random_numbersB)
    #print("correct_rate = ", correct_rate, correct, len(random_numbersB))
    return correct_rate

pc = 0.9
pm1 = 0.1
pm2 = 0.1
gens = 20

def ga_implement(xx):
    generation = [] # default min-heap
    heapq.heapify(generation)
    for i in range(generation_size):
        random_numbers = random.sample(range(1, dimension+1), ga_max_dimension)
        tmp = [[j, random.uniform(0, 1)] for j in random_numbers]
        heu = heuristic(tmp)
        #print([heu, tmp])
        heapq.heappush(generation, [heu, tmp])
        #print("i = ", i)

    for gen in range(gens):

        all_childs = []
        for x in range(generation_size // 2):

            tounament_phase1 = []
            for i in random.sample(range(0, generation_size), 5):
                tounament_phase1.append(generation[i])
            parent = sorted(tounament_phase1, reverse=True)[:2]
            parent1_gene = parent[0][1]
            parent2_gene = parent[1][1]
            child1 = copy.deepcopy(parent1_gene)
            child2 = copy.deepcopy(parent2_gene)
            #print("child = ", child1)
            
            if random.uniform(0, 1) > pc:
                for i in range(random.randint(1, ga_max_dimension)):
                    child1[i] = parent2_gene[i]
                    child2[i] = parent1_gene[i]
            
            if random.uniform(0, 1) > pm1:
                child1[random.randint(0, ga_max_dimension-1)][0] = random.randint(1, dimension)

            if random.uniform(0, 1) > pm2:
                child1[random.randint(0, ga_max_dimension-1)][1] = random.uniform(0, 1)
            
            if random.uniform(0, 1) > pm1:
                child2[random.randint(0, ga_max_dimension-1)][0] = random.randint(1, dimension)

            if random.uniform(0, 1) > pm2:
                child2[random.randint(0, ga_max_dimension-1)][1] = random.uniform(0, 1)
            
            #print("parent1 :", parent[0][0])
            #print("parent2 :", parent[1][0])
            #print("child1 :", heuristic(child1))
            #print("child2 :", heuristic(child2))

            all_childs.append(child1)
            all_childs.append(child2)
            
        #print("len(all_childs) = ", len(all_childs))
        for child in all_childs:
            heapq.heappush(generation, [heuristic(child), child])

        while len(generation) > generation_size:
            heapq.heappop(generation)

        max_fitness_in_gen = -1
        for i in range(len(generation)):
            if generation[i][0] > max_fitness_in_gen:
                max_fitness_in_gen = generation[i][0]
        if type(xx) == int:
            xx = [xx].append(max_fitness_in_gen)
        else:
            xx.append(max_fitness_in_gen)
        #print(xx)
            
    max_index = -1
    max_heuristic = -1
    max = []
    for i in range(len(generation)):
        if generation[i][0] > max_heuristic:
            max_index = i
            max_heuristic = generation[i][0]
            max = generation[i][1]
    
    #print("final =" , " max fitness = ", max_heuristic)
    return max


def test_correctness(ga) -> float:
    random_numbersC = random.sample(range(1, len(c)), 1000)
    random_numbersA = random.sample(range(1, len(a)), 1000)
    correct = 0
    for i in random_numbersC:
        cnt = []
        for j in range(attack_type):
            cnt.append(0)
        test = c[i]
        #print("test = ", test)
        #print("b = " , b[i])
        #print(test[-1], b[i][-1], float(b[i][-1]))
        pq = [] # default min-heap
        heapq.heapify(pq)
        for j in random_numbersA:
            heapq.heappush(pq, [-find_distance(test, a[j], ga), float(a[j][0]), int(a[j][-1])])
            if len(pq) > K:
                heapq.heappop(pq)
        for j in range(len(pq)):
            #print("k :", pq[j][0], pq[j][1])
            cnt[pq[j][2]] += 1
        max = -1
        max_index = -1
        for j in range(attack_type):
            if cnt[j] > max:
                max = cnt[j]
                max_index = j
        predict = max_index
        #print(predict, int(b[i][-1]))
        if predict == int(test[-1]):
            correct += 1
    correct_rate = correct / len(random_numbersC)
    #print("test: correct_rate = ", correct_rate, correct, len(random_numbersC))
    return correct_rate

"""
with open('result.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["id", "ga", "ga_time", "KNN_10","KNN_10_time","KNN_all","KNN_all_time"])

    sum_ga_final = 0
    sum_test1 = 0
    sum_test2 = 0


    for t in range(1, 31):
        x = [t]

        ga_final = ga_implement()
        print("t :", t)
        start_time = time.perf_counter()
        tmp = test_correctness(ga_final)
        end_time = time.perf_counter()
        execution_time = (end_time - start_time) * 1000
        print("ga_final", tmp)
        sum_ga_final += tmp
        x.append(tmp)
        x.append(execution_time)

        test_1 =  [[j, 1] for j in random.sample(range(1, dimension+1), ga_max_dimension)]
        start_time = time.perf_counter()
        tmp = test_correctness(test_1)
        end_time = time.perf_counter()
        execution_time = (end_time - start_time) * 1000
        print("test_1", tmp)
        sum_test1 += tmp
        x.append(tmp)
        x.append(execution_time)
        

        test_2 =  [[j, 1] for j in range(1, dimension+1)]
        start_time = time.perf_counter()
        tmp = test_correctness(test_2)
        end_time = time.perf_counter()
        execution_time = (end_time - start_time) * 1000
        print("test_2", tmp)
        sum_test2 += tmp
        x.append(tmp)
        x.append(execution_time)
        
        writer.writerow(x)

    mean_ga_final = sum_ga_final / 30
    mean_test1 = sum_test1 / 30
    mean_test2 = sum_test2 / 30
    print("mean ga:", mean_ga_final)
    print("mean test1:", mean_test1)
    print("mean test2:", mean_test2)
"""

with open('result2.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["id", i in range(1,21)])

    sum_ga_final = 0
    sum_test1 = 0
    sum_test2 = 0


    for t in range(1, 31):
        xx = [t]
        print("t =", t)

        ga_final = ga_implement(xx)
        tmp = test_correctness(ga_final)

        writer.writerow(xx)
