from bson.json_util import dumps
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.template import Template,Context
import pymongo
import datetime
import random
import string
import json
import math
import re
from unidecode import unidecode
from dateutil.tz import *
from math import pi, sin , cos , atan2,sqrt
from mongo_filter import deal_filter, merchant_filter, deal_compact_filter
from merchantApi import process_merchant, deal_valid

failure = dumps({ "success": 0 })
dbclient = pymongo.MongoClient("mongodb://45.55.232.5:27017")
db = dbclient.perkkx

dayMap = {0:1,1:2,2:3,3:4,4:5,5:6,6:0}

def distance(obj):
    R = 6371
    dLat = (obj['l2'] - obj['l1']) * pi / 180
    dLon = (obj['ln2'] - obj['ln1']) * pi / 180
    lat1 = obj['l1'] * pi / 180
    lat2 = obj['l2'] * pi / 180
    a = sin(dLat/2) * sin(dLat/2) + sin(dLon/2) * sin(dLon/2) * cos(lat1) * cos(lat2)
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    d = R * c
    return d

def group_query_update(query, qStr):
    larr = map(lambda k: int(k), qStr.split("-"))
    if len(larr) == 1:
        query.update({"gmin": larr[0]})
    else:
        a = larr[0]
        b = larr[1]
        query.update({
            "$or": [
                {"$and": [{"gmin": {"$lte": a}}, {"gmax": {"$gt": a}}]},
                {"$and": [{"gmin": {"$lt": b}}, {"gmax": {"$gte": b}}]}
            ]
        })

# TODO: Optimise the query using memoization
@csrf_exempt
def get_deals(request, category):
    global db
    debug_message = ''
    try:
        mCollection = db.merchants
        dCollection = db.deals
        data = []
        data_dynamic_deals = []
        try:
            pages = int(request.GET['pages'])
        except:
            pages = 1
        if 'lat' in request.GET.keys() and 'lon' in request.GET.keys():
            lat = re.sub("[^0-9\.]","",request.GET['lat'])
            lon = re.sub("[^0-9\.]","",request.GET['lon'])
        else:
            lat = False
        if 'r' in request.GET.keys():
            r = int(request.GET['r'])
        else:
            r = False
        if 'open' in request.GET.keys():
            ope = True
        else:
            ope = False
        reverse = False
        if 'sort' in request.GET.keys():
            if 'rating' in request.GET['sort']:
                sort = 'rating'
                reverse = True
            elif 'price' in request.GET['sort']:
                sort = 'price'
            elif 'r' in request.GET['sort']:
                sort = 'distance'
            else:
                sort = 'distance'
        else:
            sort = 'distance'

        search = {"cat": int(category)}
        if 'subcat' in request.GET.keys():
            search.update({"subcat":{"$in":[int(x.replace("u","").strip("'")) for x in request.GET['subcat'].split(",")]}})
        if 'ser' in request.GET.keys():
            search.update({"spec_event.title":{"$in":request.GET['ser'].split(",")}})
        if 'cuisine' in request.GET.keys():
            search.update({"cuisine":{"$in":request.GET['cuisine'].split(",")}})
        if 'mtype' in request.GET.keys():
            search.update({"massage.type":int(request.GET['mtype'])})
        if 'tag' in request.GET.keys():
            search.update({"icons":{"$in":request.GET['tag'].split(",")}})
        if 'vendor' in request.GET.keys():
            search.update({"vendor_id": {"$in": [int(x.replace("u","").strip("'")) for x in request.GET['vendor'].split(",")]} })
        if 'area' in request.GET.keys():
            search.update({"address.text":{"$in":[re.compile(x.replace("_"," "),re.IGNORECASE) for x in request.GET['area'].split(",")]}})
        if 'name' in request.GET.keys():
        	search.update({"vendor_name":request.GET['name']})
        if 'type' in request.GET.keys():
            search.update({"type":{"$in":[re.compile(x.replace("_"," "),re.IGNORECASE) for x in request.GET['type'].split(",")]}})
        if 'rate' in request.GET.keys():
            rating = [float(int(x) - 0.1) for x in request.GET['rate'].split(",")]
            search.update({"rating":{"$gt":min(rating)}})
        if 'price' in request.GET.keys():
            low,high = request.GET['price'].split("-")
            low = int(low) - 1
            high = int(high) - 1
            search.update({"price":{"$gt":low,"$lt":high}})

        merchants = mCollection.find(search, merchant_filter)
        debug_message += "Count of merchants"+str(merchants.count())+"\n"
        debug_message += "merchant query: "+str(search)+"\n"

        for mer in merchants:
            # --- Selecting a deal -------- #
            deal_query = {"vendor_id": mer['vendor_id']}

            if 'group' in request.GET:
                group_query_update(deal_query, request.GET['group'])

            # Step 1, dynamic deals get preference
            dyn_query = deal_query.copy()
            dyn_query.update({
                "$or": [
                    { "valid_days": {"$exists": True}},
                    { "valid_time": {"$exists": True}}
                ]
            })
            dynamic_deals = [d for d in
                             dCollection.find(dyn_query, deal_filter)
                             if deal_valid(d)]

            # Step 2, get the primary deal
            deal_query.update({"deal_cat": "primary"})
            pdeal = dCollection.find_one( deal_query, deal_filter )

            deal_query.update({"deal_cat": "secondary"})
            if pdeal in dynamic_deals:
                pdeal = {}
            elif pdeal and deal_valid(pdeal):
                secondary = dCollection.find_one(deal_query, {"_id": False, "deal": True})
                if secondary:
                    pdeal['second_deal'] = secondary['deal']
            elif len(dynamic_deals) == 0:
                secondaries = [s for s in dCollection.find(deal_query, deal_filter) if deal_valid(s)]
                if len(secondaries) == 0:
                    continue
                pdeal = secondaries[0]
                if len(secondaries) > 1:
                    pdeal['second_deal'] = secondaries[1]['deal']
            debug_message += "\n Case 1 for dynamic"

            """
            else:
                dynamic_deals = [d for d in dCollection.find(deal_query, deal_filter)
                                 if deal_valid(d)]
                pdeal = {}
                debug_message += "\n Case 2 for dynamic"
            """

            debug_message += "Size of dynamic deals: "+str(len(dynamic_deals))+"\n"

            # ----- Setup Merchant data ------ #
            process_merchant(mer, save_timing=False)       # Found in merchantApi
            if mer['address']['lat'] and mer['address']['lng']:
                if lat:
                    data_for_distance = {
                        "l1":float(lat),
                        "ln1":float(lon),
                        "l2":float(re.sub("[^0-9\.]","",str(mer['address']['lat']))),
                        "ln2":float(re.sub("[^0-9\.]","",str(mer['address']['lng'])))
                    }
                    mer.update({"distance": distance(data_for_distance)})
                else:
                    mer.update({"distance": False})
            else:
                mer.update({"distance": False})

            # ----- Setup done ----- #

            # Adding to deals arrays
            for d in dynamic_deals:
                d.update(mer)
                data_dynamic_deals.append(d)

            if pdeal:
                pdeal.update(mer)
                data.append(pdeal)

        start = (pages-1)*10
        end = start + 10

        ## God knows how to sort within lists, so we prepend the priority list (dynamic_deals) to the data list
        ## and hope for the best
        data = data_dynamic_deals + data

        if end > len(data):
            end = len(data)
        if start > len(data):
            start = len(data) - 10
        if r:
            newlist = [x for x in data if x['distance']<r]
        else:
            newlist = data
        if ope:
            delta = [x for x in newlist if x['open'] is True]
        else:
            delta = newlist
        newlist = sorted(delta, key=lambda k: k[sort] if k[sort] is not False else 100,reverse=reverse)
        res = {
            "total": len(newlist),
            "data": newlist[start:end],
            "page": pages,
            "debug": debug_message
        }
        return HttpResponse(dumps(res), content_type="application/json")
    except Exception, e:
        return HttpResponse(dumps({"exception": "error : "+str(e)}), content_type="application/json")

