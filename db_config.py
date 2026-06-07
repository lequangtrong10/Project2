from configparser import ConfigParser


def load_config(filename="database.ini", section="postgresql"):
    parser = ConfigParser()
    parser.read(filename)

    config = {}

    if parser.has_section(section):
        for key, value in parser.items(section):
            config[key] = value
    else:
        raise Exception(f"Section {section} not found in {filename}")

    return config
