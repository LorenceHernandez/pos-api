from bson import ObjectId
from flask import Blueprint, request
import pprint

from collections import defaultdict
from datetime import datetime
from app.cas_app.models.PurchaseOrderReceipt import PurchaseOrderReceipt
from app.database.config import purchase_order_receipt
from app.database.store import insert_one
from app.middlewares.authorized_attribute import authorized
from app.utils.filter_values import filterValues
from app.utils.utils import convert_objectid_to_str

api = '/api/cas/purchase-order-receipt'
purchase_order_receipt_bp = Blueprint('purchase_order_receipt', __name__)

# to do for populating the data 
pipeline = [
    {
        "$lookup": {
            "from": "purchase_orders",
            "localField": "purchaseOrderID",
            "foreignField": "_id",
            "as": "purchaseOrderDetails"
        }
    },
    {
        "$lookup": {
            "from": "items",
            "localField": "purchaseOrderItemID",
            "foreignField": "_id",
            "as": "purchaseOrderItemDetails"
        }
    },
    {
        "$lookup": {
            "from": "users",
            "localField": "userReceiverID",
            "foreignField": "_id",
            "as": "userReceiverDetails"
        }
    },
    {
        "$lookup": {
            "from": "users",
            "localField": "createdBy",
            "foreignField": "_id",
            "as": "createdByDetails"
        }
    },
    {
        "$unwind": {
            "path": "$purchaseOrderDetails"
        }
    },
    {
        "$unwind": {
            "path": "$userReceiverDetails"
        }
    },
    {
        "$unwind": {
            "path": "$createdByDetails"
        }
    },
     {
        "$unwind": {
            "path": "$purchaseOrderItemDetails"
        }
    },
    # {
    #     "$addFields": {
    #         "supplierIdObj": {
    #             "$toObjectId": "$purchaseOrderDetails.supplierId"
    #         },
           
    #     }
    # },
    
]
@purchase_order_receipt_bp.get(api + 's')
@authorized
def get_purchase_order_receipt(user_id):
    result = []
    try:
        data = list(purchase_order_receipt.aggregate(pipeline)) 
        data = convert_objectid_to_str(data)
        grouped_data = defaultdict(list)
        for item in data:
            purchase_order_item_id = item['purchaseOrderID']
            grouped_data[purchase_order_item_id].append(item)
        grouped_data = dict(grouped_data)
        
        for purchase_order_id, items in grouped_data.items():
            grouped_items = {}
            for item in items:
                item_id = item["purchaseOrderItemID"]
                if item_id not in grouped_items:
                        grouped_items[item_id] = []
                        grouped_items[item_id].append({
                             "_id": item["_id"],
                            "createdAt": item["createdAt"],
                            "createdBy": item["createdBy"],
                            "createdByDetails": item["createdByDetails"],
                            "officialReceipt": item["officialReceipt"],
                            "price": item["price"],
                            "quantity": item["quantity"],
                            "updatedAt": item["updatedAt"],
                            "userReceiverDetails": item["userReceiverDetails"],
                            "purchaseOrderItemDetails": item["purchaseOrderItemDetails"]
                        })
                else: 
                        grouped_items[item_id].append({
                             "_id": item["_id"],
                            "createdAt": item["createdAt"],
                            "createdBy": item["createdBy"],
                            "createdByDetails": item["createdByDetails"],
                            "officialReceipt": item["officialReceipt"],
                            "price": item["price"],
                            "quantity": item["quantity"],
                            "updatedAt": item["updatedAt"],
                            "userReceiverDetails": item["userReceiverDetails"],
                            "purchaseOrderItemDetails": item["purchaseOrderItemDetails"]
                })
            purchaseOrderReceipt = []
            for purchaseOrderReceiptID, receipt in grouped_items.items():
                removePurchaseOrderItemDetails =  [{k: v for k, v in obj.items() if k != "purchaseOrderItemDetails"} for obj in receipt]
                purchaseOrderReceipt.append({
                    "itemID": purchaseOrderReceiptID,
                    "purchaseOrderReceipt": removePurchaseOrderItemDetails,
                    "purchaseOrderItemDetails": grouped_items[purchaseOrderReceiptID][0]["purchaseOrderItemDetails"],
                    "totalQuantity": sum(item["quantity"] for item in data),
                    "status": ""
               })
            result.append({
                 "purchaseOrderDetails": grouped_data[purchase_order_id][0]["purchaseOrderDetails"],
                 "purchaseOrderStatus": "",
                 "purchaseItems": purchaseOrderReceipt
            })
            

               
                
        return {'data': result}  # Return the populated documents as an object

    except Exception as e:
        return {'message': str(e)}, 500

@purchase_order_receipt_bp.post(api)
@authorized
def create_purchase_order_receipt(user_id):
    request_data = request.get_json()
    
    try:
        request_data["purchaseOrderID"] = ObjectId(request_data["purchaseOrderID"])
        request_data["userReceiverID"] = ObjectId(request_data["userReceiverID"])
        request_data["purchaseOrderItemID"] = ObjectId(request_data["purchaseOrderItemID"])
        request_data["createdBy"] = ObjectId(user_id) 
        request_data["createdAt"] = datetime.now()
        request_data["updatedAt"] = datetime.now() 

        receipt = PurchaseOrderReceipt.fromDict(request_data).toDict()        
        doc = insert_one('purchase_order_receipt', filterValues(receipt))
        
        if doc and doc.inserted_id:
            receipt["_id"] = str(doc.inserted_id)
            receipt = convert_objectid_to_str(receipt)
            return {"data": receipt }
        else:
            return {'message': 'Unable to create purchase order receipt.'}, 500
    except Exception as e:
        return {'message': str(e)}, 500
    