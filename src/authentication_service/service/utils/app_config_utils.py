import json
import os

import yaml

script_path = os.path.dirname(os.path.abspath(__file__))


def get_config_from_file(script_path, logger):
    config_path = os.path.join(script_path, "config.yml")
    http_port = 9090
    if os.path.isfile(config_path):

        with open(config_path, "r") as f:
            config = yaml.load(f.read(), Loader=yaml.Loader)
        http_port = config.get("http_port", 9090)
        log_l = config.get("log_level", "info")

        logger.debug(f"Configuration: {json.dumps(config, indent=4)}")
    else:
        logger.warning("Configuration file not found!")
        log_l = "debug"
    logger.info("Starting v1.0.0")
    return http_port, log_l
