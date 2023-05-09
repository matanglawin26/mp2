class Process:
    def __init__(self, process_id: int, arrival: int, burst: int, priority: int):
        self._id = process_id
        self._arrival = arrival
        self._burst = burst
        self._remaining_time = burst
        self._priority = priority
        self._waiting_time = 0
        self._turnaround_time = 0

    def decrement(self):
        self._remaining_time -= 1

    def set_waiting_time(self, time: int):
        self._waiting_time = time

    def set_turnaround_time(self, time: int):
        self._turnaround_time = time

    def is_complete(self):
        return self._remaining_time <= 0

    def __repr__(self):
        return "PROCESS ID: %d\nARRIVAL: %d\nBURST: %d\nPRIORITY: %d\nWAITING TIME: %d\nTURNAROUND TIME: %d\n\n" % (self._id, self._arrival, self._burst, self._priority, self._waiting_time, self._turnaround_time)

class Scheduling:
    def __init__(self):
        self._processes = []
        self._headers = ['Process', 'Arrival', 'CPU Burst Time','Priority', 'Waiting Time (ms)', 'Turnaround Time (ms)']
        self._curr_waiting_time = 0
        self._curr_turnaround_time = 0
        self._total_waiting_time = 0
        self._total_turnaround_time = 0
        self._gantt = Gantt()

    def set_processes(self, processes: list):
        return [Process(*process_data) for process_data in processes]

    def set_curr_waiting_time(self, time: int):
        self._curr_waiting_time = time

    def set_curr_turnaround_time(self, time: int):
        self._curr_turnaround_time = time

    def is_finished(self):
        return all(False if not process.is_complete() else True for process in self._processes)

    def _remove(self, curr_process: Process):
        for process in self._arrived:
            if process._id == curr_process._id and curr_process.is_complete():
                self._arrived.remove(process)

    def _get_total_waiting_time(self, process_id: int):
        max_turnaround = 0
        burst_time = 0
        
        for job in self._gantt.get_jobs():
            if job['process_id'] == process_id:
                if job['turnaround_time'] > max_turnaround:
                    max_turnaround = job['turnaround_time']
                    burst_time = job['burst_time']

        return max_turnaround - burst_time

    def _get_total_turnaround_time(self, process_id: int):
        return max(job['turnaround_time'] for job in self._gantt.get_jobs() if job['process_id'] == process_id)

    def display(self):
        print("═" * 38 + " " + self._title + " " + 38 * "═", '\n')
        # Display Gantt Chart
        self._gantt.show()
        
        print("-" * 41 + " Table " + 41 * "-")
        
        print('{:<10} {:<12} {:<18} {:<12} {:<20} {:<24}'.format(*self._headers))
        for process in self._processes:
            print('{:<10} {:<12} {:<18} {:<12} {:<20} {:<24}'.format(process._id, process._arrival,
                  process._burst, process._priority, process._waiting_time, process._turnaround_time))
            self._total_waiting_time += process._waiting_time
            self._total_turnaround_time += process._turnaround_time

        self._average_waiting_time = self._total_waiting_time / len(self._processes)
        self._average_turnaround_time = self._total_turnaround_time / len(self._processes)

        print("\nAverage waiting time: %.2f ms" % self._average_waiting_time)
        print("Average turnaround time: %.2f ms\n" %self._average_turnaround_time)

class FCFS(Scheduling):
    def __init__(self):
        super().__init__()
        self._title = "FCFS"

    def compute(self, processes: list):
        self._processes = self.set_processes(processes)

        for process in self._processes:
            waiting_time = self._curr_turnaround_time
            process.set_waiting_time(waiting_time)
            self.set_curr_waiting_time(waiting_time)

            turnaround_time = self._curr_waiting_time + process._burst
            process.set_turnaround_time(turnaround_time)
            self.set_curr_turnaround_time(turnaround_time)

            self._gantt.add_job({ "process_id": process._id, "burst_time": process._burst, "waiting_time": waiting_time, "turnaround_time": turnaround_time })

        return self

