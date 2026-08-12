import sys
import numpy as np
from dataclasses import dataclass


@dataclass
class Task:
    task_id: int
    e: float
    p: float
    d: float
    priority: int = 0


class RM_Scheduling:
    def __init__(self, tasks: list[Task]):
        self.tasks = tasks

    def print_tasks(self):
        self._get_priority()
        print(
            f"{'Task ID':<10} | {'Priority':<10} | {'Execution (E)':<15} | {'Period (P)':<15} | {'Deadline (D)':<15}"
        )
        print("-" * 75)

        for task in self.tasks:
            print(
                f"{task.task_id:<10} | {task.priority:<10} | {task.e:<15} | {task.p:<15} | {task.d:<15}"
            )

    def _get_priority(self):
        sorted_tasks = sorted(self.tasks, key=lambda t: t.p)
        for i, task in enumerate(sorted_tasks):
            task.priority = i + 1

    def _is_harmonic(self):  # make harmonic test
        if not self.tasks:
            return True

        periods = sorted([task.p for task in self.tasks])

        for i in range(len(periods) - 1):
            if periods[i + 1] % periods[i] != 0:
                return False
        return True

    def _get_utilization(self):
        n = len(self.tasks)
        if n == 0:
            return 0

        utilization = np.sum([task.e / task.p for task in self.tasks])

        if self._is_harmonic():
            rm_bound = 1.0
        else:
            rm_bound = n * ((2 ** (1 / n)) - 1)

        return utilization

    def _get_hyperperiod(self):
        if not self.tasks:
            return 0

        periods = np.array([int(task.p) for task in self.tasks])
        return int(np.lcm.reduce(periods))

    def get_premptions(self):
        self._get_priority()

        utilization = self._get_utilization()
        if utilization > 1:
            return {}

        hyperperiod = self._get_hyperperiod()
        sorted_tasks = sorted(self.tasks, key=lambda t: t.priority)

        preemptions = {task.task_id: 0 for task in self.tasks}
        remaining_e = {task.task_id: 0.0 for task in self.tasks}
        next_release = {task.task_id: 0.0 for task in self.tasks}

        t = 0.0
        last_running_task = None

        while t < hyperperiod:
            # Release jobs at time t
            for task in sorted_tasks:
                if t >= next_release[task.task_id]:
                    remaining_e[task.task_id] += task.e
                    next_release[task.task_id] += task.p

            # Find highest-priority ready task
            running_task = None
            for task in sorted_tasks:
                if remaining_e[task.task_id] > 1e-9:
                    running_task = task
                    break

            if running_task is None:  # SPEEEEEEEED UP
                next_t = min(next_release.values())
                t = next_t
                last_running_task = None
                continue

            # A preemption occurs only when a higher-priority task takes over
            # from a task that still has remaining work
            if (
                last_running_task is not None
                and last_running_task != running_task.task_id
                and remaining_e[last_running_task] > 1e-9
            ):
                # Verify the new task has higher priority (lower number)
                last_priority = next(
                    t.priority for t in self.tasks if t.task_id == last_running_task
                )
                if running_task.priority < last_priority:
                    preemptions[last_running_task] += 1

            # Determine how long this task can run
            time_to_finish = remaining_e[running_task.task_id]

            # Find the earliest release of any higher-priority task
            time_to_next_event = hyperperiod - t
            for task in sorted_tasks:
                if task.priority < running_task.priority:
                    time_until = next_release[task.task_id] - t
                    if time_until > 1e-9 and time_until < time_to_next_event:
                        time_to_next_event = time_until

            active_tasks = [
                task for task in sorted_tasks if remaining_e[task.task_id] > 1e-9
            ]

            if active_tasks:
                earliest_deadline = min(
                    next_release[task.task_id] - task.p + task.d
                    for task in active_tasks
                )
                time_to_next_event = min(time_to_next_event, earliest_deadline - t)

            run_time = min(time_to_finish, time_to_next_event)

            remaining_e[running_task.task_id] -= run_time
            t += run_time

            # 2. Did any task fail to finish before its absolute deadline?
            if any(
                t >= (next_release[task.task_id] - task.p + task.d) - 1e-9
                for task in sorted_tasks
                if remaining_e[task.task_id] > 1e-9
            ):
                return {}
            # If the task finished, it's no longer "running"
            if remaining_e[running_task.task_id] < 1e-9:
                last_running_task = None
            else:
                last_running_task = running_task.task_id

        return preemptions


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python script.py <task_file.csv>")
        sys.exit(1)

    with open(sys.argv[1], "r") as f:
        user_tasks = [
            Task(i + 1, *map(float, line.split(",")))
            for i, line in enumerate(f)
            if line.strip()
        ]

    rm_solver = RM_Scheduling(user_tasks)

    preemptions = rm_solver.get_premptions()

    if preemptions:
        print(1)
        print(",".join(str(count) for count in preemptions.values()))
    else:
        print(0)
        print()

