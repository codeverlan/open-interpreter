from datetime import datetime

class Prompt:
    def __init__(self, id, project_id, name, content, is_default_system_message=False, created_at=None, updated_at=None):
        self.id = id
        self.project_id = project_id
        self.name = name
        self.content = content
        self.is_default_system_message = is_default_system_message
        self.created_at = created_at if isinstance(created_at, datetime) else datetime.fromisoformat(created_at) if created_at else datetime.now()
        self.updated_at = updated_at if isinstance(updated_at, datetime) else datetime.fromisoformat(updated_at) if updated_at else datetime.now()

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "name": self.name,
            "content": self.content,
            "is_default_system_message": self.is_default_system_message,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            project_id=data["project_id"],
            name=data["name"],
            content=data["content"],
            is_default_system_message=data.get("is_default_system_message", False),
            created_at=data["created_at"],
            updated_at=data["updated_at"]
        )