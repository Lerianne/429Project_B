import requests

BASE_URL = "http://localhost:4567"

def before_scenario(context, scenario):
    """Setup: Clear previous test data"""
    requests.delete(f"{BASE_URL}/projects")

def after_scenario(context, scenario):
    """Teardown: Cleanup after each test"""
    requests.delete(f"{BASE_URL}/projects")
