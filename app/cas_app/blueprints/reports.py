
from bson import ObjectId
from flask import Blueprint
from pydash import get, omit

from app.cas_app.models.AccountsType import AccountsType
from app.cas_app.models.ChartAccount import ChartAccount

from app.database.config import (accountstype, chart_of_accounts, payments,
                                 purchase_invoices, receipts, sales_invoices, journal_entries)
from app.middlewares.authorized_attribute import authorized

api = '/api/cas/reports'
reports_bp = Blueprint('reports', __name__)

def toArray(list, totalKey):
    ret = []
    for l in list:
        try:
            ret.append({
                'accounting': l['accounting'],
                'totalAmountPaid': l[totalKey],
                '_id': l['_id'],
            })
        except Exception as e:
            print(repr(e))
    
    return ret

@reports_bp.get(api + '/trial-balance')
@authorized
def get_trial_balance(user_id):
    account_code_credit = 'account_code_credit'
    account_code_debit = 'account_code_debit'
    ret = []
    try:

        chart_of_accounts_data = chart_of_accounts.find()
        for chart_of_account_data in chart_of_accounts_data:
            chart = ChartAccount.fromDict(chart_of_account_data).toDict()
            ret.append({
                '_id': chart['_id'],
                'account_number': chart['accountNumber'],
                'account_name': chart['accountName'],
                'debit': 0,
                'credit': 0
            })
        

        merged_sources = toArray(receipts.find(), 'totalAmountPaid') + toArray(payments.find(), 'totalAmountPaid')  + toArray(sales_invoices.find(), 'total')  + toArray(purchase_invoices.find(), 'totalAmount') + toArray(journal_entries.find(), 'total')
        
        for data in merged_sources:
            accounting = data['accounting']
            totalAmountPaid = data['totalAmountPaid']
            print(accounting)
            for accounting_item in accounting:
                try:
                    code_credit = accounting_item[account_code_credit]
                    code_debit = accounting_item[account_code_debit]
                    for chart_of_account_data in ret:
                        try:
                            if chart_of_account_data['_id'] == code_credit:
                                chart_of_account_data['credit'] += totalAmountPaid
                            if chart_of_account_data['_id'] == code_debit:
                                chart_of_account_data['debit'] += totalAmountPaid
                        except: 
                            print('source of error1', data)
                            print('except1', chart_of_account_data)
                            
                except:
                    print('source of error2', data)
                    print('except2', accounting_item)

        return {'data': ret }

    except Exception as e:
        print(e)
        return {'message': repr(e) }, 500


@reports_bp.get(api + '/balance-sheet')
@authorized
def get_balance_sheet(user_id):
    account_code_credit = 'account_code_credit'
    account_code_debit = 'account_code_debit'
    groups = ['liabilities', 'member-equity', 'assets']
    ret = {
        'assets': [],
        'liabilities': [],
        'member-equity': []
    }
    try:

        chart_of_accounts_data = chart_of_accounts.find()
        for chart_of_account_data in chart_of_accounts_data:
            chart = ChartAccount.fromDict(chart_of_account_data).toDict()
            if chart.get('accountType') != 'none' and chart.get('accountType') is not None and chart.get('accountType') != "":
                accounttype = AccountsType.fromDict(accountstype.find_one({'_id': ObjectId(chart.get('accountType'))})).toDict()
                if accounttype['name'].lower() in groups:
                    ret[accounttype['name'].lower()].append({
                        '_id': chart['_id'],
                        'account_number': chart['accountNumber'],
                        'account_name': chart['accountName'],
                        'debit': 0,
                        'credit': 0
                    })
        
        merged_sources = toArray(receipts.find(), 'totalAmountPaid') + toArray(payments.find(), 'totalAmountPaid')  + toArray(sales_invoices.find(), 'total')  + toArray(purchase_invoices.find(), 'totalAmount') + toArray(journal_entries.find(), 'total')
        
        for data in merged_sources:
            accounting = data['accounting']
            totalAmountPaid = data['totalAmountPaid']
            for accounting_item in accounting:
                code_credit = accounting_item[account_code_credit]
                code_debit = accounting_item[account_code_debit]
                for group in groups:
                    for chart_of_account_data in ret[group]:
                        if chart_of_account_data['_id'] == code_credit:
                            chart_of_account_data['credit'] += totalAmountPaid
                        if chart_of_account_data['_id'] == code_debit:
                            chart_of_account_data['debit'] += totalAmountPaid

        return {'data': ret }

    except Exception as e:
        return {'message': repr(e) }, 500


