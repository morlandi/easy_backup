import traceback
import socket
import datetime
from . import utils


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


from .utils import RUN_COMMAND_ERRORS

def notify_errors(started, command):

    title = mk_title('*** easy_backup failed with errors ***')
    details = "%s\n\nERRORS:\n" % (
        mk_header(started, datetime.datetime.now()),
    )
    for error in RUN_COMMAND_ERRORS:
        details += error['message'] + "\n"
        details += error['traceback'] + "\n"

    command = command.format(
        title=escape(title),
        details=escape(details)
    )
    utils.run_command(command, force=True)


def notify_success(started, command):
    title = mk_title('easy_backup completed with no errors')
    details = "%s\n\nNo errors" % mk_header(started, datetime.datetime.now())
    command = command.format(
        title=escape(title),
        details=escape(details)
    )
    utils.run_command(command, force=True)
