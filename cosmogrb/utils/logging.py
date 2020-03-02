import coloredlogs, logging


coloredlogs.install(
    level="INFO",
    #                    fmt="%(levelname)s:%(message)s"
)

logger = logging.getLogger("grbfunk")
