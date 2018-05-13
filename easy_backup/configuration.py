import sys
import logging

try:
    from configparser import ConfigParser
except:
    from ConfigParser import ConfigParser

try:
    # this raw_input is not converted by 2to3
    term_input = raw_input
except NameError:
    term_input = input

logger = logging.getLogger("easy_backup")


def get_config():
    """
    Returns global configuration as singleton
    """
    return config_singleton


class Configuration(ConfigParser):

    def get_item(self, section, item, default=''):
        """
        Retrieve item from parsed config file
        """
        value = default
        try:
            value = self.get(section, item).strip()
        except:
            logger.debug('Missing config item "%s/%s"; default value "%s" supplied' % (
                section, item, default
            ))
        return value

    def get_item_as_bool(self, section, item, default=False):
        item = self.get_item(section, item, default='False')
        valid = {
            "true": True,
            "y": True,
            "1": True,
            "false": False,
            "n": False,
            "0": False,
        }
        return valid[item.lower()]

    def read_config_file(self, config_filename):
        """
        Parse the config file if exists;
        otherwise, create a default config file and exit
        """
        config = get_config()
        success = len(config.read(config_filename)) > 0
        if success:
            logger.info('Using config file "%s"' % config_filename)
        else:
            # if not found, create a default config file and exit
            if self.query_yes_no('Create default config file "%s" ?' % config_filename):
                self.create_default_config_file(config_filename)
                logger.info('Default config file "%s" has been created; please revise it before running this script again' % config_filename)
            exit(-1)

        return config

    def create_default_config_file(self, config_filename):
        with open(config_filename, 'w') as configfile:
            configfile.write(DEFAULT_CONFIG_FILE)

    def query_yes_no(self, question, default="yes"):
        """Ask a yes/no question via raw_input() and return their answer.

        "question" is a string that is presented to the user.
        "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

        The "answer" return value is True for "yes" or False for "no".
        """
        valid = {"yes": True, "y": True, "ye": True,
                 "no": False, "n": False}
        if default is None:
            prompt = " [y/n] "
        elif default == "yes":
            prompt = " [Y/n] "
        elif default == "no":
            prompt = " [y/N] "
        else:
            raise ValueError("invalid default answer: '%s'" % default)

        while True:
            sys.stdout.write(question + prompt)
            choice = term_input().lower()
            if default is not None and choice == '':
                return valid[default]
            elif choice in valid:
                return valid[choice]
            else:
                sys.stdout.write("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")



config_singleton = Configuration()


DEFAULT_CONFIG_FILE = """

[general]
mount_command=mount.cifs -o user=uXXXXXX,pass=YYYYYYYYYYYYYYYY //uXXXXXX.your-storagebox.de/backup /mnt/backup
umount_command=umount /mnt/backup
mailto=
target_root=/mnt/backup/backups/{hostname}
target_subfolder=./daily

[data_folders]
enabled=False
include_1=/etc
include_2=/home/*/www/
include_3=/home/*/public/media
exclude_1=/home/baduser/public/media

[postgresql]
enabled=True
root_user=postgres
vacuumdb=True
exclude_1=db_wrong_1
exclude_2=db_wrong_2

[mysql]
enabled=False
root_user: root
root_password: f56b7bea8c084d14

[rotation]
enabled=False
daily=./daily
weekly=./weekly
monthly=./monthly
yearly=./yearly
quarantine=./quarantine
"""
