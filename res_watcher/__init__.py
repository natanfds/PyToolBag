from time import sleep
from threading import Thread
from logging import INFO as level_info
from csv_logger import CsvLogger
from psutil import Process
from os import getpid




class ResWatcher(object):
  
    def __init__(self,
                 delta:int=2, max_size:int=1024, max_files:int=4,
                 delimiter:str=';',file_path:str='consumption.csv',
                 custom_levels=['PROCESS']
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
        self.__process = Process(getpid())
        self.__get_ram = lambda: round(self.__process.memory_info().rss / 1024 ** 2)
        self.__get_cpu = lambda: self.__process.cpu_percent()
        
        # Custom Register
        self.__register_process = lambda name, state: self.csvlogger.PROCESS([name, state])
        self.process_start = lambda name:  self.__register_process(name, 'START')
        self.process_finish = lambda name: self.__register_process(name, 'END')
        
        
    def __register_resources_usage(self):  
            while self.__loop:
                self.csvlogger.info([
                    self.__get_ram(),
                    self.__get_cpu(),
                ])
                sleep(self.__delta)


        
    def start(self):
        self.csvlogger = CsvLogger(**self.log_options)
        self.__th = Thread(target=self.__register_resources_usage)
        self.__th.start()

    #TODO: gerar gráfico de consumo
    def stop(self):
        self.__loop = False
