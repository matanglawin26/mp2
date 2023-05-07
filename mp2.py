class Process:
    def __init__(self, process_id: int, arrival: int, burst: int, priority: int):
        self._id = process_id
        self._arrival = arrival
        self._burst = burst
        self._remaining_time = burst
        self._priority = priority
        self._waiting_time = 0
        self._turnaround_time = 0

    def decrement(self, time: int = None):
        if time:
            self._remaining_time -= time
        else:
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
        self._headers = ['Process', 'Arrival', 'CPU Burst Time',
                         'Priority', 'Waiting Time', 'Turnaround Time']
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
        for process in self._processes:
            if not process.is_complete():
                return False

        return True

    def _add_queue(self, job: dict):
        self._queue.append(job)
        self._queue = sorted(self._queue, key=lambda process: process['burst'])

    def _remove(self, curr_process: Process):
        for process in self._arrived:
            if process._id == curr_process._id and curr_process.is_complete():
                self._arrived.remove(process)

    def _remove2(self, job_id: int):
        for job in self._queue:
            if job['id'] == job_id:
                self._queue.remove(job)

    def _get_process(self, process_id: int):
        for process in self._processes:
            if process._id == process_id:
                return process

    def _get_total_waiting_time(self, process_id: int):
        time_list = []

        for job in self._gantt.get_jobs():
            if job['process_id'] == process_id:
                time_list.append(
                    {'waiting_time': job['waiting_time'], 'turnaround_time': job['turnaround_time']})

        final_exec = time_list[-1]['waiting_time']
        time_list = time_list[:-1]
        prior_exec = sum(job['turnaround_time'] -
                         job['waiting_time'] for job in time_list)

        return final_exec - prior_exec

    def _get_total_turnaround_time(self, process_id: int):
        total_time = 0

        for job in self._gantt.get_jobs():
            if job['process_id'] == process_id:
                if job['turnaround_time'] > total_time:
                    total_time = job['turnaround_time']

        return total_time

    def display(self):
        print('{:<10} {:<12} {:<18} {:<12} {:<16} {:<20}'.format(*self._headers))
        for process in self._processes:
            print('{:<10} {:<12} {:<18} {:<12} {:<16} {:<20}'.format(process._id, process._arrival,
                  process._burst, process._priority, process._waiting_time, process._turnaround_time))
            self._total_waiting_time += process._waiting_time
            self._total_turnaround_time += process._turnaround_time

        self._average_waiting_time = self._total_waiting_time / \
            len(self._processes)
        self._average_turnaround_time = self._total_turnaround_time / \
            len(self._processes)

        print()
        print("Average waiting time: %.2f ms" % self._average_waiting_time)
        print("Average turnaround time: %.2f ms" %
              self._average_turnaround_time)


class FCFS(Scheduling):
    def __init__(self):
        super().__init__()

    def compute(self, processes: list):
        self._processes = self.set_processes(processes)

        for process in self._processes:
            waiting_time = self._curr_turnaround_time
            process.set_waiting_time(waiting_time)
            self.set_curr_waiting_time(waiting_time)

            turnaround_time = self._curr_waiting_time + process._burst
            process.set_turnaround_time(turnaround_time)
            self.set_curr_turnaround_time(turnaround_time)

            self._gantt.add_job(
                {"process_id": process._id, "waiting_time": waiting_time, "turnaround_time": turnaround_time})

        return self


class SJF(Scheduling):
    def __init__(self):
        super().__init__()

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

            self._gantt.add_job(
                {"process_id": process._id, "waiting_time": waiting_time, "turnaround_time": turnaround_time})

        self._processes = sorted(processes, key=lambda process: process._id)

        return self

    def _sort(self, process):
        return (process._burst, process._arrival, process._id)


class SRPT(Scheduling):
    def __init__(self):
        super().__init__()
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

                self._gantt.add_job(
                    {"process_id": curr_process._id, "waiting_time": waiting_time, "turnaround_time": turnaround_time})

                if len(self._arrived) == 0:
                    break

                curr_process = self._arrived[0]

            curr_process.decrement()
            self._clock += 1

        for process in self._processes:
            total_waiting_time = self._get_total_waiting_time(
                process._id) - process._arrival
            total_turnaround_time = self._get_total_turnaround_time(
                process._id)

            process.set_waiting_time(total_waiting_time)
            process.set_turnaround_time(total_turnaround_time)

        return self

    def _sort(self, process):
        return (process._remaining_time, process._arrival, process._id)


class Priority(Scheduling):
    def __init__(self):
        super().__init__()

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

            self._gantt.add_job(
                {"process_id": process._id, "waiting_time": waiting_time, "turnaround_time": turnaround_time})

        self._processes = sorted(processes, key=lambda process: process._id)

        return self

    def _sort(self, process):
        return (process._priority, process._id)


class RoundRobin(Scheduling):
    def __init__(self):
        super().__init__()
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

            self._gantt.add_job(
                {"process_id": curr_process._id, "waiting_time": waiting_time, "turnaround_time": turnaround_time})

            if curr_process.is_complete():
                self._queue.remove(curr_process)
            else:
                self._queue.append(self._queue.pop(0))

        for process in self._processes:
            total_waiting_time = self._get_total_waiting_time(
                process._id)
            total_turnaround_time = self._get_total_turnaround_time(
                process._id)

            process.set_waiting_time(total_waiting_time)
            process.set_turnaround_time(total_turnaround_time)

        return self

    def compute2(self, processes: list):
        self._processes = processes
        processes_copy = processes

        while len(processes_copy):
            for process in processes_copy:
                if process.is_complete():
                    processes_copy.remove(process)
                else:
                    waiting_time = self._curr_turnaround_time
                    process.set_waiting_time(waiting_time)
                    self.set_curr_waiting_time(waiting_time)

                    if process._burst >= 4:
                        turnaround_time = self._curr_waiting_time + process._burst
                        process.set_turnaround_time(turnaround_time)
                        self.set_curr_turnaround_time(turnaround_time)
                    else:
                        turnaround_time = self._curr_waiting_time + process._burst

        return self


class Gantt:
    def __init__(self):
        self._jobs = []

    def get_jobs(self):
        return self._jobs

    def add_job(self, job: dict):
        self._jobs.append(job)

    def __repr__(self):
        return "%s" % self._jobs


def main():
    # Process 1
    file1 = open('process1.txt', 'r')
    file2 = open('process2.txt', 'r')
    test = open('srpttest2.txt', 'r')

    files = [file1, file2]

    for file in files:
        fcfs = FCFS()
        sjf = SJF()
        srpt = SRPT()
        priority = Priority()
        round_robin = RoundRobin()

        processes = []
        file.readline()  # Skip the header
        for line in file:
            if len(line):
                process_id, arrival, burst, priority_num = map(
                    int, line.split())
                process_data = [process_id, arrival, burst, priority_num]
                processes.append(process_data)

        # fcfs.compute(processes).display()
        # sjf.compute(processes).display()
        # srpt.compute(processes).display()
        # priority.compute(processes).display()
        round_robin.compute(processes).display()

        print()
        file.close()

    return


main()
