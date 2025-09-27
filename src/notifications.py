from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict


@dataclass
class Notification:
    id: int
    email: str
    activity_name: str
    type: str
    message: str
    read: bool
    created_at: str


class NotificationStore:
    _notifications: List[Dict] = []
    _next_id: int = 1

    @classmethod
    def create(cls, email: str, activity_name: str, type_: str, message: str) -> Dict:
        n = Notification(
            id=cls._next_id,
            email=email,
            activity_name=activity_name,
            type=type_,
            message=message,
            read=False,
            created_at=datetime.utcnow().isoformat() + "Z",
        )
        cls._next_id += 1
        cls._notifications.append(asdict(n))
        return cls._notifications[-1]

    @classmethod
    def list_for_email(cls, email: str) -> List[Dict]:
        return [n for n in cls._notifications if n["email"] == email]

    @classmethod
    def list_all(cls) -> List[Dict]:
        return cls._notifications

    @classmethod
    def mark_read(cls, id: int) -> Dict:
        for n in cls._notifications:
            if n["id"] == id:
                n["read"] = True
                return n
        raise KeyError("Notification not found")


def send_email(email: str, subject: str, body: str) -> None:
    """Dev email adapter - just logs to stdout. Replace with real provider in production."""
    print(f"[email] to={email} subject={subject}\n{body}")


def create_and_send(background_tasks, email: str, activity_name: str, type_: str, message: str) -> Dict:
    n = NotificationStore.create(email, activity_name, type_, message)
    # schedule the email send asynchronously
    background_tasks.add_task(send_email, email, f"Notification: {type_} - {activity_name}", message)
    return n
