import pandas as pd
import numpy as np
import tool as t
import random
import heapq
import pickle
from Tasks import Task
from Devices import Device

Device_ = Device(3, 4, 4, 4)
Child_Pool = []
Child_fitness_Pool = []


def task_generation():
    csv_data = open('./data1_task67.csv', 'r')
    f_name = 'Facility1-To-'
    blocks = []
    current_block = []

    for line in csv_data:
        # 去除换行符
        line = line.strip()

        # 检查该行是否以 "MIYUN-To-" 开头
        if line.startswith('"' + f_name):
            # 如果当前块不为空，将其添加到块列表中
            if current_block:
                blocks.append(current_block)
                current_block = []

        # 将当前行添加到当前块
        current_block.append(line)

    # 将最后一个块添加到块列表中
    if current_block:
        blocks.append(current_block)

    tasks_Random_Tasks = {}
    t_id = 0
    for index, block in enumerate(blocks):
        s_name = ''
        for line in block:
            line.strip()
            if f_name in line:
                s_name = line.replace(f_name, '').replace(',,,,,', '')
            else:
                _, s_t, e_t, d_t, p, s_r = line.split(',')
                if p.startswith('"'):
                    priority = int(p.strip('"'))
                else:
                    priority = int(p)
                duration = int(float(d_t.strip('"')))
                start_time = int(float(s_t.strip('"')))
                end_time = int(float(e_t.strip('"')))
                if duration < 360:
                    continue
                if s_r.startswith('"'):
                    signal_rate = int(s_r.strip('"'))
                else:
                    signal_rate = int(s_r)
                if signal_rate >= 200:
                    input_freq = 1200
                else:
                    input_freq = 720
                if input_freq == 1200:
                    output_freq = 800
                else:
                    output_freq = 640
                task = Task(t_id, priority, start_time, end_time, s_name, signal_rate, input_freq,
                            output_freq)
                task.Device_Table(Device_)
                tasks_Random_Tasks[t_id] = task
                t_id += 1
    return tasks_Random_Tasks


def Population_Generation_tabu(tasks_list: dict, initial_number, mode_rate):
    Device_.clear_device()
    Fitness = []
    tasks_exert = []
    populations = [list(np.random.permutation(range(0, len(tasks_list)))) for _ in range(initial_number)]
    for population in populations:
        t.Clear_Tasks(tasks_list)
        Device_.clear_device()
        task_exert, fitness = Devices_assignment_random_tabu(population, tasks_list, Device_)
        tasks_exert.append(task_exert)
        Fitness.append(fitness)
    # 从生成的初始个体中，选取适应度最好的目标个数作为初代种群
    max_index = t.Find_Max_Index(Fitness, 50)
    initial_pops = [populations[i] for i in max_index]
    initial_pops_fitness = [Fitness[i] for i in max_index]
    initial_pops_task_exert = [tasks_exert[i] for i in max_index]
    return initial_pops, initial_pops_fitness, initial_pops_task_exert


