import time

import genetic_main as gm
import tool as t


def run():
    # GA参数
    generations = 150
    population_size = 50
    crossover_rate = 0.9
    mutation_early_rate = 0.1
    mutation_lately_rate = 0.01
    tournament_size = [2, 5]

    # 存储每次迭代的结果
    results = []

    # Tabu参数
    tabu_limit = 35
    tabu_list = []  # 全局禁忌表
    tabu_time = []  # 禁忌次数

    # 生成任务并计算总适应度值
    tasks = gm.task_generation()
    sums = 0
    for number in tasks:
        sum_ = tasks[number].priority * (tasks[number].end_time - tasks[number].start_time)
        sums += sum_
    print(sums)

    first_pops, fits, tasks_exerts = gm.Population_Generation_tabu(tasks, 150, 0.5)

    # 保存当前种群最优
    best_fit = max(fits)
    best_index = fits.index(best_fit)
    best_pop = first_pops[best_index]
    best_task_exerts = tasks_exerts[best_index]

    # 全局禁忌表更新
    tabu_list.append(best_pop)
    tabu_time.append(tabu_limit)

    start = time.time()
    # 遗传算法开始迭代
    for generation in range(generations):
        first_pops, fits, tasks_exerts = gm.Tabu_and_GA_main(tasks, tasks_exerts, first_pops,
                                                             population_size, fits,
                                                             tournament_size, crossover_rate,
                                                             mutation_early_rate, mutation_lately_rate
                                                             , tabu_list, sums, generation, generations)
        tabu_time = [x - 1 for x in tabu_time]
        if 0 in tabu_time:
            tabu_list.remove(tabu_list[tabu_time.index(0)])
            tabu_time.remove(0)

        if best_fit < max(fits):
            best_fit = max(fits)
            best_pop = first_pops[fits.index(best_fit)]
            best_task_exerts = tasks_exerts[fits.index(best_fit)]
        # 添加禁忌
        tabu_list.append(best_pop)
        tabu_time.append(tabu_limit)

        results.append(best_fit)
    print('禁忌遗传算法计算出的适应度值为:', results[-1])
    print(f'程序运行时间为：{time.time() - start}')
    success_count = 0
    p_success_count = 0
    p_task = 0
    for value, _ in enumerate(best_task_exerts):
        if best_task_exerts[value] is not None and best_task_exerts[value] != -1:
            success_count += 1
            if tasks[best_pop[value]].priority == 2:
                p_success_count += 1
        if tasks[best_pop[value]].priority == 2:
            p_task += 1
        if best_task_exerts[value] == -1:
            print(f'任务{best_pop[value]}因为跨链路问题不能执行')
    print(f'禁忌遗传算法计算出的任务执行成功率为：{success_count / len(tasks)}, 成功执行的任务数：{success_count}，总任务数：{len(tasks)}')
    print(f'禁忌遗传算法计算出的重要任务任务执行成功率为：{p_success_count / p_task}, 成功执行的重要任务数：{p_success_count}，总任务数：{p_task}')
    print(f'禁忌遗传算法计算出的任务执行顺序：{best_pop}')
    print(f'禁忌遗传算法计算出的任务执行情况：{best_task_exerts}')
    t.Drawing(generations, results)
    t.gantt_figure_drawing(tasks, best_task_exerts, best_pop)
    t.gantt_figure_drawing_deviceUsing(tasks, best_task_exerts, best_pop)
    t.list_to_csv(results, 'tabu_res.csv')
    return results[-1], best_pop


def sortedDictValues2(adict):
    sorted_dict = {key: adict[key] for key in sorted(adict)}
    return sorted_dict


if __name__ == '__main__':
    for i in range(1):
        print(f'第{i + 1}次执行任务')
        run()
        print('-------------------------------------------------------------------')
