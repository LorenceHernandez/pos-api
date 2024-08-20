


from app.repositories.base import BackupRepository
from app.utils.generate_invoice import generate_invoice_str
from app.database.config import counters


class SettingRepository(BackupRepository):
    _collection = 'settings'
