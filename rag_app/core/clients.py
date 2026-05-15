from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

from openai import AzureOpenAI

from core.config import settings


#
# Key Vault
#

credential = DefaultAzureCredential()

secret_client = SecretClient(
    vault_url=settings.key_vault_url,
    credential=credential
)


#
# Retrieve secrets
#

azure_openai_api_key = secret_client.get_secret(
    "azure-openai-api-key"
).value

azure_search_key = secret_client.get_secret(
    "azure-search-key"
).value


#
# Azure OpenAI Client
#

openai_client = AzureOpenAI(
    azure_endpoint=settings.azure_openai_endpoint,
    api_key=azure_openai_api_key,
    api_version=settings.azure_openai_api_version
)


#
# Azure AI Search Client
#

search_client = SearchClient(
    endpoint=settings.azure_search_endpoint,
    index_name=settings.azure_search_index_name,
    credential=AzureKeyCredential(azure_search_key)
)