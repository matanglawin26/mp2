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
        # if time:
        #     self._burst -= time
        # else:
        #     self._burst -= 1        
        if time:
            self._remaining_time -= time
        else:
            self._remaining_time -= 1        
        
    def set_waiting_time(self, time: int):
        self._waiting_time = time
    
    def set_turnaround_time(self, time: int):
        self._turnaround_time = time
    
    def is_complete(self):
        # return self._burst <= 0 
        return self._remaining_time <= 0 
    
    def __repr__(self):
        return "PROCESS ID: %d\nARRIVAL: %d\nBURST: %d\nPRIORITY: %d\nWAITING TIME: %d\nTURNAROUND TIME: %d\n\n" % (self._id, self._arrival, self._burst, self._priority, self._waiting_time, self._turnaround_time)
        
class Scheduling:
    def __init__(self):
        self._processes = []
        self._headers = ['Process', 'Arrival', 'CPU Burst Time', 'Priority', 'Waiting Time', 'Turnaround Time']
        self._curr_waiting_time = 0
        self._curr_turnaround_time = 0
        self._total_waiting_time = 0
        self._total_turnaround_time = 0        
        self._gantt = Gantt()
    
    def set_processes(self, processes: list):
        return [Process(*process_data) for process_data in processes]
    
    def set_curr_waiting_time(self, time: int):
        self._curr_waiting_time = time
        # self._total_waiting_time += time
    
    def set_curr_turnaround_time(self, time: int):
        self._curr_turnaround_time = time
        # self._total_turnaround_time += time
    
    def is_finished(self):
        for process in self._processes:
            if not process.is_complete():
                return False
            
        return True
    
    def _add_queue(self, job: dict):
        self._queue.append(job)
        self._queue = sorted(self._queue, key=lambda process: process['burst'])
    
    def _remove(self, job_id: int):
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
                time_list.append({ 'waiting_time': job['waiting_time'], 'turnaround_time': job['turnaround_time'] })
        
        final_exec = time_list[-1]['waiting_time']
        time_list = time_list[:-1]
        prior_exec = sum(job['turnaround_time'] - job['waiting_time'] for job in time_list)
        
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
            print('{:<10} {:<12} {:<18} {:<12} {:<16} {:<20}'.format(process._id, process._arrival, process._burst, process._priority, process._waiting_time, process._turnaround_time))
            self._total_waiting_time += process._waiting_time
            self._total_turnaround_time += process._turnaround_time
            
        self._average_waiting_time = self._total_waiting_time / len(self._processes)
        self._average_turnaround_time = self._total_turnaround_time / len(self._processes)
        
        print()
        print("Average waiting time:", round(self._average_waiting_time, 2))
        print("Average turnaround time:", round(self._average_turnaround_time, 2))

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
            
        self._processes = sorted(processes, key=lambda process: process._id)
    
    def _sort(self, process):        
        return (process._burst, process._arrival, process._id)

