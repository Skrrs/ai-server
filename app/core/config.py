from functools import lru_cache

from pydantic import BaseSettings


class GlobalSettings(BaseSettings):
    ENV_STATE: str
    PROJ_RELOAD: bool
    PORT: int

    class Config:
        env_file = ".env"


class DevSettings(GlobalSettings):
    class Config:
        env_file = "dev.env"


class ProdSettings(GlobalSettings):
    class Config:
        env_file = "prod.env"


class FactorySettings:
    @staticmethod
    def load():
        env_state = GlobalSettings().ENV_STATE
        if env_state == "dev":
            return DevSettings()

        return ProdSettings()


@lru_cache
def conf():
    settings = FactorySettings.load()
    return settings