def Devices_assignment_random_tabu(population, tasks_list, device_):
    def is_device_available(device, start_time_, end_time_):
        for period in device.usingPeriod:
            if not (end_time_ < period[1][0] or period[1][1] < start_time_):
                return False
        return True

    def is_Tr_available(device, start_time_, end_time_, now_rate, channel_count):
        for task_id, period in device.usingPeriod:
            if not (end_time_ < period[0] or period[1] < start_time_):
                now_rate += tasks_list[task_id].signal_rate
                if channel_count == 4 and now_rate > device.rateSumMax:
                    return False
                channel_count += 1
        return True

    def assign_device_random(devices_list, device_type, start_time_, end_time_):
        target = random.choice(devices_list)
        device = device_.get_device_by_index(target, device_type)
        if is_device_available(device, start_time_, end_time_):
            return target
        else:
            return None

    def assign_device_balance(devices_list, device_type, start_time_, end_time_):
        available_devices = {}
        now_rate = 0
        channel_count = 0
        for device_index in devices_list:
            device = device_.get_device_by_index(device_index, device_type)
            if device_type == 'Tr':
                if is_Tr_available(device, start_time_, end_time_, now_rate, channel_count):
                    available_devices[device_index] = len(device.usingPeriod)
            else:
                if is_device_available(device, start_time_, end_time_):
                    available_devices[device_index] = len(device.usingPeriod)
        if not available_devices:
            return None
        return min(zip(available_devices.values(), available_devices.keys()))[1]

    tasks_exert = []
    for task_index in population:
        task = tasks_list[task_index]
        start_time, end_time = task.start_time, task.end_time
        if np.random.rand() < 0.8:
            Ta = assign_device_balance(task.Ta_table, 'Ta', task.start_time, task.end_time)
        else:
            Ta = assign_device_random(task.Ta_table, 'Ta', task.start_time, task.end_time)
        if Ta is None:
            task.Ta = -1
            task.Td = -1
            task.Tm = -1
            task.Tr = -1
            task.isExert = False
            tasks_exert.append(None)
            continue
        if task.freq_input == 1200:
            Td = assign_device_balance(task.Td_1200_table, 'Td', start_time, end_time)
        else:
            Td = assign_device_balance(task.Td_720_table, 'Td', start_time, end_time)
            if Td is None and task.signal_rate <= 200:
                Td = assign_device_balance(task.Td_1200_table, 'Td', start_time, end_time)

        if Td is None:
            task.Ta = -1
            task.Td = -1
            task.Tm = -1
            task.Tr = -1
            task.isExert = False
            tasks_exert.append(None)
            continue

        if task.freq_output == 640:
            Tm = assign_device_balance(task.Tm_640_table, 'Tm', start_time, end_time)
            if Tm is None and device_.Nsp_now < device_.Nsp:
                Tm = assign_device_random(task.Tm_800_table, 'Tm', start_time, end_time)
                device_.Nsp_now += 1
        else:
            Tm = assign_device_balance(task.Tm_800_table, 'Tm', start_time, end_time)
        if Tm is None:
            task.Ta = -1
            task.Td = -1
            task.Tm = -1
            task.Tr = -1
            task.isExert = False
            if not device_.Nsp_now == device_.Nsp:
                tasks_exert.append(None)
            else:
                tasks_exert.append(-1)
            continue

        Tr = assign_device_balance(task.Tr_table, 'Tr', start_time, end_time)
        if Tr is None:
            task.Ta = -1
            task.Td = -1
            task.Tm = -1
            task.Tr = -1
            task.isExert = False
            tasks_exert.append(None)
            continue

        task.Ta = Ta
        task.Td = Td
        task.Tm = Tm
        task.Tr = Tr
        task.isExert = True

        device_.antenna[Ta].usingPeriod.append((task.id, [task.start_time, task.end_time]))
        device_.frequencyConverter[Td].usingPeriod.append((task.id, [task.start_time, task.end_time]))
        device_.demodulator[Tm].usingPeriod.append((task.id, [task.start_time, task.end_time]))
        device_.recorder[Tr].usingPeriod.append((task.id, [task.start_time, task.end_time]))
        tasks_exert.append([Ta, Td, Tm, Tr])
    res = (tasks_exert, Fitness_pop(population, tasks_list))
    return res


def Fitness_pop(tasks_index, tasks_list):
    fitness = 0
    for i in tasks_index:
        fitness += tasks_list[i].priority * int(tasks_list[i].isExert) * (
                tasks_list[i].end_time - tasks_list[i].start_time)
    return fitness


def Tabu_and_GA_main(tasks_list, tasks_exerts, first_pops, pop_size, fits, tournament_size,
                     c_rate, m_early_rate, m_lately_rate, tabu_list, sums, generation, generations):
    pop_1 = Tournament_Select_tabu(first_pops, pop_size, fits, tournament_size[1])
    pop_2 = Tournament_Select_tabu(first_pops, pop_size, fits, tournament_size[1])
    child_pops = CrossOver_tabu(pop_size, c_rate, pop_1, pop_2, tabu_list, first_pops)
    child_pops, child_fits, child_task_exert = Mutate_tabu(child_pops, m_early_rate, tabu_list, first_pops, tasks_list,
                                                           Device_)

    # 一对一生存竞争
    for i in range(pop_size):
        if fits[i] < child_fits[i]:
            fits[i] = child_fits[i]
            first_pops[i] = child_pops[i]
            tasks_exerts[i] = child_task_exert[i]

    return first_pops, fits, tasks_exerts


