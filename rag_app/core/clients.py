from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

from openai import AzureOpenAI

from rag_app.core.config import settings


# Key Vault
credential = DefaultAzureCredential()

secret_client = SecretClient(
    vault_url=settings.key_vault_url,
    credential=credential
)

# simple in-memory cache
_secret_cache = {}

def get_secret(name: str) -> str:
    if name not in _secret_cache:
        _secret_cache[name] = secret_client.get_secret(name).value
    return _secret_cache[name]

# Retrieve secrets (start FastAPI even if KV is temporarily slow)
azure_openai_api_key = get_secret("openai-api-key")
azure_search_key = get_secret("azure-search-key")
openai_endpoint = get_secret("openai-endpoint")
search_endpoint = get_secret("search-endpoint")


# Azure OpenAI Client
openai_client = AzureOpenAI(
    azure_endpoint=openai_endpoint,
    api_key=azure_openai_api_key,
    api_version=settings.azure_openai_api_version
)


# Azure AI Search Client
search_client = SearchClient(
    endpoint=search_endpoint, # taken from KeyVault
    index_name=settings.azure_search_index_name, # taken from .env (via rag_app.core.config.settings)
    credential=AzureKeyCredential(azure_search_key)
)