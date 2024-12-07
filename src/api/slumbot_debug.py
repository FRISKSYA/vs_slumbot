# src/api/slumbot_debug.py

import requests
import sys
import logging
from typing import Dict, Any

class SlumbotAPI:
    """Enhanced debug version of Slumbot API client"""
    
    def __init__(self, host: str = 'slumbot.com'):
        self.host = host
        self.base_url = f'https://{host}/api'
    
    def _handle_response(self, response: requests.Response, endpoint: str) -> Dict[str, Any]:
        """Handle API response with enhanced error reporting"""
        status_code = response.status_code
        
        if status_code == 200:
            return response.json()
            
        # エラーの詳細なログ出力
        logging.error(f"API Error for {endpoint}:")
        logging.error(f"Status code: {status_code}")
        logging.error(f"Request URL: {response.url}")
        
        try:
            error_json = response.json()
            logging.error(f"Error response: {error_json}")
        except ValueError:
            logging.error("Could not parse error response as JSON")
            logging.error(f"Raw response: {response.text}")
            
        logging.error(f"Request headers: {response.request.headers}")
        logging.error(f"Request body: {response.request.body}")
        
        raise Exception(f"API request failed with status code: {status_code}")
    
    def act(self, token: str, action: str) -> Dict[str, Any]:
        """Send action to the API with enhanced error handling"""
        data = {'token': token, 'incr': action}
        response = requests.post(
            f'{self.base_url}/act',
            headers={'Content-Type': 'application/json'},
            json=data
        )
        return self._handle_response(response, 'act')
    
    def new_hand(self, token: str = None) -> Dict[str, Any]:
        """Start new hand with enhanced error handling"""
        data = {}
        if token:
            data['token'] = token
        response = requests.post(
            f'{self.base_url}/new_hand',
            headers={},
            json=data
        )
        return self._handle_response(response, 'new_hand')
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login with enhanced error handling"""
        data = {"username": username, "password": password}
        response = requests.post(
            f'{self.base_url}/login',
            headers={'Content-Type': 'application/json'},
            json=data
        )
        return self._handle_response(response, 'login')