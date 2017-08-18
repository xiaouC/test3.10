import logging
logger = logging.getLogger('cron')

from datetime import date, datetime, timedelta

import gevent
from gevent import event
from fields import *
from util import datetime_ceil, convert_to_datetime, iteritems, time_difference

class CronTrigger(object):
    FIELD_NAMES = ('year', 'month', 'day', 'week', 'day_of_week', 'hour',
                   'minute', 'second')
    FIELDS_MAP = {'year': BaseField,
                  'month': BaseField,
                  'week': WeekField,
                  'day': DayOfMonthField,
                  'day_of_week': DayOfWeekField,
                  'hour': BaseField,
                  'minute': BaseField,
                  'second': BaseField}

    def __init__(self, **values):
        self.start_date = values.pop('start_date', None)
        if self.start_date:
            self.start_date = convert_to_datetime(self.start_date)

        # Check field names and yank out all None valued fields
        for key, value in list(iteritems(values)):
            if key not in self.FIELD_NAMES:
                raise TypeError('Invalid field name: %s' % key)
            if value is None:
                del values[key]

        self.fields = []
        assign_defaults = False
        for field_name in self.FIELD_NAMES:
            if field_name in values:
                exprs = values.pop(field_name)
                is_default = False
                assign_defaults = not values
            elif assign_defaults:
                exprs = DEFAULT_VALUES[field_name]
                is_default = True
            else:
                exprs = '*'
                is_default = True

            field_class = self.FIELDS_MAP[field_name]
            field = field_class(field_name, exprs, is_default)
            self.fields.append(field)

    def _increment_field_value(self, dateval, fieldnum):
        """
        Increments the designated field and resets all less significant fields
        to their minimum values.

        :type dateval: datetime
        :type fieldnum: int
        :type amount: int
        :rtype: tuple
        :return: a tuple containing the new date, and the number of the field
                 that was actually incremented
        """
        i = 0
        values = {}
        while i < len(self.fields):
            field = self.fields[i]
            if not field.REAL:
                if i == fieldnum:
                    fieldnum -= 1
                    i -= 1
                else:
                    i += 1
                continue

            if i < fieldnum:
                values[field.name] = field.get_value(dateval)
                i += 1
            elif i > fieldnum:
                values[field.name] = field.get_min(dateval)
                i += 1
            else:
                value = field.get_value(dateval)
                maxval = field.get_max(dateval)
                if value == maxval:
                    fieldnum -= 1
                    i -= 1
                else:
                    values[field.name] = value + 1
                    i += 1

        return datetime(**values), fieldnum

    def _set_field_value(self, dateval, fieldnum, new_value):
        values = {}
        for i, field in enumerate(self.fields):
            if field.REAL:
                if i < fieldnum:
                    values[field.name] = field.get_value(dateval)
                elif i > fieldnum:
                    values[field.name] = field.get_min(dateval)
                else:
                    values[field.name] = new_value

        return datetime(**values)

    def get_next_fire_time(self, start_date):
        if self.start_date:
            start_date = max(start_date, self.start_date)
        next_date = datetime_ceil(start_date)
        fieldnum = 0
        while 0 <= fieldnum < len(self.fields):
            field = self.fields[fieldnum]
            curr_value = field.get_value(next_date)
            next_value = field.get_next_value(next_date)

            if next_value is None:
                # No valid value was found
                next_date, fieldnum = self._increment_field_value(
                    next_date, fieldnum - 1)
            elif next_value > curr_value:
                # A valid, but higher than the starting value, was found
                if field.REAL:
                    next_date = self._set_field_value(
                        next_date, fieldnum, next_value)
                    fieldnum += 1
                else:
                    next_date, fieldnum = self._increment_field_value(
                        next_date, fieldnum)
            else:
                # A valid value was found, no changes necessary
                fieldnum += 1

        if fieldnum >= 0:
            return next_date

    def __str__(self):
        options = ["%s='%s'" % (f.name, str(f)) for f in self.fields
                   if not f.is_default]
        return 'cron[%s]' % (', '.join(options))

    def __repr__(self):
        options = ["%s='%s'" % (f.name, str(f)) for f in self.fields
                   if not f.is_default]
        if self.start_date:
            options.append("start_date='%s'" % self.start_date.isoformat(' '))
        return '<%s (%s)>' % (self.__class__.__name__, ', '.join(options))

class Job(object):
    def __init__(self, handler, **values):
        self.handler = handler
        self.trigger = CronTrigger(**values)
        self.last_run_time = None
        self.index = -1

    def step(self, now):
        if self.last_run_time==None:
            self.last_run_time = now
        while True:
            next_time = self.trigger.get_next_fire_time(self.last_run_time)
            if next_time > now:
                return next_time
            else:
                logger.info('start run job[%s] %d %s', next_time, self.index, self.handler.__name__)
                try:
                    self.handler()
                except:
                    logger.exception('run job failed')
                self.last_run_time = next_time + timedelta(microseconds=1)

class Scheduler(object):
    def __init__(self, jobs):
        self.jobs = jobs
        self.stopped = False
        self.thread = None

    def run(self):
        try:
            while not self.stopped:
                now = datetime.now()
                logger.info('scheduler step, now:%s', now)
                next_wakeup = None
                for job in self.jobs:
                    tmp = job.step(now)
                    if next_wakeup==None:
                        next_wakeup = tmp
                    else:
                        next_wakeup = min(next_wakeup, tmp)
                sleep_time = time_difference(next_wakeup, now)
                logger.info('scheduler sleep %s', sleep_time)
                gevent.sleep(sleep_time)
        except:
            logger.exception('scheduler stopped')
        else:
            logger.info('scheduler stopped')

    def stop(self):
        self.thread.kill()
        self.thread = None

    def start(self):
        self.thread = gevent.spawn(self.run)

_scheduler = None
def reset_jobs(jobs):
    # set job indexes for logging
    for i, job in enumerate(jobs):
        job.index = i

    logger.info('reset scheduler, jobs:%d', len(jobs))
    global _scheduler
    if _scheduler:
        logger.info('stop old scheduler')
        _scheduler.stop()
        logger.info('old scheduler stopped')
    _scheduler = Scheduler(jobs)
    logger.info('start new scheduler, jobs:%d', len(jobs))
    _scheduler.start()

def scheduler_thread():
    if _scheduler:
        return _scheduler.thread

if __name__ == '__main__':
    def test1():
        print 'run per second'
    def test3():
        print 'run per second[3]'
    def slow_test():
        gevent.sleep(5)
        print 'sleep 5'
    reset_jobs([
        Job(handler=test1),
        Job(handler=test3),
        Job(handler=slow_test, second="*/5"),
    ])
    scheduler_thread().join()
