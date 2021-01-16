import base64, hashlib, hmac, json, requests, time
"""
Python wrapper for the GOPAX REST API
"""
class GopaxService():
    def __init__(self):
        #TODO: Make key info more secure
        auth_file = open('auth.json')
        auth_data = json.load(auth_file)
        self.secret_key = auth_data['secret_key']
        self.api_key = auth_data['api_key']
    def call(self, need_auth, method, path, body_json=None, recv_window=None):
        #Brought from offical GOPAX API document
        method = method.upper()
        if need_auth:
            timestamp = str(int(time.time() * 1000))
            include_querystring = method == 'GET' and path.startswith('/orders?')
            p = path if include_querystring else path.split('?')[0]
            msg = 't' + timestamp + method + p
            msg += (str(recv_window) if recv_window else '') + (json.dumps(body_json) if body_json else '')
            raw_secret = base64.b64decode(self.secret_key)
            raw_signature = hmac.new(raw_secret, str(msg).encode('utf-8'), hashlib.sha512).digest()
            signature = base64.b64encode(raw_signature)
            headers = {'api-key': self.api_key, 'timestamp': timestamp, 'signature': signature}
            if recv_window:
                headers['receive-window'] = str(recv_window)
        else:
            headers = {}
        req_func = {'GET': requests.get, 'POST': requests.post, 'DELETE': requests.delete}[method]
        resp = req_func(url='https://api.gopax.co.kr' + path, headers=headers, json=body_json)
        return {
            'statusCode': resp.status_code,
            'body': resp.json(),
            'header': dict(resp.headers),
        }

    def get_chart_data(self,coin_name:str, start_timestamp:int, end_timestamp: int, stick_interval: int):
        """ timestamps are in milliseconds, stick_interval is in minutes and should be one of 1,5,30,1440"""
        response = self.call(False,'Get',f'/trading-pairs/{coin_name}/candles?start={start_timestamp}&end={end_timestamp}&interval={stick_interval}')
        return response
    def get_orders(self):
        response = self.call(True,'Get','/orders')
        return response
    def get_server_time(self):
        response = self.call(False,'Get','/time')
        return response
    def get_stats(self,coin_name:str):
        response = self.call(False,'Get',f'/trading-pairs/{coin_name}/stats')
        return response
    def cancel_order(self,order_id:int):
        response = self.call(True,'Delete',f'/orders/{order_id}')
        return response
    def place_order(self,coin_name:str, amount_krw:int):
        #TODO:The arguments are incomplete - needs to be filled in
        post_orders_req_body = {
            'side': 'buy', 'type': 'market', 'amount': amount_krw,
            'price': 0, 'tradingPairName': coin_name
        }
        response = self.call(True, 'POST', '/orders', post_orders_req_body, 200)
        return response