class SRPT(Scheduling):
    def __init__(self):
        super().__init__()      
        self._queue = []
        self._clock = 0
            
    def compute(self, processes: list):
        processes = self.set_processes(processes)
        processes = sorted(processes, key=lambda process: process._id)
        self._processes = processes
        
        curr_process = processes[0]
        processes = processes[1:]
        # processes = sorted(processes[1:], key=self._sort)
        # while True:
        for process in processes:
            # if process.is_complete():
            #     continue
            # if curr_process.is_complete():
            #     curr_process_id = self._queue[0]['id']
            #     curr_process
                
            self._add_queue({ "id":process._id, "burst": process._remaining_time})
            
            waiting_time = self._curr_turnaround_time
            self.set_curr_waiting_time(waiting_time)
            
            curr_remaining_time = curr_process._remaining_time - (process._arrival - curr_process._arrival)
            
            if process._remaining_time < curr_remaining_time:
                curr_process.decrement((process._arrival - curr_process._arrival))
                turnaround_time = self._curr_waiting_time + process._arrival 
                # process.set_turnaround_time(turnaround_time)
                self.set_curr_turnaround_time(turnaround_time)   
                self._remove(process._id)
                self._add_queue({ "id":curr_process._id, "burst": curr_process._remaining_time})
                # self._add_queue({ "id":curr_process._id, "burst": curr_process._remaining_time})
                self._gantt.add_job({ "process_id": curr_process._id, "waiting_time": waiting_time, "turnaround_time": turnaround_time })
                curr_process = process
            
            print("QUEUE:", self._queue)
            print("GANTT:", self._gantt)
            # input("\nPress to continue...\n")
        
        while not self.is_finished():            
            # if curr_process.is_complete():        
            waiting_time = self._curr_turnaround_time
            self.set_curr_waiting_time(waiting_time)
            
            turnaround_time = self._curr_waiting_time + curr_process._remaining_time 
            self.set_curr_turnaround_time(turnaround_time)  
                
            self._gantt.add_job({ "process_id": curr_process._id, "waiting_time": waiting_time, "turnaround_time": turnaround_time })
            curr_process.decrement(curr_process._remaining_time)
            
            if len(self._queue):
                curr_process_id = self._queue[0]['id']
                curr_process = self._get_process(curr_process_id)
                self._remove(curr_process._id)
            
            print("QUEUE:", self._queue)
            print("GANTT:", self._gantt)
            # else:
            #     curr_process.decrement()                
        
        for process in self._processes:
            total_waiting_time = self._get_total_waiting_time(process._id) - process._arrival
            total_turnaround_time = self._get_total_turnaround_time(process._id)
            
            process.set_waiting_time(total_waiting_time) 
            process.set_turnaround_time(total_turnaround_time)    

            
    def compute2(self, processes: list):
        processes = self.set_processes(processes)
        self._processes = sorted(processes, key=lambda process: process._id)
        
        curr_process = self._processes[0]
        self._processes = self._processes[1:]
        # self._processes = sorted(self._processes[1:], key=self._sort)
        
        for process in self._processes:
            print("\nCURR PROCESS:", curr_process, "NEW PROCESS:", process)
            
            waiting_time = self._curr_turnaround_time
            self.set_curr_waiting_time(waiting_time)
            
            curr_remaining_time = curr_process._burst - (process._arrival - curr_process._arrival)
            
            if process._burst < curr_remaining_time:
                # process.set_waiting_time(waiting_time)       
                curr_process.decrement(curr_remaining_time)
                turnaround_time = self._curr_waiting_time + process._arrival 
                # process.set_turnaround_time(turnaround_time)
                self.set_curr_turnaround_time(turnaround_time)   
                
                self._add_queue({ "id":curr_process._id, "burst": curr_process._burst})
                self._gantt.add_job({ "process_id": curr_process._id, "waiting_time": waiting_time, "turnaround_time": turnaround_time })
                curr_process = process
            else:
                curr_process.decrement()
                print("CURR PROCESS BURST TIME:", curr_process._burst)
                self._add_queue({ "id": process._id, "burst": process._burst })
                # curr_process.set_waiting_time(waiting_time)
                # turnaround_time = self._curr_waiting_time + curr_process._burst 
                # curr_process.set_turnaround_time(turnaround_time)
                # self.set_curr_turnaround_time(turnaround_time)   
                # self._gantt.add_job({ "process_id": curr_process._id, "waiting_time": waiting_time, "turnaround_time": turnaround_time })
                
            
            print("QUEUE:", self._queue)
            print("GANTT:", self._gantt)
            # input("\nPress to continue...\n")
                
    
    # def compute_beta(self, processes: list):
    #     processes = self.set_processes(processes)
    #     self._processes = sorted(processes, key=lambda process: process._id)
        
    #     curr_process = self._processes[0]
    #     self._processes = self._processes[1:]
    #     # self._processes = sorted(self._processes[1:], key=self._sort)
        
    #     while not self.is_finished():
    #         for process in self._processes:
    #             waiting_time = self._curr_turnaround_time
    #             self.set_curr_waiting_time(waiting_time)
                
    #             if not process.is_complete():
    #                 if process._burst < curr_process._burst - process._arrival:
    #                     curr_process = process
                
    #             self._clock += 1
        
        # for process in self._processes:
        #     waiting_time = self._curr_turnaround_time
        #     process.set_waiting_time(waiting_time)        
        #     self.set_curr_waiting_time(waiting_time)
            
        #     turnaround_time = self._curr_waiting_time + process._burst 
        #     process.set_turnaround_time(turnaround_time)
        #     self.set_curr_turnaround_time(turnaround_time)   
            
        # self._processes = sorted(processes, key=lambda process: process._id)
    
    
    def _sort(self, process):        
        return (process._burst, process._arrival, process._id)

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
            
        self._processes = sorted(processes, key=lambda process: process._id)
    
    def _sort(self, process):        
        return (process._priority, process._id)

class RoundRobin(Scheduling):
    def __init__(self):
        super().__init__()
        self._quantum = 4

    def compute(self, processes: list):
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
            
    
    def _is_done(self):
        for process in self._processes:
            if process.is_complete():
                return False     
               
        return True

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
    
    files = [test]
    
    fcfs = FCFS()
    sjf = SJF()
    srpt = SRPT()
    priority = Priority()
    round_robin = RoundRobin()
    
    processes = []
    
    for file in files:
        file.readline() # Skip the header
        for line in file:
            process_id, arrival, burst, priority_num = map(int, line.split())
            # print("PROCESS ID:", process_id, "ARRIVAL:", arrival, "BURST:", burst, "PRIORITY:", priority)      
            process_data = [process_id, arrival, burst, priority_num]
            processes.append(process_data)
            # fcfs.add_process(Process(process_id, arrival, burst, priority))
            # sjf.add_process(Process(process_id, arrival, burst, priority))
            # print(line)
            # print("WAIT TIME:",process._waiting_time)
            # print("TURNAROUND TIME:",process._turnaround_time)
            
        file.close()
        
    # fcfs.compute(processes)     
    # sjf.compute(processes)     
    # srpt.compute(processes)     
    priority.compute(processes)     
    # round_robin.compute(processes)     
    
    # fcfs.display()
    # sjf.display()    
    # srpt.display()
    priority.display()    
    
    return

main()