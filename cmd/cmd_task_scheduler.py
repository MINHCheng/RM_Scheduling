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

        int_periods = np.array([int(round(task.p * 1000)) for task in self.tasks])
        return int(np.lcm.reduce(int_periods)) / 1000

    def get_premptions(self):
        self._get_priority()

        utilization = self._get_utilization()
        if utilization > 1:
            return {}

        sorted_tasks = sorted(self.tasks, key=lambda t: t.priority)
        n = len(sorted_tasks)

        # Scale everything to integers (x1000) to avoid float drift
        SCALE = 1000
        exec_times = [int(round(task.e * SCALE)) for task in sorted_tasks]
        periods = [int(round(task.p * SCALE)) for task in sorted_tasks]
        deadlines = [int(round(task.d * SCALE)) for task in sorted_tasks]
        task_ids = [task.task_id for task in sorted_tasks]

        hyperperiod = int(np.lcm.reduce(np.array(periods)))

        preemptions = [0] * n
        remaining_e = [0] * n
        next_release = [0] * n

        t = 0
        last_running_idx = -1

        while t < hyperperiod:
            # Release jobs at time t
            for i in range(n):
                if t >= next_release[i]:
                    remaining_e[i] += exec_times[i]
                    next_release[i] += periods[i]

            # Find highest-priority ready task (already sorted)
            running_idx = -1
            for i in range(n):
                if remaining_e[i] > 0:
                    running_idx = i
                    break

            if running_idx == -1:
                t = min(next_release)
                last_running_idx = -1
                continue

            # Check preemption: higher-priority task took over
            if (
                last_running_idx >= 0
                and last_running_idx != running_idx
                and remaining_e[last_running_idx] > 0
                and running_idx < last_running_idx
            ):
                preemptions[last_running_idx] += 1

            # Determine how long this task can run
            time_to_next_event = hyperperiod - t

            # Next higher-priority release
            for i in range(running_idx):
                time_until = next_release[i] - t
                if time_until > 0 and time_until < time_to_next_event:
                    time_to_next_event = time_until

            # Deadline of any waiting task
            for i in range(n):
                if remaining_e[i] > 0:
                    abs_deadline = (next_release[i] - periods[i]) + deadlines[i]
                    dt = abs_deadline - t
                    if dt > 0 and dt < time_to_next_event:
                        time_to_next_event = dt

            run_time = min(remaining_e[running_idx], time_to_next_event)
            remaining_e[running_idx] -= run_time
            t += run_time

            # Deadline check
            for i in range(n):
                if remaining_e[i] > 0:
                    abs_deadline = (next_release[i] - periods[i]) + deadlines[i]
                    if t >= abs_deadline:
                        return {}

            # Track last running task
            if remaining_e[running_idx] <= 0:
                last_running_idx = -1
            else:
                last_running_idx = running_idx

        result = {task_ids[i]: preemptions[i] for i in range(n)}
        return dict(sorted(result.items()))


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

