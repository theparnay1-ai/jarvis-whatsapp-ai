import chromadb
from sentence_transformers import SentenceTransformer
from database import SessionLocal, Knowledge

model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("knowledge")


def add_knowledge(business_id, title, content):
    db = SessionLocal()
    item = Knowledge(business_id=business_id, title=title, content=content)
    db.add(item)
    db.commit()
    db.refresh(item)
    db.close()

    collection.add(
        ids=[str(item.id)],
        documents=[content],
        metadatas=[{"business_id": business_id, "title": title}]
    )
    return item


def search_knowledge(business_id, query, limit=3):
    results = collection.query(
        query_embeddings=[model.encode(query).tolist()],
        n_results=10,
        include=["documents", "distances", "metadatas"]
    )

    if not results["documents"]:
        return []

    return [
        doc for doc, distance, meta in zip(
            results["documents"][0],
            results["distances"][0],
            results["metadatas"][0]
        )
        if meta.get("business_id") == business_id and distance < 1.0
    ][:limit]
def update_knowledge(business_id, knowledge_id, title, content):
    db = SessionLocal()
    item = db.query(Knowledge).filter(
        Knowledge.id == knowledge_id,
        Knowledge.business_id == business_id
    ).first()

    if not item:
        db.close()
        return None

    item.title = title
    item.content = content
    db.commit()
    db.refresh(item)
    db.close()

    collection.update(
        ids=[str(knowledge_id)],
        documents=[content],
        metadatas=[{"business_id": business_id, "title": title}]
    )
    return item

def delete_knowledge(business_id, knowledge_id):
    db = SessionLocal()
    item = db.query(Knowledge).filter(
        Knowledge.id == knowledge_id,
        Knowledge.business_id == business_id
    ).first()

    if not item:
        db.close()
        return False

    db.delete(item)
    db.commit()
    db.close()

    collection.delete(ids=[str(knowledge_id)])
    return True