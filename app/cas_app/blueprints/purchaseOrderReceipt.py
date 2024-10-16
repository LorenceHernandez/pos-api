from bson import ObjectId
from flask import Blueprint, request



from app.database.config import purchase_orders
from app.database.config import goods_receipt_items

from app.middlewares.authorized_attribute import authorized
from app.cas_app.models.GoodsReceipt import  PurchaseOrderTransactionStatus

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

# @purchase_order_receipt_bp.get(api + 's')
# @authorized
# def get_purchase_order_receipt(user_id):
   
#     try:
#         data = list(purchase_order_receipt.aggregate(pipeline)) 
#         data = convert_objectid_to_str(data)
#         grouped_data = defaultdict(list)
#         for item in data:
#             purchase_order_item_id = item['purchaseOrderID']
#             grouped_data[purchase_order_item_id].append(item)
#         grouped_data = dict(grouped_data)
#         result = process_grouped_data(grouped_data)               
#         return {'data': result}  # Return the populated documents as an object

#     except Exception as e:
#         return {'message': str(e)}, 400
    
# @purchase_order_receipt_bp.get(api + '/approved')
# @authorized
# def get_purchase_order_receipts_approve(user_id):
   
#     try:

#         # find purchase_orders that is not on list of  purchase_order_receipt and key is purchaseOrderID
#         receipt_ids = purchase_order_receipt.distinct("purchaseOrderID")
        
#         # Print the list of receipt IDs for debugging
#         print(receipt_ids)

#         # Find purchase orders that are not in the list of purchaseOrderIDs
#         purchase_orders_without_receipts = purchase_orders.find({
#             "_id": {"$nin": receipt_ids},
#             "status": "Approved"    # Exclude purchaseOrderIDs present in receipts
#         }) 
        
#         # Convert cursor to a list to see the actual documents
#         result = list(purchase_orders_without_receipts)
#         result = objectid_to_str(result)

#         return {'data': result}  # Return the populated documents as an object

#     except Exception as e:
#         return {'message': str(e)}, 500


# @purchase_order_receipt_bp.get(api + '/pending')
# @authorized
# def get_purchase_order_receipts_pending(user_id):
   
#     try:
#         newPipeline = list(pipeline)
#         newPipeline.append( {'$match': {'status': 'pending'}})
#         data = list(purchase_order_receipt.aggregate(newPipeline)) 
#         data = convert_objectid_to_str(data)
#         grouped_data = defaultdict(list)
#         for item in data:
#             purchase_order_item_id = item['purchaseOrderID']
#             grouped_data[purchase_order_item_id].append(item)
#         grouped_data = dict(grouped_data)
#         result = process_grouped_data(grouped_data)               
#         return {'data': result}
#     except Exception as e:
#         return {'message': str(e)}, 500


# @purchase_order_receipt_bp.get(api + '/completed')
# @authorized
# def get_purchase_order_receipts_completed(user_id):
   
#     try:
#         newPipeline = list(pipeline)
#         newPipeline.append( {'$match': {'status': 'completed'}})
#         print(newPipeline)
#         data = list(purchase_order_receipt.aggregate(newPipeline)) 
#         data = convert_objectid_to_str(data)
#         grouped_data = defaultdict(list)
#         for item in data:
#             purchase_order_item_id = item['purchaseOrderID']
#             grouped_data[purchase_order_item_id].append(item)
#         grouped_data = dict(grouped_data)
#         result = process_grouped_data(grouped_data)               
#         return {'data': result}
#     except Exception as e:
#         return {'message': str(e)}, 500
       
# @purchase_order_receipt_bp.post(api)
# @authorized
# def create_purchase_order_receipt(user_id):
#     request_data = request.get_json()
    
#     try:
#         request_data["purchaseOrderID"] = ObjectId(request_data["purchaseOrderID"])
#         request_data["userReceiverID"] = ObjectId(request_data["userReceiverID"])
#         request_data["purchaseOrderItemID"] = ObjectId(request_data["purchaseOrderItemID"])
#         request_data["createdBy"] = ObjectId(user_id) 
#         request_data["createdAt"] = datetime.now()
#         request_data["updatedAt"] = datetime.now() 
        
#         purchase_order = purchase_orders.find_one({"_id": request_data["purchaseOrderID"]}) 
#         if not purchase_order:
#             return {'message': 'Purchase order does not exist.'}, 404
#         pipeline = [
#             {
#                 "$match": {
#                     "purchaseOrderItemID": request_data["purchaseOrderItemID"],
#                     "purchaseOrderID": request_data["purchaseOrderID"]   # Use ObjectId directly
#                 }
#             },
#             {
#                 "$group": {
#                     "_id": None,
#                     "totalQuantity": {
#                         "$sum": "$quantity"
#                     }
#                 }
#             }
#         ]
#         purchaseOrderReceipts = purchase_order_receipt.aggregate(pipeline)
#         total_quantity = next(purchaseOrderReceipts, {}).get('totalQuantity', 0)
#         item_quantity = next(
#             (item['quantity'] for item in purchase_order['items'] if item['itemId'] == str(request_data["purchaseOrderItemID"])), 
#             0
#         )
#         if total_quantity >= item_quantity:
#             return {'message': 'Purchase Receipt is already completed check the amount in purchase order item'}, 400

#         total_quantity += request_data["quantity"]

#         # Determine the status based on total quantity and item quantity
#         if total_quantity >= item_quantity:
#             request_data["status"] = "completed"
#         else:
#             request_data["status"] = "pending"

#         update_data = {
#             "$set": {
#                 "status": request_data.get("status"),  # Assuming you want to update the status
#                 "updatedAt": datetime.now()            # Update the timestamp
#             }
#         }  
#         purchase_order_receipt.update_many(
#             {"purchaseOrderID": request_data["purchaseOrderID"],
#              "purchaseOrderItemID": request_data["purchaseOrderItemID"]
#              },  # Match condition
#             update_data                                # Update operation
#         )
#         receipt = PurchaseOrderReceipt.fromDict(request_data).toDict()
#         doc = insert_one('purchase_order_receipt', filterValues(receipt))
        
#         if doc and doc.inserted_id:
#             receipt["_id"] = str(doc.inserted_id)
#             receipt = convert_objectid_to_str(receipt)
#             return {"data": receipt }
#         else:
#             return {'message': 'Unable to create purchase order receipt.'}, 400
#     except Exception as e:
#         return {'message': str(e)}, 500
    

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