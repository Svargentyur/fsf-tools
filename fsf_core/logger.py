import logging
from rich.logging import RichHandler

log = logging.getLogger('fsf')

def setup_logging(verbose=False, quiet=False):
    if quiet:
        level = logging.WARNING
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )
    
    log.setLevel(level)