class SJF(Scheduling):
    def __init__(self):
        super().__init__()
        self._title = "SJF"

    def compute(self, processes: list):
        processes = self.set_processes(processes)
        self._processes = sorted(processes, key=self._sort)

        for process in self._processes:
            waiting_time = self._curr_turnaround_time
            process.set_waiting_time(waiting_time)
            self.set_curr_waiting_time(waiting_time)

            turnaround_time = self._curr_waiting_time + process._burst
            process.set_turnaround_time(turnaround_time)
            self.set_curr_turnaround_time(turnaround_time)

            self._gantt.add_job({ "process_id": process._id, "burst_time": process._burst, "waiting_time": waiting_time, "turnaround_time": turnaround_time })

        self._processes = sorted(processes, key=lambda process: process._id)

        return self

    def _sort(self, process):
        return (process._burst, process._arrival, process._id)

class SRPT(Scheduling):
    def __init__(self):
        super().__init__()
        self._title = "SRPT"
        self._arrived = []
        self._clock = 0

    def compute(self, processes: list):
        self._processes = self.set_processes(processes)
        self._processes = sorted(
            self._processes, key=lambda process: process._id)
        curr_process = None

        while True:
            for process in self._processes:
                if process._arrival == self._clock:
                    self._arrived.append(process)

            self._arrived = sorted(self._arrived, key=self._sort)

            if curr_process is None:
                curr_process = self._arrived[0]

            # New Process with shorter burst time arrived
            # or curr process is complete
            if curr_process != self._arrived[0] or curr_process.is_complete():
                waiting_time = self._curr_turnaround_time
                self.set_curr_waiting_time(waiting_time)

                turnaround_time = self._clock
                self.set_curr_turnaround_time(turnaround_time)

                self._remove(curr_process)

                self._gantt.add_job({ "process_id": curr_process._id, "burst_time":curr_process._burst, "waiting_time": waiting_time, "turnaround_time": turnaround_time })

                if len(self._arrived) == 0:
                    break

                curr_process = self._arrived[0]

            curr_process.decrement()
            self._clock += 1

        for process in self._processes:
            total_waiting_time = self._get_total_waiting_time(process._id) - process._arrival
            total_turnaround_time = self._get_total_turnaround_time(process._id)

            process.set_waiting_time(total_waiting_time)
            process.set_turnaround_time(total_turnaround_time)

        return self

    def _sort(self, process):
        return (process._remaining_time, process._arrival, process._id)

class Priority(Scheduling):
    def __init__(self):
        super().__init__()
        self._title = "Priority"

    def compute(self, processes: list):
        processes = self.set_processes(processes)
        self._processes = sorted(processes, key=self._sort)

        for process in self._processes:
            waiting_time = self._curr_turnaround_time
            process.set_waiting_time(waiting_time)
            self.set_curr_waiting_time(waiting_time)

            turnaround_time = self._curr_waiting_time + process._burst
            process.set_turnaround_time(turnaround_time)
            self.set_curr_turnaround_time(turnaround_time)

            self._gantt.add_job({ "process_id": process._id, "burst_time": process._burst, "waiting_time": waiting_time, "turnaround_time": turnaround_time })

        self._processes = sorted(processes, key=lambda process: process._id)

        return self

    def _sort(self, process):
        return (process._priority, process._id)

