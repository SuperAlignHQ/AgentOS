

class ConfigRepo:
    _instance = None

    def __init__(self) -> None:
        if ConfigRepo._instance is not None:
            raise Exception("Repositories can't be initialized out of service class")

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()

        return cls._instance
