from azure.core.credentials import AzureKeyCredential

from azure.search.documents.indexes import SearchIndexClient

from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SearchableField,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
    HnswAlgorithmConfiguration # Azure vector-search algorithm
)

from rag_app.core.clients import get_secret
from rag_app.core.config import settings


def index_exists(index_client, index_name: str) -> bool:

    existing_indexes = list(index_client.list_indexes())

    return any(
        idx.name == index_name
        for idx in existing_indexes
    )


def build_index_definition() -> SearchIndex:

    fields = [

        SimpleField(
            name="chunk_id",
            type=SearchFieldDataType.String,
            key=True
        ),

        SearchableField(
            name="content",
            type=SearchFieldDataType.String
        ),

        SimpleField(
            name="source",
            type=SearchFieldDataType.String,
            filterable=True
        ),

        SimpleField(
            name="title",
            type=SearchFieldDataType.String,
            filterable=True
        ),

        SimpleField(
            name="chunk_index",
            type=SearchFieldDataType.Int32
        ),

        SimpleField(
            name="strategy_name",
            type=SearchFieldDataType.String
        ),

        SearchField(
            name="contentVector",
            type=SearchFieldDataType.Collection(
                SearchFieldDataType.Single
            ),
            searchable=True,
            vector_search_dimensions=settings.embedding_dimensions,
            vector_search_profile_name="vector-profile"
        )
    ]

    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name="hnsw-config"
            )
        ],
        profiles=[
            VectorSearchProfile(
                name="vector-profile",
                algorithm_configuration_name="hnsw-config"
            )
        ]
    )

    return SearchIndex(
        name=settings.azure_search_index_name,
        fields=fields,
        vector_search=vector_search
    )


def create_index_if_not_exists():

    endpoint = get_secret("search-endpoint")
    api_key = get_secret("azure-search-key")

    index_client = SearchIndexClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(api_key)
    )

    if index_exists(
        index_client=index_client,
        index_name=settings.azure_search_index_name
    ):
        print(
            f"Index '{settings.azure_search_index_name}' already exists."
        )
        return

    index = build_index_definition()

    index_client.create_index(index)

    print(
        f"Index '{settings.azure_search_index_name}' created."
    )


if __name__ == "__main__":
    create_index_if_not_exists()