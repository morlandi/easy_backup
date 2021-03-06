# -*- coding: utf-8 -*-
import os
import sys
import logging
import datetime
import time
import socket
import platform
import traceback
from .args import get_args
from .configuration import get_config

logger = logging.getLogger("easy_backup")

ERRORS_LIST = []


def run_command(command, force=False, fail_silently=True):
    try:
        do_run_command(command, force=force)
    except Exception as e:
        if fail_silently:
            ERRORS_LIST.append({
                'message': str(e),
                'traceback': traceback.format_exc(),
            })
        else:
            raise
    return


def do_run_command(command, force=False):
    #interactive = not args.quiet
    if get_args().dry_run and not force:
        sys.stderr.write("\x1b[1;37;40m" + command + "\x1b[0m\n")
    else:
        # if interactive and not query_yes_no("Proceed ?"):
        #     raise Exception("Interrupted by user")
        logger.debug('Run command: "' + command + '"')
        rc = os.system(command)
        if rc != 0:
            message = 'COMMAND FAILED: "' + command + '"'
            logger.error(message)
            raise Exception(message)
    return


def setup_logger(logger, verbosity):
    """
    Set logger level based on verbosity option
    """
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s|easy_backup|%(levelname)s| %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if verbosity == 0:
        logger.setLevel(logging.WARN)
    elif verbosity == 1:  # default
        logger.setLevel(logging.INFO)
    elif verbosity > 1:
        logger.setLevel(logging.DEBUG)

    # verbosity 3: also enable all logging statements that reach the root logger
    if verbosity > 2:
        logging.getLogger().setLevel(logging.DEBUG)


def get_version():
    try:
        import easy_backup
        version = easy_backup.__version__
        version += " (python: %s)" % platform.python_version()
        return version
    except:
        return '???'


def mount(fail_silently):
    command = get_config().get_item('general', 'mount_command')
    if command:
        return run_command(command, force=True, fail_silently=fail_silently)
    return True


def umount(fail_silently):
    command = get_config().get_item('general', 'umount_command')
    if command:
        return run_command(command, force=True, fail_silently=fail_silently)
    return True


################################################################################

def timestamp():
    """
    Return localtime
    """
    def datetime_from_utc_to_local(utc_datetime):
        now_timestamp = time.time()
        offset = datetime.datetime.fromtimestamp(now_timestamp) - datetime.datetime.utcfromtimestamp(now_timestamp)
        return utc_datetime + offset

    #t = datetime_from_utc_to_local(datetime.now())
    t = datetime.datetime.now()
    return t


def timestamp_to_string(timestamp):
    return timestamp.strftime('%Y-%m-%d_%H-%M-%S')


def assure_path_exists(path):
    if not os.path.isdir(path):
        logger.info('Creating path "%s"' % path)
        os.makedirs(path)
        if not os.path.isdir(path):
            logger.error('Unable to create path "%s"' % path)
            return False
    return True


def get_target_folder(include_target_subfolder):
    config = get_config()
    if include_target_subfolder:
        folder = os.path.abspath(os.path.join(
            config.get_item('general', 'target_root'),
            config.get_item('general', 'target_subfolder'),
        ))
    else:
        folder = os.path.abspath(
            config.get_item('general', 'target_root')
        )
    while "{hostname}" in folder:
        folder = folder.replace("{hostname}", socket.gethostname())
    return folder


def output_filepath(target_folder, timestamp, filename):
    """
    Returns <target_folder>/TIMESTAMP__filename
    """
    return os.path.join(
        target_folder,
        '%s__%s' % (timestamp_to_string(timestamp), filename),
    )


def sizeof_fmt(num, suffix='B'):
    """Readable file size
    :param num: Bytes value
    :type num: int
    :param suffix: Unit suffix (optionnal) default = B
    :type suffix: str
    :rtype: str
    """
    for unit in ['', 'k', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def dump_backup_files(target_folder, daily, weekly, monthly, yearly, quarantine):

    def list_files(root, file_prefix, buffer):
        """
        - list files in "root" folder
        - appand the sorted list of files into buffer[]
        - returns (num_files, total_size_in_bytes)
        """
        files = sorted(os.listdir(root))
        n = len(files)
        total_size_in_bytes = 0
        for i, file in enumerate(files):
            #prefix = file_prefix + ("├── " if (i < n - 1) else "└── ")
            prefix = file_prefix + "+-- "
            file_size = os.path.getsize(os.path.join(root, file))
            total_size_in_bytes += file_size
            line = "%s%s (%s)" % (prefix, file, sizeof_fmt(file_size))
            buffer.append(line)
        return n, total_size_in_bytes

    buffer = []
    path_parts = target_folder.rsplit(os.path.sep, 1)
    buffer.append("[%s]" % (path_parts[-1],))

    files_counter = 0
    total_size = 0

    for i, subfolder in enumerate([daily, weekly, monthly, yearly, quarantine, ]):
        #prefix = " ├──" if i < 4 else " └──"
        prefix = " +--"
        #file_prefix = " │   " if i < 4 else "     "
        file_prefix = " |   " if i < 4 else "     "
        buffer.append("%s[%s]" % (prefix, subfolder))
        n, s = list_files(os.path.join(target_folder, subfolder), file_prefix, buffer)
        files_counter += n
        total_size += s
    buffer.append('Files: %d' % files_counter)
    buffer.append('Size: %s' % sizeof_fmt(total_size))

    text = "\n".join(buffer)
    return text


