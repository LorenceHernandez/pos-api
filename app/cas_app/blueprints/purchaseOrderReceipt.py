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

# # to do for populating the data 
# pipeline = [
#     {
#         "$lookup": {
#             "from": "purchase_orders",
#             "localField": "purchaseOrderID",
#             "foreignField": "_id",
#             "as": "purchaseOrderDetails"
#         }
#     },
#     {
#         "$lookup": {
#             "from": "items",
#             "localField": "purchaseOrderItemID",
#             "foreignField": "_id",
#             "as": "purchaseOrderItemDetails"
#         }
#     },
#     {
#         "$lookup": {
#             "from": "users",
#             "localField": "userReceiverID",
#             "foreignField": "_id",
#             "as": "userReceiverDetails"
#         }
#     },
#     {
#         "$lookup": {
#             "from": "users",
#             "localField": "createdBy",
#             "foreignField": "_id",
#             "as": "createdByDetails"
#         }
#     },
#     {
#         "$unwind": {
#             "path": "$purchaseOrderDetails"
#         }
#     },
#     {
#         "$unwind": {
#             "path": "$userReceiverDetails"
#         }
#     },
#     {
#         "$unwind": {
#             "path": "$createdByDetails"
#         }
#     },
#      {
#         "$unwind": {
#             "path": "$purchaseOrderItemDetails"
#         }
#     },
#     # {
#     #     "$addFields": {
#     #         "supplierIdObj": {
#     #             "$toObjectId": "$purchaseOrderDetails.supplierId"
#     #         },
           
#     #     }
#     # },
    
# ]
# def process_grouped_data(grouped_data):
#     result = []

#     for purchase_order_id, items in grouped_data.items():
#         grouped_items = {}
        
#         # Group items by purchaseOrderItemID
#         for item in items:
#             item_id = item["purchaseOrderItemID"]
#             if item_id not in grouped_items:
#                 grouped_items[item_id] = []
            
#             # Append item details to the grouped items
#             grouped_items[item_id].append({
#                 "_id": item["_id"],
#                 "createdAt": item["createdAt"],
#                 "createdBy": item["createdBy"],
#                 "createdByDetails": item["createdByDetails"],
#                 "officialReceipt": item["officialReceipt"],
#                 "price": item["price"],
#                 "quantity": item["quantity"],
#                 "updatedAt": item["updatedAt"],
#                 "userReceiverDetails": item["userReceiverDetails"],
#                 "purchaseOrderItemDetails": item["purchaseOrderItemDetails"]
#             })

#         purchaseOrderReceipt = []
        
#         # Create a receipt for each grouped item
#         for purchaseOrderReceiptID, receipt in grouped_items.items():
#             # Remove purchaseOrderItemDetails from the receipt objects
#             removePurchaseOrderItemDetails = [
#                 {k: v for k, v in obj.items() if k != "purchaseOrderItemDetails"} for obj in receipt
#             ]
            
#             purchaseOrderReceipt.append({
#                 "itemID": purchaseOrderReceiptID,
#                 "purchaseOrderReceipt": removePurchaseOrderItemDetails,
#                 "purchaseOrderItemDetails": grouped_items[purchaseOrderReceiptID][0]["purchaseOrderItemDetails"],
#                 "totalQuantity": sum(item["quantity"] for item in receipt),  # Correctly sum quantities
#                 "status": ""  # Placeholder for status
#             })
        
#         result.append({
#             "purchaseOrderDetails": grouped_data[purchase_order_id][0]["purchaseOrderDetails"],
#             "purchaseOrderStatus": "",  # Placeholder for purchase order status
#             "purchaseItems": purchaseOrderReceipt
#         })
    
#     return result


@purchase_order_receipt_bp.get(api)
@authorized
def get_purchase_order_received(user_id):
    approved_orders = purchase_orders.find({"status": "Approved"})
    results = []
    for order in approved_orders:
        for item in order['items']:
            item_id = item['itemId']
            purchase_id = str(order['_id'])            
            good_receipts = list(goods_receipt_items.find({
                "itemId": item_id,
                "purchaseOrderId": purchase_id, 
               "inspection": {"$ne": PurchaseOrderTransactionStatus.REJECTED}
            }))
           
            quantity_received = sum(gr['quantityReceived'] for gr in good_receipts)
            good_receipts_count = len(good_receipts)
            required_quantity = item['quantity'] - quantity_received

            if quantity_received < item['quantity'] or good_receipts_count < 1:
                result_item = {
                    "_id": purchase_id,
                    "supplierId": order["supplierId"],
                    "totalAmount": order["totalAmount"],
                    "status": order["status"],
                    "supplierEmail": order["supplierEmail"],
                    "supplierName": order["supplierName"],
                    "approverUserID": order["approverUserID"],
                    "notes": order["notes"],
                    "item": {
                        "itemId": item_id,
                        "itemName": item['itemName'],
                        "quantity": item['quantity'],
                        "unitPrice": item['unitPrice'],
                        "totalPrice": item['totalPrice'],
                        "quantityReceived": quantity_received,
                        "requiredQuantity": required_quantity
                    }
                }
                results.append(result_item)
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