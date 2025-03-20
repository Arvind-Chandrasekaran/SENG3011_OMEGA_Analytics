import requests
import pandas as pd
import json

url = "http://127.0.0.1:5000/retrieve_analysis"

data = {"stock_name": "AAPL",
        "user_name": "man88"
        }


response = requests.post(url, json=data)

data_dict = response.json()


print(data_dict)