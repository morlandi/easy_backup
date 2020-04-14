easy_backup
===========

A script to create timestamped backups for local databases and data folders, and optionally rotate previous backups

Installation
------------

::

    pip install git+https://github.com/morlandi/easy_backup


Purposes
--------

- new backup files will be saved into the specified target folder
- an optional "mount" command is executed at the beginning
- an optional "umount" command is executed at the end
- each folder listed in the "data_folders" section is saved in a new .tar.gz archive
- all postgres databases (unless explicitly excluded) are dumped to new .gz archives
- postgresql "vacuumdb" command is optionally applied
- all mysql databases (unless explicitly excluded) are dumped to new .gz archives
- after all new backups have been saved to the "daily" folder, a rotation procedure
  can be applied as further detailed below


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


Config file
-----------

A sample config file "easy_backup.conf" is automatically created on first run.

You should revise it to supply appropriate values.

::

  [general]
  mount_command=mount.cifs -o user=uXXXXXX,pass=YYYYYYYYYYYYYYYY //uXXXXXX.your-storagebox/backup /mnt/backup
  umount_command=umount /mnt/backup
  #on_errors=echo "{details}" | mail -s'{title}' testuser@somewhere.com
  #on_success=echo "{details}" | mail -s'{title}' testuser@somewhere.com
  report_backup_files_list=False
  target_root=/mnt/backup/backups/{hostname}
  target_subfolder=daily

  [run_before]
  enabled=False
  #script_1=...
  #script_2=...

  [run_after]
  enabled=False
  #script_1=...
  #script_2=...

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
  root_password: password

  [rotation]
  enabled=False
  daily=daily
  weekly=weekly
  monthly=monthly
  yearly=yearly
  quarantine=quarantine
  quarantine_max_age=7


File rotation
-------------

When rotation is activated, a specific procedure is run after backup completion,
in order to organize backup files with the following purposes:

- limit the overall disk space used
- provide a significant history depth

Backup files are organized according to the following schema::

    .
    +-- daily       ... most recent files
    +-- weekly      ... files older than one week; only monday and 1-st day of month dated files are preserved
    +-- monthly     ... files older than one month; only 1-st day of month dated files are preserved
    +-- yearly      ... files older than one year and dated 1-st january
    +-- quarantine  ... the files to get rid of

Redundant files are kept in the quarantine folder for 1 month.

The date of each backup file is deducted from the file name.

Recognized formats (examples):

    - "1521766816_2018_03_23_10.5.6-ee_gitlab_backup.tar"
    - "2018-03-24_01.02.57_nexterbox3.media.tar.gz"

