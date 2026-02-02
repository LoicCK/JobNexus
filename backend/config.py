from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ft_client_id: str
    ft_client_secret: str
    lba_api_key: str
    wttj_app_id: str
    wttj_api_key: str


@lru_cache()
def get_settings():
    return Settings()
