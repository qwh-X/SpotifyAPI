import logging
from logging import Logger

from mdurl import _format

RESET_LOG = True

LEVEL = logging.DEBUG
FILENAME = "log.log"
PRINT_CONSOLE = False

formats = {
    'time': 'rel', # rel | full
    'caller': 'full',
    'level': 'full',
    'msg': 'full'
}

FORMAT_TIME_FULL = '[%(asctime)s | %(relativeCreated)d]'
FORMAT_TIME_REL = '[%(relativeCreated)d]'

FORMAT_CALLER_FULL = '[%(name)s:%(funcName)s:%(lineno)d]'

FORMAT_LEVEL_FULL = '[%(levelname)s]'

FORMAT_MSG_FULL = '%(message)s'

if formats['time'] == 'rel':
    format_time = FORMAT_TIME_REL
elif formats['time'] == 'full':
    format_time = FORMAT_TIME_FULL
else:
    raise ValueError('Invalid format')

if formats['caller'] == 'full':
    format_caller = FORMAT_CALLER_FULL
else:
    raise ValueError('Invalid format')

if formats['level'] == 'full':
    format_level = FORMAT_LEVEL_FULL
else:
    raise ValueError('Invalid format')

if formats['msg'] == 'full':
    format_msg = FORMAT_MSG_FULL
else:
    raise ValueError('Invalid format')

format_ = format_time + format_level + format_caller + ': ' + format_msg

handlers = [ logging.FileHandler(FILENAME) ]

if RESET_LOG:
    with open(FILENAME, 'wb') as f:
        f.write(bytes())

if PRINT_CONSOLE:
    handlers.append(logging.StreamHandler())

logging.basicConfig(
    level=logging.DEBUG,
    format=format_,
    handlers=handlers
)

def get_logger(name) -> Logger:
    return logging.getLogger(name)
