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
    HnswAlgorithmConfiguration
)

from rag_app.core.clients import get_secret
from rag_app.core.config import settings


def get_index_client() -> SearchIndexClient:

    endpoint = get_secret("search-endpoint")
    api_key = get_secret("azure-search-key")

    return SearchIndexClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(api_key)
    )


def index_exists(
    index_client: SearchIndexClient,
    index_name: str
) -> bool:

    existing_indexes = list(
        index_client.list_indexes()
    )

    return any(
        idx.name == index_name
        for idx in existing_indexes
    )


def create_index_if_not_exists(
    index: SearchIndex
):

    index_client = get_index_client()

    if index_exists(
        index_client=index_client,
        index_name=index.name
    ):
        print(
            f"Index '{index.name}' already exists."
        )
        return

    index_client.create_index(index)

    print(
        f"Index '{index.name}' created."
    )


def build_rag_index_definition() -> SearchIndex:

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
            name="content_hash",
            type=SearchFieldDataType.String,
            filterable=True
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


def build_ingestion_index_definition() -> SearchIndex:

    fields = [

        SimpleField(
            name="hash_id",
            type=SearchFieldDataType.String,
            key=True
        ),

        SimpleField(
            name="file_hash",
            type=SearchFieldDataType.String,
            filterable=True
        ),

        SimpleField(
            name="source",
            type=SearchFieldDataType.String,
            filterable=True
        ),

        SimpleField(
            name="strategy_name",
            type=SearchFieldDataType.String,
            filterable=True
        ),

        SimpleField(
            name="embedding_model",
            type=SearchFieldDataType.String,
            filterable=True
        ),

        SimpleField(
            name="ingested_at",
            type=SearchFieldDataType.String,
            filterable=True
        )
    ]

    return SearchIndex(
        name=settings.azure_search_ingestion_index_name,
        fields=fields
    )

if __name__ == "__main__":

    create_index_if_not_exists(
        build_rag_index_definition()
    )

    create_index_if_not_exists(
        build_ingestion_index_definition()
    )