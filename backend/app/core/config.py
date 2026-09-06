from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config= SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # ai configs
    openai_api_key: str
    model_name: str
    openai_api_base_url: str
    text_embedding_model_name: str
    
    # database config
    mongo_uri: str
    db_name: str = "prodreach"
    
    
    
app_settings= Settings()