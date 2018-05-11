easy_backup
===========

A script to create timestamped backups for local databases and data folders, and optionally rotate previous backups

Installation
------------

::

    pip install git+https://github.com/morlandi/easy_backup


Sample usage
------------

::

    usage: easy_backup [-h] [-c config_filename] [-v {0,1,2,3}] [--dry-run] [--version]

    Creates timestamped backups for local databases and data folders, and optionally rotate previous backups

    optional arguments:
      -h, --help            show this help message and exit
      -c config_filename, --config config_filename
                            config. filename (default = "./easy_backup.conf")
      -v {0,1,2,3}, --verbosity {0,1,2,3}
                            Verbosity level. (default: 2)
      --dry-run, -d         simulate actions
      --version             show program's version number and exit



rotate_files
------------


This utility script is used to organize backup files with the following purposes:

- limit the overall disk space used
- provide a significant history depth

New backup files should be added to the './daily' folder before executing the script.

Backup files are organized according to the following schema::

    .
    +-- daily       ... most recent files
    +-- weekly      ... files older than one week; only monday and dated 1-st day of month are preserved
    +-- monthly     ... files older than one month (dated 1-st day of month)
    +-- yearly      ... files older than one year and date 1-st january
    +-- quarantine  ... the files to get rid of

Redundant files are kept in the quarantine folder for 1 month.

The date of each backup file is deducted from the file name.

Recognized formats (examples):

    - "1521766816_2018_03_23_10.5.6-ee_gitlab_backup.tar"
    - "2018-03-24_01.02.57_nexterbox3.media.tar.gz"

