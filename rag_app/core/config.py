from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # src-data (mini-example)
    data_directory: str = "data/hobbit"

    # Azure OpenAI
    azure_openai_api_version: str = "2024-02-01"

    azure_openai_chat_deployment: str
    azure_openai_embedding_deployment: str
    embedding_dimensions: int = 1536 # text-embedding-3-small default dimensions
    embedding_batch_size: int = 1 # using cheapest tier of embedding model (6 requests/min limit)

    # Azure AI Search
    azure_search_index_name: str # one srtoring chunks
    azure_search_ingestion_index_name : str # one storing deterministic-hashes for ingested chubks (deduplication)

    # Key Vault
    key_vault_url: str

    # Retrieval settings
    top_k_retrieval: int = 5

    # Generation settings
    temperature: float = 0.3

    # Chunking settings
    chunk_size: int = 500
    chunk_overlap: int = 50

    # Pydantic Settings Config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )



settings = Settings()