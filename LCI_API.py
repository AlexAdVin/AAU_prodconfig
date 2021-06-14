#from __future__ import print_statement
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
apiKey = "83a038d5-28e4-49ef-b374-fe6def292e2c" # String | The API key to perform secured actions
query = "plastic" # String | A full text search query. Mulitple words are conjucted with AND (optional)
free = true

try: 
    # Search for data sets (numeric filters can use '<', '>', and ',' to specify ranges). e.g. validUntilYear=<2010 or validUntilYear=2000,2010 (all data sets in between 2000 and 2010). Boolean filters accept 'true' and 'false'
    api_response = api_instance.search_get(query=query)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->searchGet: %s\n" % e)