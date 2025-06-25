
class YamlValidationException(Exception):
    missing: list[str] = None
    def __init__(self, missing: list[str] = None):
        self.missing = missing if missing is not None else []
