from bson import ObjectId
from flask import Blueprint, jsonify, request
from pydash import omit

from app.cas_app.models.AccountsGroup import AccountsGroup
from app.database.config import accountsgroup
from app.database.store import insert_one
from app.middlewares.authorized_attribute import authorized
from app.utils.filter_values import filterValues

api = '/api/cas/accountsgroup'
accounts_group_bp = Blueprint('accountsgroup', __name__)

@accounts_group_bp.get(api + 's')
@authorized
def get_account_groups(user_id):
    ret = []
    try:

        data = accountsgroup.find()
        for item in data: 
          ret.append(AccountsGroup.fromDict(item).toDict())
            
        return {'data': ret }

    except Exception as e:
        return {'message': repr(e) }, 500

    
# @accounts_group_bp.get(api + '/<id>')
# @authorized
# def get_category(user_id, id):

#     try:
#         data = categories.find_one({ '_id': ObjectId(id) })

#         if data is not None: 
           
#             return {'data': Category.fromDict(data).toDict() }
#         return {'message': 'Unable to find supplier.'}

#     except Exception as e:
#         return {'message': repr(e) }, 500

@accounts_group_bp.post(api + '/create')
@authorized
def create_accounts_group(user_id):
    request_data = request.get_json()
    
    try:
        doc = insert_one('accountsgroup', filterValues(AccountsGroup.fromDict(request_data).toDict()))
        if doc.inserted_id:
            return {'message': 'AccountsGroup successfully created.'}
        else:
            return {'message': 'Unable to create AccountsGroup.'}, 500
    except Exception as e:
        return {'message': repr(e)}, 500
    

    
# @accounts_group_bp.post(api + '/edit')
# @authorized
# def edit_category(user_id):
#     request_data = request.get_json()
#     id = request_data['id']

#     try:
#       item = Category.fromDict(request_data)
   
    
#       filter = { '_id': ObjectId(id) }
#       new_val = { "$set": filterValues(omit(item.toDict(), 'id')) }

#       res = categories.update_one(filter, new_val)

#       if res.modified_count > 0:
#         return { 'message': 'Category successfully updated.' }
#       else:
#         return { 'message': 'Unable to update categories.' }, 400
#     except Exception as e:
#       print (e)
#       return { 'message': 'data format is invalid' }
