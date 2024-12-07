import datetime
import os

import arguments
from time import sleep
from log import Logger

def copy_file(src: str, dst: str):
    attribute_list = os.stat(src, follow_symlinks=False)
    if os.path.islink(src):
        os.symlink(os.readlink(src), dst)
    else:
        with open(src, "rb") as read_file, open(dst, "wb") as write_file:
            while block := read_file.read(2**16):
                write_file.write(block)
        os.chmod(dst, attribute_list.st_mode, follow_symlinks=False)
        os.utime(dst, (attribute_list.st_atime, attribute_list.st_mtime), follow_symlinks=False)
        formated_time = datetime.datetime.utcfromtimestamp(attribute_list.st_ctime).isoformat().encode()
        os.setxattr(dst, "user.creation_time", formated_time, follow_symlinks=False)

    # this operation can be ran on both links and files.
    # others are only for files and will crash it ran on syslink
    os.chown(dst, attribute_list.st_uid, attribute_list.st_gid, follow_symlinks=False)



def look_thru_replica(replica_root_path: str, source_root_path: str, logger: Logger, path: str = ''):
    """Checks all files on replica and marks deprecated ones for deletion"""
    full_path = os.path.join(replica_root_path, path)

    for file in os.listdir(full_path):
        if os.path.isdir(os.path.join(full_path, file)):
            look_thru_replica(replica_root_path, source_root_path, logger, os.path.join(path, file))

        else:
            if not os.path.exists(os.path.join(source_root_path, path, file)):
                path_to_remove = os.path.join(replica_root_path, path, file)
                os.remove(path_to_remove)
                logger.log(f"DELETE {path_to_remove}")
                continue
            # if last edit times are equal
            if os.path.getmtime(os.path.join(replica_root_path, path, file)) == os.path.getmtime(os.path.join(source_root_path, path, file)):
                continue

def look_thru_source(source_root_path: str, replica_root_path:str, logger: Logger, path: str = ''):
    """Checks all files in source and copies files to replica it hey have not been found"""
    full_path = os.path.join(source_root_path, path)
    for file in os.listdir(full_path):
        if os.path.isdir(os.path.join(full_path, file)):
            if not os.path.exists(os.path.join(replica_root_path, file)) or not os.path.isdir(os.path.join(full_path, file)):
                os.makedirs(os.path.join(replica_root_path, file), exist_ok=True)
                logger.log(f"CREATE dir {os.path.join(replica_root_path, file)}")
            look_thru_source(source_root_path, replica_root_path, logger, os.path.join(path, file))

        elif os.path.islink(os.path.join(full_path, file)):
            if os.path.exists(os.path.join(replica_root_path, file)) and os.path.islink(os.path.join(replica_root_path, file)) and os.readlink(os.path.join(full_path, file)) == os.readlink(os.path.join(replica_root_path, file)):
                continue
            copy_file(os.path.join(full_path, file), os.path.join(replica_root_path, file))
            logger.log(f"LINKING link from {os.path.join(full_path, file)} on {os.readlink(os.path.join(full_path, file))}")
        else:
            if not os.path.exists(os.path.join(replica_root_path, path, file)):
                logger.log(f"COPY file from {os.path.join(full_path, file)} to {os.path.join(replica_root_path, path, file)}")
                copy_file(os.path.join(full_path, file), os.path.join(replica_root_path, path, file))
                continue
            if os.path.getmtime(os.path.join(full_path, file)) == os.path.getmtime(os.path.join(replica_root_path, path, file)):
                continue
            logger.log(f"REPLACE file from {os.path.join(full_path, file)} on {os.path.join(replica_root_path, path, file)}")
            copy_file(os.path.join(full_path, file), os.path.join(replica_root_path, path, file))


def main():
    args = arguments.Arguments()
    logger = Logger(args.log)

    while True:
        look_thru_replica(args.replica, args.source, logger)
        look_thru_source(args.source, args.replica, logger)
        sleep(args.timeout)


if __name__ == '__main__':
    main()