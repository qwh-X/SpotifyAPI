import logging
from logging import Logger

RESET_LOG = True

LEVEL = logging.DEBUG
FILENAME = "log.log"
PRINT_CONSOLE = False

formats = {
        'time': 'rel', # rel | full
}

FORMAT_TIME_FULL = '%(asctime)s | %(relativeCreated)d'
FORMAT_TIME_REL = '%(relativeCreated)d'

if formats['time'] == 'rel':
    format_time = FORMAT_TIME_REL
elif formats['time'] == 'full':
    format_time = FORMAT_TIME_FULL
else:
    raise ValueError('Invalid format')

handlers = [ logging.FileHandler(FILENAME) ]

if RESET_LOG:
    with open(FILENAME, 'wb') as f:
        f.write(bytes())

if PRINT_CONSOLE:
    handlers.append(logging.StreamHandler())

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s|%(relativeCreated)d][%(name)s:%(funcName)s:%(lineno)d][%(levelname)s]: %(message)s',
    handlers=handlers
)

def get_logger(name) -> Logger:
    return logging.getLogger(name)
