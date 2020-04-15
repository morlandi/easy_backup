import traceback
import socket
import datetime
import os
from . import utils
from .utils import ERRORS_LIST


def mk_title(title):
    return "[%s] %s - %s" % (
        socket.gethostname(),
        datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
        title
    )


def mk_header(started, completed):
    header = "easy_backup v%s - started: %s, completed: %s" % (
        utils.get_version(),
        str(started),
        str(completed),
    )
    return header


def escape(text):
    return text.replace('"', '\"')


def notify_errors(started, command, backup_file_list):

    title = mk_title('*** easy_backup failed with errors ***')
    details = "%s\n\nERRORS:\n" % (
        mk_header(started, datetime.datetime.now()),
    )
    for error in ERRORS_LIST:
        details += error['message'] + "\n"
        details += error['traceback'] + "\n"

    if backup_file_list is not None:
        details += "\n\nAvailable backup files:\n"
        details += backup_file_list

    command = command.format(
        title=escape(title),
        details=escape(details)
    )
    utils.run_command(command, force=True)


def notify_success(started, command, backup_file_list):
    title = mk_title('easy_backup completed with no errors')
    details = "%s\n\nNo errors" % mk_header(started, datetime.datetime.now())

    if backup_file_list is not None:
        details += "\n\nAvailable backup files:\n"
        details += backup_file_list

    command = command.format(
        title=escape(title),
        details=escape(details)
    )
    utils.run_command(command, force=True)
