#!/usr/bin/env python
from __future__ import print_function
"""
(c) 2018 Mario Orlandi, Brainstorm S.n.c.
"""
import sys
import os
import logging
import argparse
import glob
import subprocess

from .args import get_args, set_args
from .configuration import get_config
from .rotate_files import rotate_all
from . import utils


logger = logging.getLogger("easy_backup")

################################################################################

def backup_data_folders(timestamp, target_folder):

    logger.info('*** backup_data_folders() begin ...')

    #
    # Collect source folders
    #

    include_patterns = [value for key, value in get_config().items("data_folders") if key.startswith('include_')]
    exclude_patterns = [value for key, value in get_config().items("data_folders") if key.startswith('exclude_')]

    logger.debug('include_patterns: %s' % str(include_patterns))
    logger.debug('exclude_patterns: %s' % str(exclude_patterns))

    excluded_folders = []
    for p in exclude_patterns:
        excluded_folders += glob.glob(p)

    # remove duplicates
    excluded_folders = [x for x in set(excluded_folders)]

    included_folders = []
    for p in include_patterns:
        for f in glob.glob(p):
            if f not in included_folders and f not in excluded_folders:
                included_folders.append(f)

    included_folders.sort()

    for folder in included_folders:
        logger.debug('data folder: "%s"' % folder)

    #
    # Backup folders
    #

    for folder in included_folders:

        target_file = utils.output_filepath(target_folder, timestamp,
            folder.replace('/', '.').strip('.').lower()
        ) + '.tgz'
        logger.info('Backing up data folder "%s"' % folder)
        logger.debug('Target file: "%s"' % target_file)

        # split folder into parent_folder + subfolder;
        # Example:
        #   '/Users/morlandi/Downloads/tmp/user/due/' --> ['/Users/morlandi/Downloads/tmp/user', 'due']
        # but also:
        #   '/etc/' --> ['/', 'etc']
        path = folder.strip(os.sep)
        parent_folder = os.sep
        n = path.rfind(os.sep)
        if n >= 0:
            parent_folder += path[:n]
        subfolder = path[n+1:]

        # backup with tar; -h option = follow links
        command = 'tar chz -C %s -f %s %s' % (parent_folder, target_file, subfolder)
        utils.run_command(command)

    logger.info('*** backup_data_folders() end')

################################################################################

def backup_postgresql_databases(timestamp, target_folder):

    def build_postgresql_command(command):
        command = 'sudo -u %s %s' % (
            get_config().get_item('postgresql', 'root_user'),
            command,
        )
        return str(command)

    def list_postgresql_databases():
        try:
            #command = 'sudo -u %s psql -c "SELECT datname FROM pg_database" 2>/dev/null | sed -n 3,/\eof/p | grep -v "rows)"' % POSTGRESQL_USER
            #command = 'sudo -u %s psql -c "SELECT datname FROM pg_database"' % POSTGRESQL_USER
            command = build_postgresql_command('psql')
            output = subprocess.check_output(command.split() + ['-c', "SELECT datname FROM pg_database"])
            logger.debug(output)
            # sample output:
            # '  datname  \n-----------\n template1\n template0\n postgres\n(3 rows)\n\n'
            names = [str(name.decode("utf-8")) for name in output.split()]
            databases = [
                name for name in names
                if name != 'datname' and '---' not in name and '(' not in name and ')' not in name
            ]
        except:
            databases = []
        if len(databases) <= 0:
            logger.error('empty database list')
        return databases

    logger.info('*** backup_postgresql_databases() begin ...')

    # list databases
    databases = list_postgresql_databases()
    excluded = [value for key, value in get_config().items("postgresql") if key.startswith('exclude_')]
    databases = [d for d in databases if d not in excluded]

    # dump databases
    dump_command = build_postgresql_command('pg_dump')
    vacuum_command = build_postgresql_command('vacuumdb -z')
    for database in databases:

        logger.debug(database)

        # es: "/target_path/2017-01-01_01-01-01__postgresql.demo1.gz"
        target_file = utils.output_filepath(
            target_folder,
            timestamp,
            'postgresql.' + database.lower() + '.gz'
        )
        logger.info('Backing up postgresql database "%s"' % database)
        logger.debug('Target file: "%s"' % target_file)

        command = '%s %s | gzip > "%s"' % (dump_command, database, target_file)
        utils.run_command(command)
        # vacuum
        if get_config().get_item_as_bool('postgresql', 'vacuumdb'):
            utils.run_command('%s %s' % (vacuum_command, database))

    logger.info('*** backup_postgresql_databases() end')

