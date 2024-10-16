from bson import ObjectId
from flask import Blueprint, request, jsonify



from app.database.config import purchase_orders
from app.database.config import goods_receipt_items
from app.database.config import goods_receipt
from app.database.config import inventories
from app.middlewares.authorized_attribute import authorized
from app.cas_app.models.GoodsReceipt import  PurchaseOrderTransactionStatus, CompletePurchaseOrder
from app.repositories.goods_receipt import GoodsReceiptRepository
repository = GoodsReceiptRepository()

# def objectid_to_str(data):
#     if isinstance(data, dict):
#         return {k: objectid_to_str(v) for k, v in data.items()}
#     elif isinstance(data, list):
#         return [objectid_to_str(item) for item in data]
#     elif isinstance(data, ObjectId):
#         return str(data)
#     return data
api = '/api/cas/purchase-to-received'
purchase_order_receipt_bp = Blueprint('purchase_order_receipt', __name__)

pipeline = [
    {
        "$match": {
            "status": "Approved"
        }
    },
    {
        "$unwind": "$items"
    },
    {
        "$lookup": {
            "from": "goods_receipt_items",
            "let": {
                "itemId": "$items.itemId",
                "purchaseOrderId": {"$toString": "$_id"}
            },
            "pipeline": [
                {
                    "$match": {
                        "$expr": {
                            "$and": [
                                {"$eq": ["$itemId", "$$itemId"]},
                                {"$eq": ["$purchaseOrderId", "$$purchaseOrderId"]},
                                {"$ne": ["$inspection", "REJECTED"]}
                            ]
                        }
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "quantityReceived": {"$sum": "$quantityReceived"},
                        "goodReceiptsCount": {"$sum": 1}
                    }
                }
            ],
            "as": "good_receipts"
        }
    },
    {
        "$unwind": {
            "path": "$good_receipts",
            "preserveNullAndEmptyArrays": True
        }
    },
    {
        "$addFields": {
            "quantityReceived": {"$ifNull": ["$good_receipts.quantityReceived", 0]},
            "goodReceiptsCount": {"$ifNull": ["$good_receipts.goodReceiptsCount", 0]},
            "requiredQuantity": {"$subtract": ["$items.quantity", {"$ifNull": ["$good_receipts.quantityReceived", 0]}]}
        }
    },
    {
        "$match": {
            "$or": [
                {"$expr": {"$lt": ["$quantityReceived", "$items.quantity"]}},
                {"goodReceiptsCount": {"$lt": 1}}
            ]
        }
    },
    {
        "$project": {
            "_id": {"$toString": "$_id"},  # Convert purchase order _id to string
            "supplierId": "$supplierId",
            "totalAmount": "$totalAmount",
            "status": "$status",
            "supplierEmail": "$supplierEmail",
            "supplierName": "$supplierName",
            "approverUserID": "$approverUserID",
            "notes": "$notes",
            "item": {
                "itemId": "$items.itemId",
                "itemName": "$items.itemName",
                "quantity": "$items.quantity",
                "unitPrice": "$items.unitPrice",
                "totalPrice": "$items.totalPrice",
                "quantityReceived": "$quantityReceived",
                "requiredQuantity": "$requiredQuantity"
            }
        }
    }
]


@purchase_order_receipt_bp.get(api)
@authorized
def get_purchase_order_received(user_id):
    # approved_orders = purchase_orders.find({"status": "Approved"})
    results = list(purchase_orders.aggregate(pipeline))
    # for order in approved_orders:
    #     for item in order['items']:
    #         item_id = item['itemId']
    #         purchase_id = str(order['_id'])            
    #         good_receipts = list(goods_receipt_items.find({
    #             "itemId": item_id,
    #             "purchaseOrderId": purchase_id, 
    #            "inspection": {"$ne": PurchaseOrderTransactionStatus.REJECTED}
    #         }))
           
    #         quantity_received = sum(gr['quantityReceived'] for gr in good_receipts)
    #         good_receipts_count = len(good_receipts)
    #         required_quantity = item['quantity'] - quantity_received

    #         if quantity_received < item['quantity'] or good_receipts_count < 1:
    #             result_item = {
    #                 "_id": purchase_id,
    #                 "supplierId": order["supplierId"],
    #                 "totalAmount": order["totalAmount"],
    #                 "status": order["status"],
    #                 "supplierEmail": order["supplierEmail"],
    #                 "supplierName": order["supplierName"],
    #                 "approverUserID": order["approverUserID"],
    #                 "notes": order["notes"],
    #                 "item": {
    #                     "itemId": item_id,
    #                     "itemName": item['itemName'],
    #                     "quantity": item['quantity'],
    #                     "unitPrice": item['unitPrice'],
    #                     "totalPrice": item['totalPrice'],
    #                     "quantityReceived": quantity_received,
    #                     "requiredQuantity": required_quantity
    #                 }
    #             }
    #             results.append(result_item)
    return {"data": results } 

@purchase_order_receipt_bp.post(api + "/complete-purchase-order-items")
@authorized
def update_good_receipts_and_inventory(user_id):
    
    request_data = request.get_json()
    quantity = request_data["quantity"]
    itemID = request_data["itemID"]
    complete = CompletePurchaseOrder(**request_data, completorId=user_id)
    update_data = complete.model_dump()  # Assuming complete.model_dump() returns a dictionary
    # Perform the update
    update_result = goods_receipt.update_many(
        { '_id': { '$in': [ObjectId(id) for id in request_data["receiptIds"]] } },
        { '$set': update_data }
    )   

    # Check if any receipts were updated
    if update_result.modified_count > 0:
        # Find the item with the smallest quantity or nearest expiration date
        item = inventories.find_one(
            {
                "itemId": itemID
            },
            sort=[("quantityOnHand", 1), ("expirationDate", 1)]
        )

        if item:
            # Update the quantity for the identified item
            inventory_update_result = inventories.update_one(
                {"_id": item["_id"]},
              {"$inc": {"quantityOnHand": quantity}} 
            )

            if inventory_update_result.modified_count > 0:
                return jsonify({"message": f"Successfully updated inventory for item {itemID} to quantity {quantity}."}), 200
            else:
                return jsonify({"message": f"No changes made to the inventory for item {itemID}."}), 400
        else:
                       # Create a new inventory item if it doesn't exist
            new_inventory_item = {
                "itemId": itemID,
                "quantityOnHand": quantity,
                "reorderPoint": "",  # Empty string
                "expirationDate": "",  # Empty string
                "expirationWarningDays": 30,  # Set to 30 days
                "expirationStatus": "",  # Empty string
                "lotNumber": 0  # Set to zero
            }
            
            inventory_result  = inventories.insert_one(new_inventory_item)  # Insert new inventory item

            return jsonify({"message": f"New Inventory Created Successfully", "updateInventory": True, "inventoryID": str(inventory_result.inserted_id) }), 200
    else:
        return jsonify({"message": "No receipts were updated. Inventory update skipped."}), 400