""" Deprecated """
@csrf_exempt
def get_all_deals_for_vendor(request, typ, vendor):
    try:
        deals = [d for d in db.deals.find({"vendor_id": int(vendor), "type": typ}, deal_compact_filter)
                 if deal_valid(d)]
        return HttpResponse(dumps({"data": deals, "total": len(deals), "success": 1}))
    except Exception, e:
        return HttpResponse(dumps({"success": 0, "error": "Exception: "+str(e)}))

@csrf_exempt
def get_totals(request):
    global db
    res = []
    for i in range(1, 6):
        mers = [int(m['vendor_id']) for m in
                db.merchants.find({"cat": i}, {"vendor_id": True, "_id": False})]
        res.append(
            db.deals.count({"vendor_id": {"$in": mers}})
        )

    return HttpResponse(dumps({"data": res}), content_type='application/json')

""" Deprecated
@csrf_exempt
def get_totals(request):
    global db
    res = {
        "single": [],
        "group": []
    }
    for i in range(1,5):        # each category
        mers = db.merchants.find({"cat": i}, {"vendor_id": True})
        s = 0
        g = 0
        for mer in mers:
            s += len([
                d for d in db.deals.find({"vendor_id": mer['vendor_id'], "type": 'single'})
                if deal_valid(d)
            ])
            g += len([
                d for d in db.deals.find({"vendor_id": mer['vendor_id'], "type": 'group'})
                if deal_valid(d)
            ])

        res["single"].append(s)
        res["group"].append(g)
    return HttpResponse(dumps(res), content_type="application/json")
"""
