import os
from dotenv import load_dotenv
import requests
import streamlit as st

# main.py
load_dotenv()  # Load environment variables from .env file
sec_key = os.getenv("MY_SECRET_KEY")
print(sec_key)
print("new commit")
# Example of using an external library (install in next step)
#import requests

def fetch_data(url):
    try:
        response = requests.get(url)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

if __name__ == "__main__":
    print("Starting application...")
    # Example: Fetching data from a public API
    data = fetch_data("https://jsonplaceholder.typicode.com/todos/1")
    if data:
        print(f"Fetched data: {data}")
    print("Application finished.")