@reports_bp.get(api + '/profit-and-loss')
@authorized
def get_profit_loss(user_id):
    account_code_credit = 'account_code_credit'
    account_code_debit = 'account_code_debit'
    groups = ['less:expense', 'net profit(loss)', 'income']
    ret = {
        'less:expense': [],
        'net profit(loss)': [],
        'income': []
    }
    try:

        chart_of_accounts_data = chart_of_accounts.find()
        for chart_of_account_data in chart_of_accounts_data:
            chart = ChartAccount.fromDict(chart_of_account_data).toDict()
            if chart.get('accountType') != 'none' and chart.get('accountType') is not None and chart.get('accountType') != "":
                accounttype = AccountsType.fromDict(accountstype.find_one({'_id': ObjectId(chart.get('accountType'))})).toDict()
                if accounttype['name'].lower() in groups:
                    ret[accounttype['name'].lower()].append({
                        '_id': chart['_id'],
                        'account_number': chart['accountNumber'],
                        'account_name': chart['accountName'],
                        'debit': 0,
                        'credit': 0
                    })
        
        merged_sources = toArray(receipts.find(), 'totalAmountPaid') + toArray(payments.find(), 'totalAmountPaid')  + toArray(sales_invoices.find(), 'total')  + toArray(purchase_invoices.find(), 'totalAmount') + toArray(journal_entries.find(), 'total')
        
        for data in merged_sources:
            accounting = data['accounting']
            totalAmountPaid = data['totalAmountPaid']
            for accounting_item in accounting:
                code_credit = accounting_item[account_code_credit]
                code_debit = accounting_item[account_code_debit]
                for group in groups:
                    for chart_of_account_data in ret[group]:
                        if chart_of_account_data['_id'] == code_credit:
                            chart_of_account_data['credit'] += totalAmountPaid
                        if chart_of_account_data['_id'] == code_debit:
                            chart_of_account_data['debit'] += totalAmountPaid

        return {'data': ret }

    except Exception as e:
        return {'message': repr(e) }, 500


