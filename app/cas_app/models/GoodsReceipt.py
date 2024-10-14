from enum import Enum, IntEnum
from typing import List

from bson import ObjectId
from pydantic import BaseModel, Field, computed_field

from app.cas_app.models.new_models.PurchaseOrder import PurchaseOrderAction, PurchaseOrderItemCondition, PurchaseOrderTransactionStatus
from app.cas_app.models.new_models.Supplier import Supplier
from app.utils.utils import getLocalTimeStr


class BaseAction(BaseModel):
    purchaseOrderId: str

    @property  
    def purchaseOrderObjectId(self) -> float:
        return ObjectId(self.purchaseOrderId)

class BaseActionItem(BaseModel):
    itemId: str

    @property  
    def itemObjectId(self) -> float:
        return ObjectId(self.itemId)

class ReceivePurchaseOrderItem(BaseActionItem):
    itemId: str
    itemName: str
    notes: str = None
    condition: PurchaseOrderItemCondition
    quantityReceived: float
    inventoryStatus: PurchaseOrderTransactionStatus = PurchaseOrderTransactionStatus.RECEIVED


class ReceivePurchaseOrder(BaseAction):
    dateReceived: str = Field(default_factory=getLocalTimeStr)
    receiverId: str = None
    status: PurchaseOrderTransactionStatus = PurchaseOrderTransactionStatus.PENDING_INSPECTION
    items: list[ReceivePurchaseOrderItem] = Field(min_items=1)


class InspectPurchaseOrderItem(BaseActionItem):
    itemId: str
    inspection: PurchaseOrderAction
    inspectionReason: str = None

class InspectPurchaseOrder(BaseAction):
    dateInspected: str = Field(default_factory=getLocalTimeStr)
    inspectorId: str = None
    items: list[InspectPurchaseOrderItem] = Field(min_items=1)
    status: PurchaseOrderTransactionStatus = PurchaseOrderTransactionStatus.PENDING_ACTION


class CompletePurchaseOrder(BaseAction):
    dateCompleted: str = Field(default_factory=getLocalTimeStr)
    status: PurchaseOrderTransactionStatus = PurchaseOrderTransactionStatus.COMPLETED
    action: PurchaseOrderAction
    actionReason: str = None
    completorId: str

class InventoryPurchaseOrder(BaseAction):
    status: PurchaseOrderTransactionStatus = PurchaseOrderTransactionStatus.STOCKED
    dateInventoried: str = Field(default_factory=getLocalTimeStr)
    inventoriedId: str
    items: list[object] = Field(min_items=1)
