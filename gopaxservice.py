import base64, hashlib, hmac, json, requests, time
"""
Python wrapper for the GOPAX REST API
"""
class GopaxService():
    def __init__(self,secret_key,api_key):
        self.secret_key = secret_key
        self.api_key = api_key
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


    """ Private APIs 
        Private APIs need authentication
    """

    def get_balance(self):
        response = self.call(False,'Get','/balances')
        return response
    def get_balance_by_asset(self, asset_name:str):
        response = self.call(False,'Get',f'/balances/{asset_name}')
        return response
    def get_orders(self):
        response = self.call(True,'Get','/orders')
        return response
    def get_order_by_id(self, order_id:int):
        response = self.call(True,'Get',f'/orders/{order_id}')
        return response
    def place_order(self,client_order_id = None, trading_pair_name:str, side:str, order_type:str, price, stop_price = None,\
                    amount, protection:bool = False, time_in_force:str = "gtc"):
        post_orders_req_body = {
            "clientOrderId": client_order_id,       # opt. | client order ID (max 20 characters of [a-zA-Z0-9_-])
            "tradingPairName": trading_pair_name,   # man. | order book
            "side": side,                           # man. | buy, sell
            "type": order_type,                     # man. | limit, market
            "price": price,                         # man. (only for limit) | price
            "stopPrice": stop_price,                # opt. (becomes a stop order if set) | stop price
            "amount": amount,                       # man. | amount
            "protection": protection,               # opt. (default=no) | whether protection is activated (yes or no)
            "timeInForce": time_in_force            # opt. (default=gtc) | limit order's time in force (gtc/po/ioc/fok)``
        }
        response = self.call(True, 'POST', '/orders', post_orders_req_body, 200)
        return response

    def cancel_order(self,order_id:int):
        response = self.call(True,'Delete',f'/orders/{order_id}')
        return response

    def get_trading_history(self):
        response = self.call(False,'Get','/trades')
        return response
    def get_deposit_withdrawal_status(self):
        response = self.call(False,'Get','/deposit-withdrawal-status')
        return response
    def get_crypto-deposit-addresses(self):
        response = self.call(False,'Get','/crypto-deposit-addresses')
        return response
    def get_crypto-withdrawal-addresses(self):
        response = self.call(False,'Get','/crypto-withdrawal-addresses')
        return response
        
    """ Public APIs
        Public APIs don't need authentication. There is no need to set headers
    """
    def get_chart_data(self,coin_name:str, start_timestamp:int, end_timestamp: int, stick_interval: int):
        """ timestamps are in milliseconds, stick_interval is in minutes and should be one of 1,5,30,1440"""
        response = self.call(False,'Get',f'/trading-pairs/{coin_name}/candles?start={start_timestamp}&end={end_timestamp}&interval={stick_interval}')
        return response
    def get_server_time(self):
        response = self.call(False,'Get','/time')
        return response
    def get_stats(self,coin_name:str):
        response = self.call(False,'Get',f'/trading-pairs/{coin_name}/stats')
        return response