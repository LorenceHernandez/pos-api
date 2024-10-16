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
        "$match": {"status": "Approved"}
    },
    {
        "$unwind": "$items"
    },
    {
        "$lookup": {
            "from": "goods_receipt_items",
            "let": {
                "itemId": "$items.itemId",
                "purchaseOrderId": "$_id"
            },
            "pipeline": [
                {
                    "$match": {
                        "$expr": {
                            "$and": [
                                {"$eq": ["$itemId", "$$itemId"]},
                                {"$eq": ["$purchaseOrderId", "$$purchaseOrderId"]},
                                {"$ne": ["$inspection", PurchaseOrderTransactionStatus.REJECTED]}
                            ]
                        }
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "quantityReceived": {"$sum": "$quantityReceived"},
                        "count": {"$sum": 1}
                    }
                }
            ],
            "as": "good_receipts"
        }
    },
    {
        "$addFields": {
            "quantityReceived": {
                "$ifNull": [{"$arrayElemAt": ["$good_receipts.quantityReceived", 0]}, 0]
            },
            "good_receipts_count": {
                "$ifNull": [{"$arrayElemAt": ["$good_receipts.count", 0]}, 0]
            }
        }
    },
    {
        "$match": {
            "$expr": {
                "$or": [
                    {"$lt": ["$quantityReceived", "$items.quantity"]},
                    {"$lt": ["$good_receipts_count", 1]}
                ]
            }
        }
    },
    {
        "$project": {
            "_id": {"$toString": "$_id"},  # Convert _id to string
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
                "requiredQuantity": {"$subtract": ["$items.quantity", "$quantityReceived"]}
            }
        }
    }
]

@purchase_order_receipt_bp.get(api)
@authorized
def get_purchase_order_received(user_id):
    # approved_orders = purchase_orders.find({"status": "Approved"})
    results =  list(purchase_orders.aggregate(pipeline))
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