from time import sleep
from threading import Thread
from logging import INFO as level_info
from csv_logger import CsvLogger
from psutil import Process


class ResWatcher(object):
  
    def __init__(self,
                 delta:int=2, max_size:int=1024, max_files:int=1,
                 delimiter:str=';',file_path:str='consumption.csv',
                 custom_levels=['PROC']
                ):

        self.__file_path = file_path
        self.__delimiter=delimiter
        self.__delta=delta
        self.__loop = True
        self.__csvlogger = None
        self.__th = None
       
        self.log_options={
           'filename': file_path,
           'delimiter': delimiter,
           'level': level_info,
           'fmt': f'%(asctime)s{delimiter}%(levelname)s{delimiter}%(message)s',
           'datefmt': '%Y/%m/%d %H:%M:%S',
           'max_size': max_size,
           'max_files': max_files,
           'header': ['DATE_TIME', 'LEVEL', 'RAM', 'CPU'],
            'add_level_names': custom_levels
        }
        
        # Resource measurement
        from os import getpid
        self.__process = Process(getpid())
        del getpid
        self.__get_ram = lambda: round(self.__process.memory_info().rss / 1024 ** 2)
        self.__get_cpu = lambda: self.__process.cpu_percent()
        
        # Custom Register
        self.__register_process = lambda name, state: self.csvlogger.PROC([name, state])
        self.process_start = lambda name:  self.__register_process(name, 'START')
        self.process_finish = lambda name: self.__register_process(name, 'END')
        
        
    def __register_resources_usage(self):  
            while self.__loop:
                self.csvlogger.info([
                    self.__get_ram(),
                    self.__get_cpu(),
                ])
                sleep(self.__delta)

                
    def __gen_graph(self, date=False):
        from matplotlib import pyplot as plt
        from csv import reader as csv_reader
        
        res = []
        process = []
        usage = []
        __check_row_type = lambda x: True in [e.isnumeric() for e in x ]
        
        with open(self.__file_path) as csv_file:
            csv = csv_reader(csv_file, delimiter=self.__delimiter)
            for row in csv:
                res.append(row)
        
        del csv_reader


        header = True
        for row in res:
            if header:
                process.append(row); usage.append(row)
                header = False
                continue

            if __check_row_type(row): usage.append(row)
            else: process.append(row)


        timestamp = [e[0] for e in usage[1:]]
        if not date:
            timestamp = [e.split(' ')[-1] for e in timestamp]
        ram = [int(e[2]) for e in usage[1:]]
        cpu = [float(e[3]) for e in usage[1:]]

        
        fig, axs = plt.subplots(2)
        fig.autofmt_xdate(rotation=45)


        axs[0].plot(timestamp, ram)
        axs[0].set_title("RAM [MB]")
        axs[0].grid(True)

        axs[1].plot(timestamp, cpu)
        axs[1].set_title("CPU [%]")    
        axs[1].grid(True) 

        
        proc = {}
        for row in process[1:]:
            name = row[2]
            proctimestamp = row[0] if date else row[0].split(' ')[-1]

            if name in proc:
                if len(proc[name][-1]) == 1:
                    proc[name][-1].append(proctimestamp)
                else:
                    proc[name].append([proctimestamp])
            else:
                proc[name] = [[proctimestamp]]

            plt.savefig('resource_usage.png')
            
        del plt
        return proc
    
        
    def start(self):
        self.csvlogger = CsvLogger(**self.log_options)
        self.__th = Thread(target=self.__register_resources_usage)
        self.__th.start()

    
    def stop(self):
        self.__loop = False
        return self.__gen_graph()
        