@reports_bp.get(api + '/general-ledger')
@authorized
def get_general_ledger(user_id):
    
    query = {}

    def _create_match_accounting_query(table_name, id="$_id"):
        return [
            { 
                '$lookup': {
                    'from': table_name,
                    "let": {
                        "accountId": id,
                    },
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$gt": [
                                        {
                                            "$size": {
                                                "$filter": {
                                                    "input": "$accounting",
                                                    "as": "item",
                                                    "cond": {
                                                        "$or": [
                                                            { "$eq": [ "$$item.account_code_debit", "$$accountId" ] },
                                                            { "$eq": [ "$$item.account_code_credit", "$$accountId" ] },
                                                        ]
                                                    }
                                                }
                                            }
                                        },
                                        0 
                                    ]
                                }
                            }
                        },
                        {
                            '$addFields': {
                                '_id': {'$toString': '$_id' },
                            }
                        },
                    ],
                    "as": table_name
                }, 
            },
        ]

    result = []
    data = list(chart_of_accounts.aggregate([
        { '$match': query },
        {
            '$addFields': {
                '_id': {'$toString': '$_id' },
            }
        },
        *_create_match_accounting_query('payments'),
        *_create_match_accounting_query('purchase_invoices'),
        *_create_match_accounting_query('receipts'),
        *_create_match_accounting_query('sales_invoices'),
        {
            "$match": {
                "$expr": {
                    "$or": [
                        { "$gt": [{"$size": "$payments"}, 0] },
                        { "$gt": [{"$size": "$purchase_invoices"}, 0] },
                        { "$gt": [{"$size": "$receipts"}, 0] },
                        { "$gt": [{"$size": "$sales_invoices"}, 0] },
                    ]
                }
            }
        },
    ]))

    for item in data:
        keys = {
            "payments": lambda i: get(i, 'totalAmountPaid', 0),
            "purchase_invoices": lambda i: get(i, 'totalAmount', 0),
            "receipts": lambda i: get(i, 'totalAmountPaid', 0),
            "sales_invoices": lambda i: get(i, 'total', 0),
        }

        def sumAllTransactions(debit=True):
            sum = 0
            for key, fn in keys.items():
                transactions = get(item, key, [])
                for transaction in transactions:
                    accounting_key = 'account_code_debit' if debit else 'account_code_credit'
                    accounting = get(transaction, 'accounting', [])
                    
                    for account in accounting:
                        if(account[accounting_key] == item['_id']):
                            sum += fn(transaction)

            return sum

        overallTotalDebit = sumAllTransactions(True)
        overallTotalCredit = sumAllTransactions(False)

        item['overallTotalDebit'] = overallTotalDebit
        item['overallTotalCredit'] = overallTotalCredit
        result.append(item)

    keys = ['payments', 'purchase_invoices', 'receipts', 'sales_invoices']
    for index, item in enumerate(result):
        transactions = []
        
        for key in keys:
            data = map(lambda i: { **i, 'type': key }, item.get(key, []))
            transactions.extend(list(data))
            result[index] = omit(result[index], key)
        
        transactions = sorted(transactions, key=lambda i: ObjectId(i['_id']).generation_time)
        result[index]['transactions'] = transactions


    return result
    

@reports_bp.get(api + '/general-entries')
@authorized
def get_general_entries(user_id):
    query = {}
    result = []
    data = list(chart_of_accounts.aggregate([
        { '$match': query },
        {
            '$addFields': {
                '_id': {'$toString': '$_id' },
            }
        },
        { 
            '$lookup': {
                'from': 'journal_entries',
                'let': {
                    "accountId": "$_id"
                },
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$and": [
                                    { 
                                        "$or": [
                                            { "$eq": ["$accounting.account_code_debit", "$$accountId"] },
                                            { "$eq": ["$accounting.account_code_credit", "$$accountId"] },
                                        ] 
                                    },
                                    { "$ne": ["$status", "Draft"] }
                                ]
                            }
                        }
                    },
                     {
                        '$addFields': {
                            '_id': {'$toString': '$_id' },
                        }
                    },
                ],
                'as': 'journal_entries'
            }, 
        },
        {
            "$match": {
                "$expr": {
                    "$or": [
                        { "$gt": [{"$size": "$journal_entries"}, 0] },
                    ]
                }
            }
        }
    ]))

    for item in data:

        item['journal_entries'] = list(map(lambda i: ({ **i, "isDebit": i['accounting']['account_code_debit'] == item['_id'] }), item['journal_entries']))

        get_entries_by = lambda key: list(filter(lambda i: i['accounting'][key] == item['_id'], item['journal_entries']))
        
        debitEntries = get_entries_by('account_code_debit')
        totalDebit = sum(map(lambda i: get(i, 'total', 0), debitEntries))
        
        creditEntries = get_entries_by('account_code_credit')
        totalCredit = sum(map(lambda i: get(i, 'total', 0), creditEntries))

        item['totalDebit'] = totalDebit
        item['totalCredit'] = totalCredit
        result.append(item)

    return result