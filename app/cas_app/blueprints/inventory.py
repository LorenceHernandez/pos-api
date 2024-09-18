from bson import ObjectId
from flask import Blueprint, jsonify, request
from pydash import omit

from app.cas_app.models.Inventory import Inventory
from app.database.config import inventories
from app.database.store import insert_one
from app.middlewares.authorized_attribute import authorized
from app.utils.filter_values import filterValues

api = '/api/cas/inventory'
inventory_bp = Blueprint('inventories', __name__)

@inventory_bp.get(api.replace('inventory', 'inventories'))
@authorized
def get_inventories(user_id):
    ret = []
    try:

        data = inventories.find()
        for item in data: 
          ret.append(Inventory.fromDict(item).toDict())
            
        return {'data': ret }

    except Exception as e:
        return {'message': repr(e) }, 500

    
@inventory_bp.get(api + '/<id>')
@authorized
def get_inventory(user_id, id):

    try:
        data = inventories.find_one({ '_id': ObjectId(id) })

        if data is not None: 
           
         return {'data': Inventory.fromDict(data).toDict() }
        return {'message': 'Unable to find supplier.'}

    except Exception as e:
        return {'message': repr(e) }, 500

@inventory_bp.post(api + '/create')
@authorized
def create_inventory(user_id):
    request_data = request.get_json()
    
    try:
        doc = insert_one('inventories', filterValues(Inventory.fromDict(request_data).toDict()))
        if doc.inserted_id:
            return {'message': 'Inventory successfully created.'}
        else:
            return {'message': 'Unable to create Inventory.'}, 500
    except Exception as e:
        return {'message': repr(e)}, 500
    

    
@inventory_bp.post(api + '/edit')
@authorized
def edit_inventory(user_id):
    request_data = request.get_json()
    id = request_data['id']

    try:
      item = Inventory.fromDict(request_data)
    except Exception as e:
      print (e)
      return { 'message': 'data format is invalid' }
   
   
    filter = { '_id': ObjectId(id) }
    new_val = { "$set": filterValues(omit(item.toDict(), 'id')) }

    res = inventories.update_one(filter, new_val)

    if res.modified_count > 0:
      return { 'message': 'Inventory successfully updated.' }
    else:
      return { 'message': 'Unable to update inventories.' }, 400
