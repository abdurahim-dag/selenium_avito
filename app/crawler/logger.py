import logging


logger = logging.getLogger(__name__)

_ch = logging.StreamHandler()
_ch.setLevel(logging.INFO)
logger.addHandler(_ch)

_ch = logging.FileHandler('avitospider.log', 'w', 'utf-8')
_ch.setLevel(logging.INFO)
logger.addHandler(_ch)