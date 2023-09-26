import heapq
import random
import pandas as pd
import csv
import genetic_main as gm

import matplotlib.pyplot as plt
from pylab import mpl

mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False


def check_sequential_overlap(list1, list2, threshold_percent=70):
    assert len(list1) == len(list2), "Lists must have the same length"

    length = len(list1)
    matches = 0

    for i in range(length):
        if list1[i] == list2[i]:
            matches += 1

    return (matches / length) * 100 > threshold_percent


def Find_Max_Index(data, n):
    # 获取最大值及其索引
    max_indices = heapq.nlargest(int(n), enumerate(data), key=lambda x: x[1])
    max_index = [index for index, _ in max_indices]
    random.shuffle(max_index)
    # 仅返回索引列表
    return max_index


def Clear_Tasks(tasks_clear):
    for index in tasks_clear:
        tasks_clear[index].task_clear()


def Drawing(generations, results):
    X = []
    Y = []
    for generation in range(generations):
        X.append(generation)
        Y.append(results[generation])
    plt.plot(X, Y)
    plt.show()


def find_different_parent(parent, candidates, threshold_percent=70):
    for candidate in candidates:
        if not check_sequential_overlap(parent, candidate, threshold_percent):
            return candidate, True
    # 如果所有候选项都过于相似，返回原始列表中的第一个元素
    return candidates[0], False


def find_duplicates(lst):
    duplicates = set()
    seen = set()

    for item in lst:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)

    return duplicates


def sortedDictValues2(adict):
    sorted_dict = {key: adict[key] for key in sorted(adict)}
    return sorted_dict


def gantt_figure_drawing(tasks_list, task_exerts, plan):
    datas = []
    for task_index in range(len(plan)):
        task = tasks_list[plan[task_index]]
        if task_exerts[task_index] is not None and task_exerts[task_index] != -1:
            status = 'running'
        elif task_exerts[task_index] == -1:
            status = 'stop'
        else:
            status = 'stop'
        data = {'Task': task.satellite, 'Start': task.window_start_time,
                'End': task.window_end_time, 'Status': status}
        datas.append(data)

    unique_task_names = sorted(set(task['Task'] for task in datas))
    fig, ax = plt.subplots()

    status_colors = {
        'running': 'green',
        'stop': 'red'
    }

    for task in datas:
        task_name_index = unique_task_names.index(task['Task'])
        color = status_colors[task['Status']]

        # 计算已完成任务的持续时间
        duration = (task['End'] - task['Start'])

        # 对于具有相同任务名的任务，将其堆叠在一起
        ax.barh(task_name_index, duration, left=task['Start'], height=0.3, color=color)

    ax.set_yticks(range(len(unique_task_names)))
    ax.set_yticklabels(unique_task_names)

    ax.set_xlim(0, 86400)

    plt.xticks()
    plt.xlabel('Time')
    plt.ylabel('Tasks')

    # 添加图例
    legend_handles = [plt.Rectangle((0, 0), 1, 1, color=color) for color in status_colors.values()]
    plt.legend(legend_handles, status_colors.keys())

    plt.show()


def gantt_figure_drawing_deviceUsing(tasks_list, task_exerts, plan):
    datas = []
    for task_index in range(len(plan)):
        if task_exerts[task_index] is None or task_exerts[task_index] == -1:
            continue
        task = tasks_list[plan[task_index]]
        data = {'Task': 'Antenna' + str(task_exerts[task_index][0]), 'Start': task.window_start_time,
                'End': task.window_end_time}
        datas.append(data)

    unique_task_names = sorted(set(task['Task'] for task in datas))
    fig, ax = plt.subplots()

    for task in datas:
        task_name_index = unique_task_names.index(task['Task'])

        # 计算已完成任务的持续时间
        duration = (task['End'] - task['Start'])

        # 对于具有相同任务名的任务，将其堆叠在一起
        ax.barh(task_name_index, duration, left=task['Start'], height=0.3, color='black')

    ax.set_yticks(range(len(unique_task_names)))
    ax.set_yticklabels(unique_task_names)

    ax.set_xlim(0, 86400)

    plt.xticks()
    plt.xlabel('Time')
    plt.ylabel('Tasks')

    plt.show()


def gantt_figure_drawing_only_picture(tasks_list):
    datas = []
    for task_index in range(len(tasks_list)):
        task = tasks_list[task_index]
        if tasks_list[task_index].isExert:
            status = 'running'
        else:
            status = 'stop'
        data = {'Task': task.satellite, 'Start': task.window_start_time,
                'End': task.window_end_time, 'Status': status}
        datas.append(data)

    unique_task_names = sorted(set(task['Task'] for task in datas))
    fig, ax = plt.subplots()

    status_colors = {
        'running': 'green',
        'stop': 'green'
    }

    for task in datas:
        task_name_index = unique_task_names.index(task['Task'])
        color = status_colors[task['Status']]

        # 计算已完成任务的持续时间
        duration = (task['End'] - task['Start'])

        # 对于具有相同任务名的任务，将其堆叠在一起
        ax.barh(task_name_index, duration, left=task['Start'], height=0.3, color=color)

    ax.set_yticks(range(len(unique_task_names)))
    ax.set_yticklabels(unique_task_names)

    ax.set_xlim(0, 86400)

    plt.xticks()
    plt.xlabel('Time')
    plt.ylabel('Tasks')

    # 添加图例
    legend_handles = [plt.Rectangle((0, 0), 1, 1, color=color) for color in status_colors.values()]
    plt.legend(legend_handles, status_colors.keys())

    plt.show()


def list_to_csv(data, output_file):
    # 将列表数据写入 CSV 文件
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for item in data:
            writer.writerow([item])
