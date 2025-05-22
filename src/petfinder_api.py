# src/petfinder_api.py
import requests
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json


class PetfinderAPI:
    def __init__(self, api_key: str, secret: str):
        self.api_key = api_key
        self.secret = secret
        self.base_url = "https://api.petfinder.com/v2"
        self.token = None
        self.token_expires = None

    def authenticate(self) -> bool:
        """Get OAuth token for API access"""
        auth_url = f"{self.base_url}/oauth2/token"

        data = {
            'grant_type': 'client_credentials',
            'client_id': self.api_key,
            'client_secret': self.secret
        }

        try:
            response = requests.post(auth_url, data=data)
            response.raise_for_status()

            token_data = response.json()
            self.token = token_data['access_token']
            # Token expires in 1 hour, refresh 5 minutes early
            self.token_expires = datetime.now() + timedelta(seconds=token_data['expires_in'] - 300)

            print("Successfully authenticated with Petfinder API")
            return True

        except requests.exceptions.RequestException as e:
            print(f"Authentication failed: {e}")
            return False

    def _ensure_token_valid(self):
        """Check if token is still valid, refresh if needed"""
        if not self.token or datetime.now() >= self.token_expires:
            self.authenticate()

    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make authenticated request to API"""
        self._ensure_token_valid()

        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.get(f"{self.base_url}/{endpoint}",
                                    headers=headers, params=params)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return None

    def get_animals(self, **filters) -> List[Dict]:
        """
        Get animals with optional filters

        Common filters:
        - type: 'dog', 'cat', 'bird', etc.
        - breed: specific breed
        - size: 'small', 'medium', 'large', 'xlarge'
        - gender: 'male', 'female'
        - age: 'baby', 'young', 'adult', 'senior'
        - location: postal code or city, state
        - distance: distance from location (miles)
        - limit: number of results (max 100 per page)
        - page: page number for pagination
        """
        animals = []
        page = 1

        while True:
            params = {**filters, 'page': page}
            if 'limit' not in params:
                params['limit'] = 100  # Max per page

            data = self._make_request('animals', params)

            if not data or 'animals' not in data:
                break

            batch = data['animals']
            if not batch:
                break

            animals.extend(batch)
            print(f"Retrieved {len(batch)} animals (page {page})")

            # Check if we have more pages
            pagination = data.get('pagination', {})
            if page >= pagination.get('total_pages', 1):
                break

            page += 1
            time.sleep(0.1)  # Be nice to the API

        return animals

    def get_animal_by_id(self, animal_id: str) -> Optional[Dict]:
        """Get detailed info for specific animal"""
        return self._make_request(f'animals/{animal_id}')

    def get_organizations(self, **filters) -> List[Dict]:
        """Get shelter/rescue organizations"""
        data = self._make_request('organizations', filters)
        return data.get('organizations', []) if data else []


# Example usage and testing
if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    # Initialize API client
    api = PetfinderAPI(
        api_key=os.getenv('PETFINDER_API_KEY'),
        secret=os.getenv('PETFINDER_SECRET')
    )

    # Test authentication
    if api.authenticate():
        # Test getting some animals
        print("\nTesting API with small dog sample...")
        dogs = api.get_animals(type='dog', size='small', limit=5)
        print(f"Found {len(dogs)} small dogs")

        if dogs:
            print(f"Sample dog: {dogs[0]['name']} - {dogs[0]['breeds']['primary']}")
    else:
        print("Failed to authenticate. Check your API credentials.")