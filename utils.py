import configargparse


def get_args():
    parser = configargparse.ArgParser(default_config_files=["minechat.ini"])
    parser.add("-c", "--config", is_config_file=True, help="config file path")
    parser.add("--host", help="URL of chat hosting server")
    parser.add("--inport", type=int, help="port to read from")
    parser.add("--outport", type=int, help="port to write to")
    parser.add("--history", help="where to save transcript")

    return parser.parse_args()
