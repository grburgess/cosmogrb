from configya import YAMLConfig

from cosmogrb.utils.package_utils import get_path_of_user_dir

structure = {}
structure["logging"] = dict(level="INFO")
structure["multiprocess"] = dict(n_grb_workers=6, n_universe_workers=6)


class CosmogrbConfig(YAMLConfig):
    def __init__(self):

        super(CosmogrbConfig, self).__init__(
            structure=structure,
            config_path=get_path_of_user_dir(),
            config_name="cosmogrb_config.yml",
        )


cosmogrb_config = CosmogrbConfig()


__all__ = ["cosmogrb_config"]