def Tournament_Select_tabu(pops, pop_size, fits, tournament_size):
    new_pops = []
    while len(new_pops) < len(pops):
        tournament_list = random.sample(range(0, pop_size), tournament_size)
        tournament_fit = [fits[i] for i in tournament_list]
        # 转化为df方便索引
        tournament_df = pd.DataFrame([tournament_list, tournament_fit]).transpose().sort_values(by=1,
                                                                                                ascending=False).reset_index(
            drop=True)

        # 选出获胜者
        pop = pops[int(tournament_df.iloc[0, 0])]
        new_pops.append(pop)
    return new_pops


def CrossOver_tabu(pop_size, pc, selected_pops_1, selected_pops_2, tabu_list, last_pops):
    def select_segments(lst):
        segment_length = int(len(lst) * 0.1)
        start_pos_ = random.randint(0, len(lst) - segment_length)
        segment = lst[start_pos_:start_pos_ + segment_length]
        return start_pos_, start_pos_ + segment_length, segment

    def generate_mapping(A, B):
        while True:
            start_pos_A, end_pos_A, segment_A = select_segments(A)
            start_pos_B, end_pos_B, segment_B = select_segments(B)
            if len(set(segment_A).intersection(segment_B)) == 0:
                break
        mapping_ = dict(zip(segment_A, segment_B))
        mapping_.update(dict(zip(segment_B, segment_A)))
        return start_pos_A, end_pos_A, start_pos_B, end_pos_B, mapping_

    def replace_elements(parent1, parent2, start_1_replace, end_1_replace,
                         start_2_replace, end_2_replace, mapping_):
        return [mapping_.get(x, x) for x in parent1[:start_1_replace]] + \
               parent2[start_2_replace:end_2_replace] + \
               [mapping_.get(x, x) for x in parent1[end_1_replace:]], \
               [mapping_.get(x, x) for x in parent2[:start_2_replace]] + \
               parent1[start_1_replace:end_1_replace] + \
               [mapping_.get(x, x) for x in parent2[end_2_replace:]]

    child_pops = []
    for _ in range(int(pop_size / 2)):
        flag = True
        while flag:
            i = random.randint(0, pop_size - 1)
            parent_1 = selected_pops_1[i]
            parent_2, isDifferent = t.find_different_parent(parent_1, selected_pops_2)
            if isDifferent and np.random.rand() < pc:
                start_1_pos, end_1_pos, start_2_pos, end_2_pos, mapping = generate_mapping(parent_1, parent_2)
                child_1, child_2 = replace_elements(parent_1, parent_2, start_1_pos, end_1_pos,
                                                    start_2_pos, end_2_pos, mapping)
            else:
                child_1 = selected_pops_1[i][:]
                child_2 = selected_pops_2[i][:]
            if ((child_1 not in tabu_list) and (child_2 not in tabu_list)) & (
                    (child_1 not in child_pops) and (child_2 not in child_pops)) & (
                    (child_1 not in last_pops) and (child_2 not in last_pops)):
                child_pops.append(child_1)
                child_pops.append(child_2)
                flag = False
    return child_pops


def Mutate_tabu(pops, pm, tabu_list, last_pops, tasks_list, device_):
    pops_mutate = []
    pop_size = len(pops)
    Tasks_exert = []
    Fitness = []

    for index in range(pop_size):
        task_exert = []
        fitness = 0
        flag = True
        while flag:
            pop = pops[index][:]
            if np.random.rand() < pm:
                i, j = random.sample(range(len(pop)), 2)
                pop[i], pop[j] = pop[j], pop[i]
                task_exert, fitness = device_distribution_tabu(pop, tasks_list, device_)
                territory = pop[:]
                i, j = random.sample(range(len(territory)), 2)
                territory[i], territory[j] = territory[j], territory[i]
                task_exert_t, fitness_t = device_distribution_tabu(territory, tasks_list, device_)
                if fitness < fitness_t:
                    pop = territory
                    task_exert = task_exert_t
                    fitness = fitness_t

            if (pop not in tabu_list) & (pop not in pops_mutate) & (pop not in pops) & (
                    pop not in last_pops):  # 全局禁忌、当前禁忌、交叉后种群禁忌，上一代种群禁忌
                pops_mutate.append(pop)
                Tasks_exert.append(task_exert)
                Fitness.append(fitness)
                flag = False

    return pops_mutate, Fitness, Tasks_exert


def device_distribution_tabu(pops, tasks_list, device_):
    task_exert, fitness = Devices_assignment_random_tabu(pops, tasks_list, Device_)
    device_.clear_device()
    t.Clear_Tasks(tasks_list)
    return task_exert, fitness
