import re
from datetime import date, datetime, time
from django.conf import settings

TIMESTAMP_FORMAT = getattr(settings, 'TIMESTAMP_FORMAT', 'ISO 8601')

date_patt = r'(\d{4})-(\d{1,2})-(\d{1,2})'
time_patt = r'(\d{2}):(\d{1,2}):(\d{1,2})(?:.(\d+))?'
date_re = re.compile(date_patt)
time_re = re.compile(time_patt)
datetime_re = re.compile(r'(?:\s|T)'.join([date_patt, time_patt]))

def from_iso8601(timestamp):
    try:
        d, t = timestamp.split('T')
    except ValueError:
        if date_re.match(timestamp):
            args = [int(a) for a in date_re.match(timestamp).groups()]
            return date(*args)
        if time_re.match(timestamp):
            args = [int(a) for a in time_re.match(timestamp).groups()]
            return time(*args)
        return timestamp
    date_args = date_re.match(d).groups()
    time_args = time_re.match(t).groups()
    h, m, s = timestamp.split(':')
    args = [int(a) for a in (date_args + time_args)]
    return datetime(*args)
    
timestamp_formats = {
    'ISO 8601': (lambda dt: dt.isoformat(), from_iso8601)
}

def to_timestamp(dt):
    return timestamp_formats[TIMESTAMP_FORMAT][0](dt)

def from_timestamp(timestamp):
    return timestamp_formats[TIMESTAMP_FORMAT][1](timestamp)
