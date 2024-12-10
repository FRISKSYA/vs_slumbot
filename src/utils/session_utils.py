# src/utils/session_utils.py

import time
import logging
from typing import Any, Callable, TypeVar, Optional
from functools import wraps

from sample.slumbot_api import NewHand, Login

T = TypeVar('T')

def execute_with_retry(
    func: Callable[[], T],
    max_retries: int = 3,
    delay: float = 1.0,
    exponential_backoff: bool = True
) -> T:
    """リトライ機構付きで関数を実行"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            
            wait_time = delay * (2 ** attempt if exponential_backoff else 1)
            logging.warning(
                f"Attempt {attempt + 1} failed: {str(e)}. "
                f"Retrying in {wait_time:.1f} seconds..."
            )
            time.sleep(wait_time)

def is_token_valid(token: Optional[str]) -> bool:
    """トークンの有効性をチェック"""
    if not token:
        return False
        
    try:
        test_state = NewHand(token)
        return 'error_msg' not in test_state
    except Exception as e:
        logging.warning(f"Token validation failed: {str(e)}")
        return False

def get_fresh_token(username: Optional[str] = None, password: Optional[str] = None) -> Optional[str]:
    """新しいトークンを取得"""
    if username and password:
        try:
            return Login(username, password)
        except Exception as e:
            logging.error(f"Failed to get new token: {str(e)}")
    return None

def with_valid_token(func: Callable) -> Callable:
    """トークンの有効性を確認するデコレータ"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        current_token = kwargs.get('current_token')  # 引数名の変更
        username = kwargs.get('username')
        password = kwargs.get('password')
        
        if not is_token_valid(current_token):
            new_token = get_fresh_token(username, password)
            if new_token:
                kwargs['current_token'] = new_token  # 引数名の変更
            else:
                kwargs['current_token'] = None
                
        return func(*args, **kwargs)
    return wrapper