import sys
from dataclasses import dataclass

@dataclass
class Task:
    task_id: int
    e: float
    p: float
    d: float

class RM_Scheduling:
    def __init__(self, tasks: list[Task]):
        self.tasks = tasks
        
    def print_tasks(self):
        print(f"{'Task ID':<10} | {'Execution (E)':<15} | {'Period (P)':<15} | {'Deadline (D)':<15}")
        print("-" * 63)
        
        for task in self.tasks:
            print(f"{task.task_id:<10} | {task.e:<15} | {task.p:<15} | {task.d:<15}")
    
    def _is_harmonic(self):
        pass
    
    def _is_under_uterlization(self):
        pass
    
    def get_schedule(self):
        pass

if __name__ == "__main__":
    with open(sys.argv[1], 'r') as f:
        user_tasks = [Task(i+1, *map(float, line.split(','))) for i, line in enumerate(f) if line.strip()]
        
    rm_solver = RM_Scheduling(user_tasks)
    
    rm_solver.print_tasks()