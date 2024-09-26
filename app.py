from flask import Flask, request, jsonify, Response
import redis
import urllib3
import certifi
import argparse
import logging
import json

#-initialise app 
app = Flask(__name__)

#-initialising redis for cache
r = redis.Redis(host='localhost', port=6379, db=0)
EXPIRY = 60 # 1 hour


#-initialising urrllib
http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

#-cli input-------#
#-----------------#
#initialising arg parser
parser = argparse.ArgumentParser(
    prog='cache-proxy',
    description='a cli interface for a cache proxy'
)
parser.add_argument('port')
parser.add_argument('origin')

#readig cli args
args = parser.parse_args()
port = args.port
origin = args.origin


#clear cache
# TODO need to make it either port = 'clear' or port AND origin is needed
if port == 'clear':
    print('cache cleared')


# helper functions
#attempts to retrieve data from cache
def get_from_cache(data):
    data = json.loads(data)
    print('get')
    return Response(
        data, 
        status = 200, 
        headers ={
            'Content-Type':'application/json',
            'X-Cache' : 'Hit'
        }
    )
    
#attempts to retreive data from external api
def get_from_origin(method, url,data="", ):
    try:
        return http.request(method, url, body=json.dumps(data), headers={"Content-Type": "application/json"})
    except urllib3.exceptions.HTTPError as e:
        logging.error(f"HTTP error occurred: {e}")
        return jsonify({ "msg: : "f"HTTP error occurred: {e}"}), 400
    except urllib3.exceptions.RequestError as e:
        logging.error(f"Request error occurred: {e}")
        return jsonify({"msg":f"Request error occurred: {e}"}), 400

#attempts to set the cache
def set_cache(url, external_response):
    data = json.dumps(external_response.data.decode('utf-8'))
    if external_response.status == 200:
        try:
            r.setex(url, EXPIRY, data)
            print('set')
        except redis.RedisError as redis_error:
            logging.error(f"Redis error:{redis_error}")

#formats response (when using external api)
def response_cache_miss(response, status):
    return Response(
        response.data,
        status = status,
        headers = {
            'Content-Type': response.headers.get('Content-Type','application/json'),
            'X-Cache' : 'Miss'
        }
    )


#   GET    /url        CACHED
#-------------------------------#
@app.route("/<url>", methods=['GET'])
def cache_get(url):
    #attempt to read from cache
    try:
        cached_data = r.get(url)
        if cached_data:
            return get_from_cache(cached_data)
    except redis.RedisError as redis_error:
        logging.error(f"Redis error:{redis_error}")

    #set external url
    proxy_url = f"{origin}/{url}"

    #try fetching the data
    external_response = get_from_origin(request.method, proxy_url)

    #if request returns with 200, add to cache
    if external_response.status == 200:
        set_cache(url, external_response)

    #return the response from the server
    if external_response.status >= 500:
        return jsonify({'msg':'server error'}), external_response.status
    
    return response_cache_miss(external_response, external_response.status)
   

#   GET    /url /id       CACHED
#-------------------------------#
@app.route('/<url>/<id>', methods=['GET'])
def get_single_post(url,id):
    #attempt to read from cache
    url_id = f"{url}/{id}"
    try:
        cached_data = r.get(url_id)
        if cached_data:
            return get_from_cache(cached_data)
    except redis.RedisError as redis_error:
        logging.error(f"Redis error:{redis_error}")

    #set external url
    proxy_url = f"{origin}/{url}/{id}"

    #try fetching the data
    external_response = get_from_origin(request.method, proxy_url)

    #if request returns with 200, add to cache
    if external_response.status == 200:
        set_cache(url_id, external_response)

    #return the response from the server
    if external_response.status >= 500:
        return jsonify({'msg':'server error'}), external_response.status
    
    return response_cache_miss(external_response, external_response.status)



#   PUT, PATCH, DELETE     /url /id       NOT CACHED
#-------------------------------#

#PUT, PATCH, DELETE -> forward all requests, no cache
@app.route("/<url>/<id>", methods=['PUT', 'PATCH', 'DELETE'])
def forward_methods(url, id):
    print(type(request.data))
    data =json.loads(request.data.decode('utf-8'))
    print(data, type(data))
    #set external url
    proxy_url = f"{origin}/{url}/{id}"
    #try fetching the data
    external_response = get_from_origin(request.method, proxy_url, data)

    #return the response from the server
    if external_response.status >= 500:
        return jsonify({'msg':'server error'}), external_response.status
    
    return response_cache_miss(external_response, external_response.status)

if __name__ == '__main__':
    app.run(debug=True, port=port)




