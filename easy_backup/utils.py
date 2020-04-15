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


