#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)

# https://maps.googleapis.com/maps/api/place/nearbysearch/json?
#location=-34.5988222,-58.4104831&radius=1000&type=restaurant&keyword=cruise&key=AIzaSyCZ8V7Jb7KwHGXMwNRb27U3Lf_nk5Wpc0c



@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("result").get("action") != "showRestoForLocation":
        return {}
    baseurl = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
    req_query = makeYqlQuery(req)

    print("req_query 1")
    print(req_query)
    if req_query is None:
        return {}
    req_query = baseurl + urlencode(req_query)
    print("req_query 2")
    print(req_query)
    result = urlopen(req_query).read()
    data = json.loads(result)
    res = makeWebhookResult(data)
    return res


def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    location = parameters.get("location")
    radius = "1000"
    apiKey = "AIzaSyCZ8V7Jb7KwHGXMwNRb27U3Lf_nk5Wpc0c"
    forType = "restaurant"

    print(json.dumps(result, indent=4))
    print(parameters)
    print(location)
    print(radius)
    print(apiKey)
    url = "location=" + location + "&radius=" + radius + "&type=" + forType + "&key=" + apiKey
    print(url)
    return url


def makeWebhookResult(data):
    print("makeWebhookResult")

    result = data.get('results')
    return result
    if result is None:
        return {}

    channel = result.get('channel')
    if channel is None:
        return {}

    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}

    condition = item.get('condition')
    if condition is None:
        return {}

    # print(json.dumps(item, indent=4))

    speech = "Today in " + location.get('city') + ": " + condition.get('text') + \
             ", the temperature is " + condition.get('temp') + " " + units.get('temperature')

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
