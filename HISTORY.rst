.. :changelog:

History
=======

v1.2.5
------
* use only Ascii chars

v1.2.4
------
* replace graphic lines

v1.2.3
------
* Fix backup files list report

v1.2.2
------
* Better backup file list reporting

v1.2.1
------
* Better error handling when mount fails

v1.2.0
------
* Optionally include a report of available backup files list in notification email
* Collect errors and run backup procedure to complation anyhow

v1.1.2
------
* default config file revised

v1.1.1
------
* add started and completed datetime to notification massages

v1.1.0
------
* always raise exception on command failure
* optionally send notifications after failure and/or success
* fail silently on mount failure

v1.0.8
------
* update default config file
* "enabled" item atted to "run_before" and "run_after" sections

v1.0.7
------
* force mount/umount even during dry-run

v1.0.6
------
* print python version

v1.0.5
------
* consider dry_run flag
* "run before" and "run after" scripts

v1.0.4
------
* set default value of "quarantine_max_age" to 7

v1.0.3
------
* configurable "quarantine_max_age"

v1.0.0
------
* Initial script
