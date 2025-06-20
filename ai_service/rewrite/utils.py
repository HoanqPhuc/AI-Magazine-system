"""
Module cung cấp các tiện ích cho dịch vụ viết lại nội dung
"""

import os
import json
import logging
import requests
from typing import Dict, List, Any, Optional
from pathlib import Path

# Import module config
from config import get_config

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("rewrite.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("rewrite_service")

# Tải cấu hình khi import module
config = get_config()

# Mẫu mô hình mặc định
DEFAULT_MODEL_GPT = "gpt-3.5-turbo"
DEFAULT_MODEL_OLLAMA = config.get("OLLAMA_MODEL", "gemma2:latest")
DEFAULT_MODEL_GEMINI = config.get("GEMINI_MODEL", "gemini-1.5-flash-latest")

# Cấu hình mặc định
DEFAULT_CONFIG = {
    "model_provider": config.get("DEFAULT_PROVIDER", "gemini"),
    "openai": {
        "api_key": config.get("OPENAI_API_KEY"),
        "model": DEFAULT_MODEL_GPT,
        "temperature": 0.7,
        "max_tokens": 8000,
        "stream": False
    },
    "ollama": {
        "model": DEFAULT_MODEL_OLLAMA,
        "temperature": 0.7,
        "num_ctx": 8192,
        "stream": False,
        "base_url": config.get("OLLAMA_BASE_URL", "http://localhost:11434")
    },
    "gemini": {
        "api_key": config.get("GEMINI_API_KEY"),
        "model": DEFAULT_MODEL_GEMINI,
        "temperature": 0.7,
        "max_tokens": 8000,
        "stream": False
    }
}

# Định nghĩa các prompt mặc định
DEFAULT_PROMPTS = {
    "openai": {
        "system": "Bạn là trợ lý viết lại nội dung chuyên nghiệp. Nhiệm vụ của bạn là viết lại đoạn văn bản được cung cấp thành một bài viết có cấu trúc rõ ràng, đầy đủ thông tin, có độ dài khoảng 500-1000 từ. Hãy giữ văn phong phù hợp với ngữ cảnh ban đầu.",
        "user": "Hãy viết lại nội dung sau đây thành một bài viết có cấu trúc rõ ràng, mạch lạc và hấp dẫn. Giữ nguyên các thông tin quan trọng, ý nghĩa chính của bài viết gốc nhưng diễn đạt theo cách khác. Chia thành các đoạn hợp lý, đảm bảo bài viết có độ dài từ 500-1000 từ:\n\n{content}"
    },
    "ollama": {
        "system": "Bạn là trợ lý viết lại nội dung chuyên nghiệp. Nhiệm vụ của bạn là viết lại đoạn văn bản được cung cấp thành một bài viết có cấu trúc rõ ràng, đầy đủ thông tin, có độ dài khoảng 500-1000 từ.",
        "user": "Hãy viết lại nội dung sau đây thành một bài viết có cấu trúc rõ ràng, mạch lạc và hấp dẫn. Giữ nguyên các thông tin quan trọng, ý nghĩa chính của bài viết gốc nhưng diễn đạt theo cách khác. Chia thành các đoạn hợp lý, đảm bảo bài viết có độ dài từ 500-1000 từ:\n\n{content}"
    },
    "gemini": {
        "system": "Bạn là trợ lý viết lại nội dung chuyên nghiệp. Nhiệm vụ của bạn là viết lại đoạn văn bản được cung cấp thành một bài viết có cấu trúc rõ ràng, đầy đủ thông tin, có độ dài khoảng 500-1000 từ.",
        "user": "Hãy viết lại nội dung sau đây thành một bài viết có cấu trúc rõ ràng, mạch lạc và hấp dẫn. Giữ nguyên các thông tin quan trọng, ý nghĩa chính của bài viết gốc nhưng diễn đạt theo cách khác. Chia thành các đoạn hợp lý, đảm bảo bài viết có độ dài từ 500-1000 từ:\n\n{content}"
    }
}

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Tải cấu hình từ file hoặc sử dụng cấu hình mặc định
    
    Args:
        config_path (str, optional): Đường dẫn đến file cấu hình
        
    Returns:
        Dict[str, Any]: Cấu hình
    """
    if not config_path:
        logger.info("Sử dụng cấu hình mặc định")
        return DEFAULT_CONFIG.copy()
        
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        logger.info(f"Đã tải cấu hình từ {config_path}")
        
        # Đảm bảo các trường cần thiết tồn tại
        default_config = DEFAULT_CONFIG.copy()
        for key, value in default_config.items():
            if key not in config:
                config[key] = value
            elif isinstance(value, dict) and isinstance(config[key], dict):
                # Merge các trường con
                for subkey, subvalue in value.items():
                    if subkey not in config[key]:
                        config[key][subkey] = subvalue
                        
        return config
        
    except Exception as e:
        logger.warning(f"Không thể tải cấu hình từ {config_path}: {str(e)}. Sử dụng cấu hình mặc định")
        return DEFAULT_CONFIG.copy()

def save_config(config: Dict[str, Any], config_path: str) -> bool:
    """
    Lưu cấu hình vào file
    
    Args:
        config (Dict[str, Any]): Cấu hình
        config_path (str): Đường dẫn đến file cấu hình
        
    Returns:
        bool: True nếu lưu thành công, False nếu thất bại
    """
    try:
        # Đảm bảo thư mục tồn tại
        os.makedirs(os.path.dirname(os.path.abspath(config_path)), exist_ok=True)
        
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Đã lưu cấu hình vào {config_path}")
        return True
        
    except Exception as e:
        logger.error(f"Không thể lưu cấu hình vào {config_path}: {str(e)}")
        return False

def format_prompt(prompt: str, **kwargs) -> str:
    """
    Định dạng prompt với các giá trị
    
    Args:
        prompt (str): Prompt cần định dạng
        **kwargs: Các giá trị để thay thế trong prompt
        
    Returns:
        str: Prompt đã định dạng
    """
    try:
        return prompt.format(**kwargs)
    except KeyError as e:
        logger.warning(f"Không tìm thấy khóa {e} trong prompt")
        return prompt
    except Exception as e:
        logger.warning(f"Lỗi khi định dạng prompt: {str(e)}")
        return prompt

def check_api_keys() -> Dict[str, bool]:
    """
    Kiểm tra tính khả dụng của các API key
    
    Returns:
        Dict[str, bool]: Trạng thái của các API key
    """
    result = {}
    
    # Tải lại cấu hình để có thông tin mới nhất
    current_config = get_config()
    
    # Kiểm tra OpenAI API key
    openai_key = current_config.get("OPENAI_API_KEY")
    if openai_key:
        try:
            headers = {
                "Authorization": f"Bearer {openai_key}",
                "Content-Type": "application/json"
            }
            response = requests.get(
                "https://api.openai.com/v1/models",
                headers=headers,
                timeout=5
            )
            result["openai"] = response.status_code == 200
            
            if result["openai"]:
                logger.info("OpenAI API key khả dụng")
            else:
                logger.warning(f"OpenAI API key không khả dụng: {response.status_code}")
                
        except Exception as e:
            logger.warning(f"Không thể kiểm tra OpenAI API key: {str(e)}")
            result["openai"] = False
    else:
        logger.warning("Không tìm thấy OpenAI API key trong cấu hình")
        result["openai"] = False
    
    # Kiểm tra Gemini API key
    gemini_key = current_config.get("GEMINI_API_KEY")
    if gemini_key:
        try:
            # Kiểm tra key bằng cách gọi API models của Gemini
            headers = {
                "x-goog-api-key": gemini_key,
                "Content-Type": "application/json"
            }
            response = requests.get(
                "https://generativelanguage.googleapis.com/v1beta/models",
                headers=headers,
                timeout=5
            )
            result["gemini"] = response.status_code == 200
            
            if result["gemini"]:
                logger.info("Gemini API key khả dụng")
            else:
                logger.warning(f"Gemini API key không khả dụng: {response.status_code}")
                
        except Exception as e:
            logger.warning(f"Không thể kiểm tra Gemini API key: {str(e)}")
            result["gemini"] = False
    else:
        logger.warning("Không tìm thấy Gemini API key trong cấu hình")
        result["gemini"] = False
        
    return result

def is_ollama_available() -> bool:
    """
    Kiểm tra xem Ollama có sẵn hay không
    
    Returns:
        bool: True nếu Ollama có sẵn, False nếu không
    """
    try:
        # Tải lại cấu hình để có thông tin mới nhất
        current_config = get_config()
        ollama_base_url = current_config.get("OLLAMA_BASE_URL", "http://localhost:11434")
        
        # Kiểm tra Ollama API
        response = requests.get(f"{ollama_base_url}/api/tags", timeout=2)
        available = response.status_code == 200
        
        if available:
            logger.info(f"Ollama có sẵn tại {ollama_base_url}")
        else:
            logger.warning(f"Ollama không có sẵn tại {ollama_base_url}: {response.status_code}")
            
        return available
        
    except Exception as e:
        logger.warning(f"Không thể kết nối tới Ollama: {str(e)}")
        return False
