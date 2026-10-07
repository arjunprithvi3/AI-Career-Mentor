import json
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from rag.ingestion import create_embeddings

RESOURCE_DIRECTORY = Path("uploads/resources")
FAISS_INDEX_PATH = "vector_stores/resource_collection"


def load_resource_documents() -> list[Document]:

    documents = []
    for file_path in RESOURCE_DIRECTORY.glob("*.json"):
        with open(file_path, "r", encoding="utf-8") as file:
            resources = json.load(file)
        for resource in resources:
            page_content = (
                f"Skill: {resource['skill']}\n"
                f"Title: {resource['title']}\n"
                f"Provider: {resource['provider']}\n"
                f"Type: {resource['resource_type']}\n"
                f"Level: {resource['level']}\n"
                f"URL: {resource['url']}\n"
                f"Description: "
                f"{resource['description']}"
            )
            documents.append(
                Document(
                    page_content=page_content,
                    metadata={
                        "resource_id": resource["resource_id"],
                        "skill": resource["skill"],
                        "title": resource["title"],
                        "provider": resource["provider"],
                        "resource_type": resource["resource_type"],
                        "level": resource["level"],
                        "url": resource["url"],
                        "source_file": file_path.name,
                    },
                )
            )
    return documents


def build_vector_store(documents: list[Document]) -> int:

    embeddings = create_embeddings()
    vector_store = FAISS.from_documents(documents=documents, embedding=embeddings)
    vector_store.save_local(FAISS_INDEX_PATH)
    return len(documents)


def load_vector_store():

    embeddings = create_embeddings()
    return FAISS.load_local(
        FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True
    )


def get_resource_retriever(k: int = 5):

    vector_store = load_vector_store()
    return vector_store.as_retriever(search_kwargs={"k": k})