class RoundRobin(Scheduling):
    def __init__(self):
        super().__init__()
        self._title = "Round Robin"
        self._clock = 0
        self._queue = []
        self._quantum = 4

    def compute(self, processes: list):
        processes = self.set_processes(processes)
        self._processes = sorted(
            processes, key=lambda process: process._id)
        self._queue = sorted(
            processes, key=lambda process: process._id)

        while len(self._queue) > 0:
            time = 0
            curr_process = self._queue[0]

            while time < self._quantum and not curr_process.is_complete():
                curr_process.decrement()
                self._clock += 1
                time += 1

            waiting_time = self._curr_turnaround_time
            self.set_curr_waiting_time(waiting_time)

            turnaround_time = self._clock
            self.set_curr_turnaround_time(turnaround_time)

            self._gantt.add_job({ "process_id": curr_process._id, "burst_time":curr_process._burst, "waiting_time": waiting_time, "turnaround_time": turnaround_time })

            if curr_process.is_complete():
                self._queue.remove(curr_process)
            else:
                self._queue.append(self._queue.pop(0))

        for process in self._processes:
            total_waiting_time = self._get_total_waiting_time(process._id)
            total_turnaround_time = self._get_total_turnaround_time(process._id)

            process.set_waiting_time(total_waiting_time)
            process.set_turnaround_time(total_turnaround_time)

        return self

class Gantt:
    def __init__(self):
        self._jobs = []

    def get_jobs(self):
        return self._jobs

    def add_job(self, job: dict):
        self._jobs.append(job)

    def show(self):
        length = len(self._jobs)
        
        print("-" * 41 + " Gantt Chart " + 41 * "-")
        
        row_limit = 10
        row = (length + row_limit - 1) // row_limit

        for row_idx in range(row):
            start_idx = row_idx * row_limit
            end_idx = min(length, (row_idx + 1) * row_limit)
            
            for i in range(start_idx, end_idx):
                process_id = self._jobs[i]['process_id']
                pad = ""
                
                if process_id >= 10:
                    pad = "─"
                    
                if end_idx - start_idx == 1:
                    print("┌────%s────┐" % pad)
                else:
                    if i == start_idx:
                        print("┌────%s────┬" % pad, end="")
                    elif i == end_idx - 1:
                        print("────%s────┐" % pad)
                    else:
                        print("────%s────┬" % pad, end="")
                    
            for i in range(start_idx, end_idx):
                process_id = self._jobs[i]['process_id']
                    
                if end_idx - start_idx == 1:
                    print("│   P%s   │" % (process_id))
                else:
                    if i == start_idx:
                        print("│   P%s   │" % (process_id), end="")
                    elif i == end_idx - 1:
                        print("   P%s   │" % (process_id))
                    else:
                        print("   P%s   │" % (process_id), end="")
                    
            for i in range(start_idx, end_idx):
                process_id = self._jobs[i]['process_id']
                pad = ""
                
                if process_id >= 10:
                    pad = "─"
                    
                if end_idx - start_idx == 1:
                    print("├────%s────┤" % pad)
                else:
                    if i == start_idx:
                        print("├────%s────┼" % pad, end="")
                    elif i == end_idx - 1:
                        print("────%s────┤" % pad)
                    else:
                        print("────%s────┼" % pad, end="")
                    
            for i in range(start_idx, end_idx + 1):
                if i < end_idx:
                    process_id = self._jobs[i]['process_id']
                    
                    if process_id >= 10:
                        print("{:<10}".format(self._jobs[i]['waiting_time']), end="")
                    else:
                        print("{:<9}".format(self._jobs[i]['waiting_time']), end="")
                else:
                    print(self._jobs[i-1]['turnaround_time'])
                    
            print()
        print()

    def __repr__(self):
        return "%s" % self._jobs

def main():
    files = ['process1.txt']

    for file_name in files:
        print("┅" * 38 + " " + file_name + " " + 38 * "┅", "\n")
        file = open(file_name, 'r')
        
        fcfs = FCFS()
        sjf = SJF()
        srpt = SRPT()
        priority = Priority()
        round_robin = RoundRobin()

        processes = []
        file.readline()  # Skip the header
        for line in file:
            if len(line):
                process_id, arrival, burst, priority_num = map(int, line.split())
                process_data = [process_id, arrival, burst, priority_num]
                processes.append(process_data)

        fcfs.compute(processes).display()
        sjf.compute(processes).display()
        srpt.compute(processes).display()
        priority.compute(processes).display()
        round_robin.compute(processes).display()

        file.close()

    return

main()