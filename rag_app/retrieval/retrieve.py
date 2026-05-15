from retrieval.search import vector_search


def retrieve_context(query: str):

    results = vector_search(query)

    formatted_chunks = []

    for doc in results:
        formatted_chunks.append(doc["content"])

    return "\n\n".join(formatted_chunks)