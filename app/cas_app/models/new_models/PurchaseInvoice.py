from enum import Enum

from pydantic import BaseModel

class EditPurchaseInvoice(BaseModel):
    issueDate = None
    dueDate = None
    supplierId = None
    totalAmount = None
    isAccountMode = None
    accounting = []
    items = []
    invoiceDate = None
    status = None
    refInvoiceNumber = None
    notes = None
    series = None