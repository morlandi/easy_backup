
import os
import logging
import datetime
import sys

logger = logging.getLogger("easy_backup")


class DatedFile(object):

    filename = None
    filedate = None
    age = None

    def __init__(self, filename):
        self.filename = filename
        self.parse_filedate()
        if self.filedate is not None:
            self.age = (datetime.date.today() - self.filedate).days

    def parse_filedate(self):
        if self.filedate is None:
            # try "2018-03-22_..."
            try:
                self.filedate = datetime.datetime.strptime(self.filename[:10], "%Y-%m-%d").date()
            except:
                pass
        if self.filedate is None:
            # try "1521766816_2018_03_23_..."
            try:
                n = self.filename.find('_')
                self.filedate = datetime.datetime.strptime(self.filename[n+1:n+1+10], "%Y_%m_%d").date()
            except:
                pass

    def __str__(self):
        if self.filedate is None:
            return self.filename
        return '%s [dated:%s, age=%d, fdow=%d, fdom=%d, fdoy=%d]' % (
            self.filename,
            self.filedate,
            int(self.age),
            int(self.fdow),
            int(self.fdom),
            int(self.fdoy),
        )

    def is_dated(self):
        return self.filedate is not None

    @property
    def fdow(self):
        """
        First day of week ?
        """
        if self.filedate is None:
            return False
        return self.filedate.weekday() == 0

    @property
    def fdom(self):
        """
        First day of month ?
        """
        if self.filedate is None:
            return False
        return self.filedate.day == 1

    @property
    def fdoy(self):
        """
        First day of year ?
        """
        if self.filedate is None:
            return False
        return self.filedate.month == 1 and self.filedate.day == 1

    def dry_run_message(self, message):
        sys.stderr.write("\x1b[1;37;40m" + message + "\x1b[0m\n")

    def move_to(self, source_folder, target_folder, dry_run):
        """
        Move dated file from source to target folder
        """
        assert(self.is_dated())
        message = 'Moving file "%s" from "%s" to "%s"' % (self.filename, source_folder, target_folder)
        if dry_run:
            self.dry_run_message(message)
        else:
            logger.info('File "%s" ...' % self.filename)
            logger.debug(message)
            os.rename(os.path.join(source_folder, self.filename), os.path.join(target_folder, self.filename))

    def to_quarantine(self, source_folder, quarantine_folder, dry_run):
        """
        Move dated file to quarantine.
        Target filename will be prepended with current date,
        so we always know when this happened.

        If no quarantine folder has been configured, just delete the file.
        """
        assert(self.is_dated())
        if quarantine_folder:
            target_filename = "%s_____%s" % (datetime.date.today().strftime('%Y-%m-%d'), self.filename)
            message = 'Moving file "%s" from "%s" to "%s"' % (self.filename, source_folder, quarantine_folder)
            if dry_run:
                self.dry_run_message(message)
            else:
                logger.info('File "%s" ...' % self.filename)
                logger.debug(message)
                os.rename(os.path.join(source_folder, self.filename), os.path.join(quarantine_folder, target_filename))
        else:
            self.destroy(source_folder, dry_run)

    def destroy(self, source_folder, dry_run):
        """
        Remove the file.
        """
        message = 'Erasing file "%s" from "%s"' % (self.filename, source_folder)
        if dry_run:
            self.dry_run_message(message)
        else:
            logger.info(message)
            os.unlink(os.path.join(source_folder, self.filename))


def collect_dated_files(source_folder, min_age):
    """
    """
    files = []
    filenames = os.listdir(source_folder)
    for filename in filenames:
        file_obj = DatedFile(filename)
        if file_obj.is_dated() and file_obj.age >= min_age:
            files.append(file_obj)
    return files


def rotate_daily(DAILY, WEEKLY, QUARANTINE, dry_run):
    logger.info('* Rotating daily files ...')
    files = collect_dated_files(DAILY, 7)
    errors = 0
    for file_obj in files:
        logger.debug(file_obj)
        try:
            if file_obj.fdow or file_obj.fdom:
                file_obj.move_to(DAILY, WEEKLY, dry_run)
            else:
                file_obj.to_quarantine(DAILY, QUARANTINE, dry_run)
        except Exception as e:
            logger.error(str(e), exc_info=True)
            errors += 1
    return errors


def rotate_weekly(WEEKLY, MONTHLY, QUARANTINE, dry_run):
    logger.info('* Rotating weekly files ...')
    files = collect_dated_files(WEEKLY, 31)
    errors = 0
    for file_obj in files:
        logger.debug(file_obj)
        try:
            if file_obj.fdom:
                file_obj.move_to(WEEKLY, MONTHLY, dry_run)
            else:
                file_obj.to_quarantine(WEEKLY, QUARANTINE, dry_run)
        except Exception as e:
            logger.error(str(e), exc_info=True)
            errors += 1
    return errors


def rotate_monthly(MONTHLY, YEARLY, QUARANTINE, dry_run):
    logger.info('* Rotating monthly files ...')
    files = collect_dated_files(MONTHLY, 365)
    errors = 0
    for file_obj in files:
        logger.debug(file_obj)
        try:
            if file_obj.fdoy:
                file_obj.move_to(MONTHLY, YEARLY, dry_run)
            else:
                file_obj.to_quarantine(MONTHLY, QUARANTINE, dry_run)
        except Exception as e:
            logger.error(str(e), exc_info=True)
            errors += 1
    return errors


def cleanup_quarantine(QUARANTINE, quarantine_max_age, dry_run):
    if QUARANTINE:
        logger.info('* Cleanup quarantine ... (max age: %d)' % quarantine_max_age)
        files = collect_dated_files(QUARANTINE, quarantine_max_age)
        for file in files:
            file.destroy(QUARANTINE, dry_run)


def rotate_all(target_folder, daily, weekly, monthly, yearly, quarantine, quarantine_max_age, dry_run):

    # remember cwd
    original_cwd = os.getcwd()

    errors = 0
    try:
        logger.info('File rotation started')

        # Select target_folder as cwd
        os.chdir(target_folder)

        # We want to be extra sure we've moved successfully to the target folder,
        # to avoid moving files to a wrong place
        if os.getcwd() != target_folder:
            raise Exception('Unable to select "%s" as cwd' % target_folder)
        logger.debug('cwd set to: "%s"' % os.getcwd())

        # Create working folders
        if os.path.exists(daily):
            for folder in [weekly, monthly, yearly, quarantine, ]:
                if not os.path.exists(folder):
                    logger.info('Creating folder "%s"' % folder)
                    os.makedirs(folder)
        else:
            raise Exception('Daily folder "%s" not found in "%s"' % (daily, target_folder))

        # Rotate files
        errors += rotate_daily(daily, weekly, quarantine, dry_run)
        errors += rotate_weekly(weekly, monthly, quarantine, dry_run)
        errors += rotate_monthly(monthly, yearly, quarantine, dry_run)

        cleanup_quarantine(quarantine, quarantine_max_age, dry_run)

    except Exception as e:
        logger.error(str(e), exc_info=True)
        errors += 1
    finally:
        os.chdir(original_cwd)
        logger.debug('cwd set to: "%s"' % os.getcwd())
        logger.info('File rotation completed ' + ('successfully' if errors <= 0 else 'with errors'))

    return errors
