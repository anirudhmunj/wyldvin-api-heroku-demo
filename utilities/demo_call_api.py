import requests
from pprint import pprint


response = requests.post("http://127.0.0.1:8000/extract", json={"source": "development testt", "document": "this wine is aged 100% in new french oak. It pairs well with aged cheese, game, and assorted-meats"})

# response = requests.post("http://127.0.0.1:8000/extract", json={"source": "development testt", "document": "a"})

print(response.json())
if response.status_code == 200:
    result = response.json()
    print(result)
else:
    print('Error')
