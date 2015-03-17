import re
import json

from stock.base_engine import Engine
from stock.model import Stock, ParserException

class HexunEngine(Engine):
    """
    Hexun Engine transform stock id & parse data
    """

    __slots__ = ['_url']

    DEFAULT_BASE_URL = "http://api.money.126.net/data/feed/%s,money.api"

    def __init__(self, base_url=None):

        if base_url is None:
            self._url = self.DEFAULT_BASE_URL
        else:
            self._url = base_url

        self.shanghai_transform = lambda sid: "0%s" % sid
        self.shenzhen_transform = lambda sid: "1%s" % sid

 
    def get_url(self, stock_id):
        hexun_id = self.get_hexun_id(stock_id)
        return self._url % hexun_id

    def get_hexun_id(self, stock_id):
        """
        get hexun id in URL from standard china stock/fund ID
        hexun regards stock/fund starting with 0 or 3 belongs to shenzhen
        """

        if stock_id.startswith('0') or stock_id.startswith('3'):
            return self.shenzhen_transform(stock_id)
        
        if stock_id.startswith('6'):
            return self.shanghai_transform(stock_id)
        
        raise ParserException("Unknow stock id %s" % stock_id)

    def parse(self, data):
        """parse data from hexun request
        """

        def prepare_data(data):
            """because hexun does not return a standard json,
            we need to extract the real json part
            """
            regroup = re.match(r'^_ntes_quote_callback\((.*)\)', data)

            if regroup:
                return regroup.group(1)
            else:
                raise ParserException("Unable to extact json from %s" % data)

        json_string = prepare_data(data)
        obj = json.loads(json_string)
        return self.generate_stock(obj)

    @staticmethod
    def generate_stock(obj):
        """obj struct is {'1000626': {'code': ...}}
        """
        stock = obj.values()[0]        

        code = stock.get('code', None)
        if code is not None:
            # we need to move the hexun addition market digit in stock code
            code = code[1:]

        return Stock(
            code=code,
            price=stock.get('price', None),
            time=stock.get('time', None),
            open=stock.get('open', None),
            low=stock.get('low', None),
            high=stock.get('high', None),
        )                

__all__ = ['HexunEngine']