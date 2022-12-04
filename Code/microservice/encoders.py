from decimal import Decimal
import json


class DecimalEncoder(json.JSONEncoder):
    def default(self, n):
        if isinstance(n, Decimal):
            return int(n)
        else:
            return super().default(n)
