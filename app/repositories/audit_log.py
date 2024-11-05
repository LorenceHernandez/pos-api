


from app.new_models.AuditLog import AuditLog
from app.repositories.base import BackupRepository


class AuditLogRepository(BackupRepository):
    _collection = 'audit_logs'

    def insert_one(self, data: AuditLog):
        return super().insert_one(data.model_dump())