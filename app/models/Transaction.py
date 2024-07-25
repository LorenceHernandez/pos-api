

from bson import ObjectId


class DiscountApplied:
    type = None
    value = None
    total_discount = None

    def __init__(self, type, value, total_discount):
        self.type = type
        self.value = value
        self.total_discount = total_discount

    @staticmethod
    def fromDict(data: dict):
        if data is None:
            return None
        
        return DiscountApplied(
            data.get('type'),
            data.get('value'),
            data.get('totalDiscount')
        )

    def toDict(self): 
        return {
            "type": self.type,
            "value": self.value,
            "totalDiscount": self.total_discount,
        } 

class Transaction: 
    _id = None
    _customer_id = None
    # _tender_amount = None
    # _change = None
    _branch_id = None
    reason = None
    transaction_no = None
    status = None
    transaction_date = None
    created_by = None
    services = None
    requested_by = None
    referred_by = None
    # tender_type = None
    # payment_due = None
    # total = None
    # sub_total = None
    invoice_no = None
    discount_applied = None
    customer_data = None
    payment_details = None
    # def __init__(self, 
    #         transaction_no = None, 
    #         status = None, 
    #         transaction_date = None,
    #         id = None,
    #         branch_id = None, 
    #         created_by = None, 
    #         customer_id = None, 
    #         services = None, 
    #         requested_by = None,
    #         referred_by = None,
    #         tender_type = None,
    #         tender_amount = None,
    #         change = None,
    #     ):
    #     self.id = id
    #     self.customer_id = customer_id
    #     self.transaction_no = transaction_no
    #     self.status = status
    #     self.transaction_date = transaction_date
    #     self.branch_id = branch_id
    #     self.created_by = created_by
    #     self.services = services
    #     self.requested_by = requested_by
    #     self.referred_by = referred_by
    #     self.tender_type = tender_type
    #     self.tender_amount = tender_amount
    #     self.change = change

    @staticmethod
    def fromDict(data: dict):
        if data is None:
            return None
            
        transaction = Transaction()

        transaction.transaction_no = data.get('transactionNo')
        transaction.transaction_date = data.get('transactionDate')
        transaction.reason = data.get('reason')
        transaction.status = data.get('status')
        transaction.id = data.get('_id')
        transaction.branch_id = data.get('branchId')
        transaction.created_by = data.get('createdBy')
        transaction.customer_id = data.get('customerId')
        transaction.services = data.get('services')
        transaction.requested_by = data.get('requestedBy')
        transaction.referred_by = data.get('referredBy')
        # transaction.tender_type = data.get('tendetType')
        # transaction.tender_amount = data.get('tenderAmount')
        # transaction.change = data.get('change')
        # transaction.payment_due = data.get('paymentDue')
        # transaction.total = data.get('total')
        # transaction.sub_total = data.get('subTotal')
        transaction.invoice_no = data.get('invoiceNo')
        transaction.discount_applied = DiscountApplied.fromDict(data.get('discountApplied'))
        transaction.customer_data = data.get('customerData')
        transaction.payment_details = data.get('paymentDetails')
        return transaction
    
    def toDict(self): 

        discount_applied = None
        if(self.discount_applied is not None):
            discount_applied = self.discount_applied.toDict()

        return {
            "id": self.id,
            "transactionNo": self.transaction_no,
            "transactionDate": self.transaction_date,
            "status": self.status,
            "branchId": self.branch_id,
            "customerId": self.customer_id,
            "requestedBy": self.requested_by,
            "referredBy": self.referred_by,
            "services": self.services,
            # "tenderType": self.tender_type,
            # "tenderAmount": self.tender_amount,
            # "paymentDue": self.payment_due,
            # "total": self.total,
            # "subTotal": self.sub_total,
            # "change": self.change,
            "reason": self.reason,
            "invoiceNo": self.invoice_no,
            "createBy": self.created_by,
            "customerData": self.customer_data,
            "discountApplied": discount_applied,
            "paymentDetails": self.payment_details
        }
    
    @property
    def id(self): 
        if(self._id is not None):
            return str(self._id)

    @id.setter
    def id(self, value): 
        if value is not None:
            self._id = ObjectId(value)
            
    @property
    def tender_amount(self): 
        if(self._change is not None):
            return self._tender_amount

    @tender_amount.setter
    def tender_amount(self, value): 
        if value is not None:
            self._tender_amount = float(value)

    @property
    def change(self): 
        if(self._change is not None):
            return self._change
    
    @change.setter
    def change(self, value): 
        if value is not None:
            self._change = float(value)

    @property
    def customer_id(self):
        if(self._customer_id is not None):
            return str(self._customer_id)

    @customer_id.setter
    def customer_id(self, value): 
        if value is not None:
            self._customer_id = ObjectId(value)
   
    @property
    def branch_id(self): 
        if(self._branch_id is not None):
            return str(self._branch_id)

    @branch_id.setter
    def branch_id(self, value): 
        if(value is not None):
            self._branch_id = ObjectId(value)

    # @property
    # def requested_by(self): return self._requested_by    

    # @requested_by.setter
    # def requested_by(self, value): 
    #     if(value is not None):
    #         self._requested_by = ObjectId(value)

    

    