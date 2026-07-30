import hashlib
import json
import time,uuid
from datetime import datetime, timedelta  , timezone
from copy import deepcopy

PAYU_TEST_URL = "https://test.payu.in/_payment"
PAYU_SECURE_URL = "https://secure.payu.in/_payment"

def generate_transaction_id():
    return f"TXN-{datetime.now(timezone.utc):%Y%m%d%H%M%S}-{uuid.uuid4().hex[:12].upper()}"

class Error(Exception):
      pass

class payu_manager:
      " python api for payu subscription link generating"
      def __init__(self, MERCHANT_KEY, SALT,PAYU_URL=""):
            
            if not MERCHANT_KEY  or  not SALT:
                  raise Error("you should provide key and salt to payu api , https://payu.in/business")
            
            if not isinstance(MERCHANT_KEY,str) or not isinstance(SALT,str):
                  raise Error("key and salt should be strings")
            
            self.SALT: str = SALT
            self.MERCHANT_KEY: str = MERCHANT_KEY
            self.PAYU_URL : str = PAYU_URL
            
      @staticmethod
      def generate_hash( fields , KEY , SALT):
            hash_string = (
                  f"{KEY}|"
                  f"{fields['txnid']}|"
                  f"{fields['amount']}|"
                  f"{fields['productinfo']}|"
                  f"{fields['firstname']}|"
                  f"{fields['email']}|"
                  f"{fields.get('udf1', '')}|"
                  f"{fields.get('udf2', '')}|"
                  f"{fields.get('udf3', '')}|"
                  f"{fields.get('udf4', '')}|"
                  f"{fields.get('udf5', '')}||||||"
                  f"{fields['si_details']}|"
                  f"{SALT}"
            )
            return hashlib.sha512(hash_string.encode()).hexdigest()
      
      def generate_hash_self(self, fields):
            try:
                
                hash = self.generate_hash(fields, self.MERCHANT_KEY, self.SALT)
                fields_with_hash = deepcopy(fields)
                fields_with_hash['hash'] = hash
                return fields_with_hash
            
            except KeyError:
                  raise Error (
                        " required keys of payu subscription web api not provided"
                        " see https://docs.payu.in/reference/payment-consent-transaction-payu-hosted "
                        )
            
class payu_subscription(payu_manager):
      def __init__( self, *args, **kargs ):
            PAYU_URL = kargs.get("PAYU_URL", "")
            super().__init__( *args, PAYU_URL = PAYU_URL )
            self.amount = kargs.get( "amount", 1 )
            self.productinfo = kargs.get( "productinfo", "" )
            self.firstname = kargs.get( "firstname", "" )
            self.email = kargs.get( "email", "" )
            self.currency = kargs.get( "currency", "INR" )
            self.cycle = kargs.get( "cycle", "MONTHLY" )
            self.duration = kargs.get( "duration", 365 )
            self.dateobj = self.create_subscription_date( self.duration)
            self.si_details = self.get_si_details(self.amount,self.dateobj ,currency = self.currency , cycle = self.cycle)
            
      @staticmethod
      def get_si_details( amount , date_obj ,currency = "INR", cycle = "MONTHLY" ):
            si_details = {
                  "billingAmount": str(amount),
                  "billingCurrency": currency ,
                  "billingCycle": cycle,
                  "billingInterval": 1,
                  "paymentStartDate": date_obj["paymentStartDate"],
                  "paymentEndDate": date_obj["paymentEndDate"]
            }
            return si_details
      
      @staticmethod
      def create_subscription_date( days  = 365 * 30 ):
            start_date = datetime.today()
            end_date = start_date + timedelta(days=days)
            return {
                  "paymentStartDate": start_date.strftime("%Y-%m-%d"),
                  "paymentEndDate": end_date.strftime("%Y-%m-%d")
                  }
      
      def generate_subscription_link_data( self, fields  ):
            copyofdata = deepcopy ( fields )
            copyofdata.update( { "si_details" : self.si_details } )
            copyofdata.update( { "txnid" : generate_transaction_id() } )
            copyofdata.update( { "amount" : str ( self.amount) } )
            copyofdata.update( { "productinfo" : str( self.productinfo ) } )
            fields_with_hash = self.generate_hash_self ( copyofdata )
            return fields_with_hash
      


class payu_test_man( payu_subscription ):
      def __init__( self, *args, **kargs ):
            kargs.setdefault( "PAYU_URL", PAYU_TEST_URL )
            super().__init__( *args, **kargs )


class payu_production_man( payu_subscription ):
      def __init__( self, *args, **kargs ):
            kargs.setdefault( "PAYU_URL", PAYU_SECURE_URL )
            super().__init__( *args, **kargs )


def get_test_data_json():
      fields = {
            "firstname": "raju",
            "email": "raju@localhost.localhost",
            "phone": "0000000000",
            "surl": "https://localhost:3000/_/theme/payu_success.html",
            "furl": "https://localhost:3000/_/theme/payu_fail.html",
            "api_version": "7s",
            "si": "1",
      }
      return fields
      
      
if __name__ == "__main__":
      import os
      MERCHANT_KEY = os.getenv("PAYU_KEY")
      SALT = os.getenv("PAYU_SALT")
      
      if not MERCHANT_KEY or not SALT:
            raise ValueError("PAYU_KEY and PAYU_SALT environment variables must be set, you can get them from PayU dashboard")
      man = payu_test_man(MERCHANT_KEY, SALT , amount = 99 )
      
      print(json.dumps(man.generate_subscription_link_data(get_test_data_json())))
