from typing import TextIO

class Logger:
    __path_to_log_file: str
    __log_file: TextIO
    def __init__(self, path_to_log_file: str):
        self.__path_to_log_file = path_to_log_file
        self.__log_file = open(self.__path_to_log_file, mode='a')

    def log(self, log_content: str):
        print(log_content)
        self.__log_file.write(log_content + '\n')
        self.__log_file.flush()