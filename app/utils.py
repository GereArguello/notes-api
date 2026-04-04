from datetime import datetime, timezone
from app.core.database import SessionDep

def utc_now():
    return datetime.now(timezone.utc)

def shift_items(
    session: SessionDep,
    items: list,
    reverse: bool
):
    sorted_items = sorted(items, key=lambda x: x.sort_order, reverse=reverse)
    delta = 1 if reverse else -1

    for item in sorted_items:
        item.sort_order += delta
        session.add(item)
        session.flush()