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


def escape(text):
    return text.replace('"', '\"')


def notify_errors(command, e):

    title = mk_title('*** easy_backup failed with errors ***')
    details = "ERROR: %s\n\n%s" % (str(e), traceback.format_exc())
    command = command.format(
        title=escape(title),
        details=escape(details)
    )
    utils.run_command(command)


def notify_success(command):
    title = mk_title('easy_backup completed with no errors')
    command = command.format(
        title=escape(title),
        details=escape(title)
    )
    utils.run_command(command)
