import os
import sys


class Arguments():
    """Reads through arguments from CMD and parses them into usable data witch it stores"""
    source: str = None
    replica: str = None
    log: str = None
    timeout: int = None
    def __init__(self):
        args = sys.argv[1:]
        if len(args) != 4:
            print("Missing some arguments, please check help menu:")
            self.print_help()
        for arg in args:
            arg_split = arg.split('=')
            match arg_split[0]:
                case 'source':
                    self.__set_source(arg_split[1])
                case 'replica':
                    self.__set_replica(arg_split[1])
                case 'log':
                    self.__set_log(arg_split[1])
                case 'timeout':
                    self.__set_timeout(arg_split[1])
                case _:
                    raise Exception(f'Invalid argument | {arg}')
            print(" ")

    def __set_source(self, path: str) -> None:
        """Sets source path to path provided as argument, while checking if path is valid"""
        if self.source is not None:
            raise Exception('Source already set')
        if not os.path.exists(path):
            raise Exception('Source file not found')
        self.source = path

    def __set_replica(self, path: str) -> None:
        """Sets replica path to path provided as argument, while checking if path is valid. If dir doesn't exist and dir can be created at specified path it will do so"""
        if self.replica is not None:
            raise Exception('Replica already set')

        if not os.path.exists(path):
            if os.access(os.path.dirname(path), os.W_OK):
                os.makedirs(path, mode=0o700)
            else:
                raise Exception('Replica dir not found and cant be created')
        self.replica = path

    def __set_log(self, path: str) -> None:
        """Sets log to provided path if path is valid.
        If its not and it can create the file it will do so, else will fail"""
        if self.log is not None:
            raise Exception('LogfilePath already set')
        if not os.path.exists(path):
            if os.access(os.path.dirname(path), os.W_OK):
                os.mknod(path, 0o600)
            else:
                raise Exception('Logfile not found and cant be created')

        self.log = path

    def __set_timeout(self, time: str) -> None:
        try:
            timeout = int(time)
            if timeout <= 0:
                raise Exception()
            self.timeout = timeout
        except:
            raise Exception('Invalid timeout value, needs to be a positive integer')

    def print_help(self):
        print("Please insert arguments in format {parameter}={value}",
              "Possible parameter values: ",
              "     source  > path to source",
              "     replica > path to safe location",
              "     log     > path to preferred log file",
              "     timeout > time in seconds to save by, ex.: 12h32min17s => timeout=45137"
              , sep="\n")
        exit(0)