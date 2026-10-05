from database import (
    SessionLocal,
    Knowledge,
)


def add_knowledge(business_id, title, content):
    db = SessionLocal()

    item = Knowledge(
        business_id=business_id,
        title=title,
        content=content
    )

    db.add(item)
    db.commit()
    db.refresh(item)
    db.close()

    return item


def search_knowledge(business_id, query, limit=3):
    db = SessionLocal()

    words = query.lower().split()

    results = db.query(Knowledge).filter(
        Knowledge.business_id == business_id
    ).all()

    matches = [
        k.content
        for k in results
        if any(
            word in k.content.lower()
            for word in words
            if len(word) > 2
        )
    ]

    db.close()

    return matches[:limit]


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

    return True