################################################################################

def backup_mysql_databases(timestamp, target_folder):

    def build_mysql_command(command):
        command = '%s --host localhost --user %s --password="%s"' % (
            command,
            get_config().get_item('mysql', 'root_user'),
            get_config().get_item('mysql', 'root_password'),
        )
        return str(command)

    def list_mysql_databases():
        try:
            mysql_command = build_mysql_command('mysql')
            output = subprocess.check_output(mysql_command.split() + ['-e', "show databases"])
            logger.debug(output)
            # sample output:
            # 'Database\ninformation_schema\ndemo1\ndemo2\nmysql\nperformance_schema\nsys\n'
            databases = output.split()[1:]
        except:
            databases = []
        if len(databases) <= 0:
            logger.error('empty database list')
        return databases

    logger.info('*** backup_mysql_databases() begin ...')

    # list databases
    databases = list_mysql_databases()
    excluded = [value for key, value in get_config().items("mysql") if key.startswith('exclude_')]
    databases = [d for d in databases if d not in excluded]

    # dump databases
    dump_command = build_mysql_command('mysqldump')
    for database in databases:

        logger.debug(database)

        # es: "/target_path/2017-01-01_01-01-01__mysql.demo1.gz"
        target_file = utils.output_filepath(
            target_folder,
            timestamp,
            'mysql.' + database.lower() + '.gz'
        )

        logger.info('Backing up mysql database "%s"' % database)
        logger.debug('Target file: "%s"' % target_file)

        command = '%s %s | gzip > "%s"' % (dump_command, database, target_file)
        utils.run_command(command)

    logger.info('*** backup_mysql_databases() end')

################################################################################

def rotate_backups():
    logger.info('*** rotate_backups() begin ...')
    rotate_all(
        target_folder=utils.get_target_folder(include_target_subfolder=False),
        daily=get_config().get_item('rotation', 'daily'),
        weekly=get_config().get_item('rotation', 'weekly'),
        monthly=get_config().get_item('rotation', 'monthly'),
        yearly=get_config().get_item('rotation', 'yearly'),
        quarantine=get_config().get_item('rotation', 'quarantine'),
    )
    logger.info('*** rotate_backups() end')

################################################################################

class CommandLineParser(argparse.ArgumentParser):

    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


def main():

    #
    # Parse command line
    #

    #default_config_filename = './%s%sconf' % (os.path.splitext(os.path.basename(__file__))[0], os.path.extsep)
    default_config_filename = './easy_backup.conf'

    # See: https://docs.python.org/2/library/argparse.html
    parser = CommandLineParser(
        description='Creates a timestamped backups for local databases and data folders, and optionally rotate previous backups',
        formatter_class=argparse.RawTextHelpFormatter,
#         epilog="""Examples:
# """,
    )
    parser.add_argument('-c', '--config', metavar='config_filename', default=default_config_filename,
        help="config. filename (default = \"%s\")" % default_config_filename)
    parser.add_argument('-v', '--verbosity', type=int, choices=[0, 1, 2, 3], default=1, help="Verbosity level. (default: 2)")
    parser.add_argument('--dry-run', '-d', action='store_true', help="simulate actions")
    parser.add_argument('--version', action='version', version='%(prog)s ' + utils.get_version())

    set_args(parser.parse_args())
    args = get_args()

    # Setup logger
    utils.setup_logger(logger, args.verbosity)
    logger.info("")

    # Read config. file
    config_filename = os.path.abspath(args.config.strip())
    get_config().read_config_file(config_filename)

    utils.umount()
    if not utils.mount(args):
        utils.fail('Unable to mount')

    # Retrieve timestamp and target folder
    timestamp = utils.timestamp()
    logger.info('Timestamp: "%s"' % utils.timestamp_to_string(timestamp))
    target_folder = utils.get_target_folder(include_target_subfolder=True)
    if not utils.assure_path_exists(target_folder):
        utils.fail('Target folder "%s" not found' % target_folder)
    logger.info('Target folder: "%s"' % target_folder)

    if get_config().get_item_as_bool('data_folders', 'enabled', False):
        backup_data_folders(timestamp, target_folder)

    if get_config().get_item_as_bool('postgresql', 'enabled', False):
        backup_postgresql_databases(timestamp, target_folder)

    if get_config().get_item_as_bool('mysql', 'enabled', False):
        backup_mysql_databases(timestamp, target_folder)

    if get_config().get_item_as_bool('rotation', 'enabled', False):
        rotate_backups()

    utils.umount()


if __name__ == "__main__":
    main()

