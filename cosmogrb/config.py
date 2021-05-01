import os
import warnings
from dataclasses import dataclass
from pathlib import Path

from omegaconf import OmegaConf

_config_path = Path("~/.config/cosomogrb/").expanduser()

_config_name = Path("cosmogrb_config.yml")

_config_file = _config_path / _config_name


# Define structure with dataclasses
@dataclass
class LogConsole:

    on: bool = True
    level: str = "WARNING"


@dataclass
class LogFile:

    on: bool = True
    level: str = "WARNING"


@dataclass
class Logging:

    debug: bool = False
    level: str = "INFO"
    console: LogConsole = LogConsole()
    file: LogFile = LogFile()


@dataclass
class MultiProcess:
    n_grb_workers: int = 6
    n_universe_workers = 6


@dataclass
class Orbit:
    default_time: float = 0.0
    use_random_time: bool = True


@dataclass
class GBM:

    orbit: Orbit = Orbit()


@dataclass
class CosmogrbConfig:

    logging: Logging = Logging()
    gbm: GBM = GBM()
    multiprocess: MultiProcess = MultiProcess()


# Read the default config
cosmogrb_config: CosmogrbConfig = OmegaConf.structured(CosmogrbConfig)

# Merge with local config
if _config_file.is_file():

    _local_config = OmegaConf.load(_config_file)

    cosmogrb_config: CosmogrbConfig = OmegaConf.merge(cosmogrb_config, _local_config)

# Write defaults
else:

    # Make directory if needed
    _config_path.mkdir(parents=True, exist_ok=True)

    with _config_file.open("w") as f:

        OmegaConf.save(config=cosmogrb_config, f=f.name)


__all__ = ["cosmogrb_config"]
