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

# Simple in-memory secret cache
_secret_cache = {}


def get_secret(name: str) -> str:

    if name not in _secret_cache:
        _secret_cache[name] = (
            secret_client
            .get_secret(name)
            .value
        )

    return _secret_cache[name]


# Client caches
_openai_client = None
_search_clients = {}


def get_openai_client():

    global _openai_client

    if _openai_client is None:

        _openai_client = AzureOpenAI(
            azure_endpoint=get_secret("openai-endpoint"),
            api_key=get_secret("openai-api-key"),
            api_version=settings.azure_openai_api_version,
            timeout=30,
            max_retries=2
        )

    return _openai_client


def get_search_client(
    index_name: str
) -> SearchClient:

    if index_name not in _search_clients:

        _search_clients[index_name] = SearchClient(
            endpoint=get_secret("search-endpoint"),
            index_name=index_name,
            credential=AzureKeyCredential(
                get_secret("azure-search-key")
            ),
            retry_total=2
        )

    return _search_clients[index_name]
