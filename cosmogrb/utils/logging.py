import coloredlogs, logging

from cosmogrb import cosmogrb_config


coloredlogs.install(
    level=cosmogrb_config['logging']['level'],
    #                    fmt="%(levelname)s:%(message)s"
)

logger = logging.getLogger("cosmogrb")
