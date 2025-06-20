"""
Module chính cung cấp dịch vụ viết lại nội dung bằng AI
"""

import os
import json
import time
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.llms import Ollama

from .utils import (
    load_config,
    save_config,
    format_prompt,
    check_api_keys,
    is_ollama_available,
    logger,
    DEFAULT_MODEL_GPT,
    DEFAULT_MODEL_OLLAMA
)
from .model import create_model, BaseRewriteModel

class RewriteService:
    """
    Dịch vụ viết lại nội dung
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Khởi tạo dịch vụ viết lại
        
        Args:
            config_path (str, optional): Đường dẫn đến file cấu hình. Nếu None, sử dụng cấu hình mặc định.
        """
        self.config_path = config_path
        self.config = load_config(config_path)
        self.model = None
        self._initialize_model()
        
    def _initialize_model(self):
        """Khởi tạo mô hình dựa trên cấu hình"""
        try:
            provider = self.config.get("model_provider", "openai")
            provider_config = self.config.get(provider, {})
            
            # Kiểm tra sự khả dụng của nhà cung cấp
            if provider == "openai" and not check_api_keys().get("openai"):
                logger.warning("OpenAI API key không có sẵn, chuyển sang sử dụng Gemini nếu có thể")
                if check_api_keys().get("gemini"):
                    provider = "gemini"
                    provider_config = self.config.get("gemini", {})
                elif is_ollama_available():
                    logger.warning("Gemini API key không có sẵn, chuyển sang sử dụng Ollama nếu có thể")
                    provider = "ollama"
                    provider_config = self.config.get("ollama", {})
                else:
                    raise ValueError("Không thể sử dụng OpenAI API, Gemini API hoặc Ollama")
            
            elif provider == "gemini" and not check_api_keys().get("gemini"):
                logger.warning("Gemini API key không có sẵn, chuyển sang sử dụng OpenAI nếu có thể")
                if check_api_keys().get("openai"):
                    provider = "openai"
                    provider_config = self.config.get("openai", {})
                elif is_ollama_available():
                    logger.warning("OpenAI API key không có sẵn, chuyển sang sử dụng Ollama nếu có thể")
                    provider = "ollama"
                    provider_config = self.config.get("ollama", {})
                else:
                    raise ValueError("Không thể sử dụng Gemini API, OpenAI API hoặc Ollama")
                    
            elif provider == "ollama" and not is_ollama_available():
                logger.warning("Ollama không khả dụng, chuyển sang sử dụng Gemini nếu có thể")
                if check_api_keys().get("gemini"):
                    provider = "gemini"
                    provider_config = self.config.get("gemini", {})
                elif check_api_keys().get("openai"):
                    logger.warning("Gemini API key không có sẵn, chuyển sang sử dụng OpenAI nếu có thể")
                    provider = "openai"
                    provider_config = self.config.get("openai", {})
                else:
                    raise ValueError("Không thể sử dụng Ollama, Gemini API hoặc OpenAI API")
            
            # Tạo mô hình dựa trên nhà cung cấp
            self.model = create_model(provider, provider_config)
            logger.info(f"Đã khởi tạo dịch vụ viết lại với {provider}")
            
        except Exception as e:
            logger.error(f"Lỗi khi khởi tạo dịch vụ viết lại: {str(e)}")
            raise
            
    def rewrite(self, content: str, custom_prompt: Optional[str] = None) -> str:
        """
        Rewrite the content using the current provider
        
        Args:
            content: The content to rewrite
            custom_prompt: Custom prompt to use for rewriting
        
        Returns:
            The rewritten content
        """
        if not content:
            raise ValueError("Content cannot be empty")
        
        # Get the provider
        provider = self.config.get("model_provider")
        if not provider:
            raise ValueError("No model provider configured")
        
        # Get or create the provider class
        provider_class = self._get_provider(provider)
        
        # Get the prompt
        if custom_prompt:
            prompt = custom_prompt
        else:
            prompt = self.utils.get_default_prompt(provider)
        
        # Get model info
        model_info = self.get_model_info()
        
        # Log the request
        self.logger.info(f"Rewriting content ({len(content)} chars) using {provider} ({model_info.get('model', 'unknown')})")
        
        try:
            # Rewrite the content
            start_time = time.time()
            rewritten = provider_class.rewrite(content, prompt)
            duration = time.time() - start_time
            
            # Check word count - log a warning if outside desired range
            word_count = len(rewritten.split())
            if word_count < 500 or word_count > 1000:
                self.logger.warning(f"Rewritten content has {word_count} words (target: 500-1000)")
                
            self.logger.info(f"Rewriting completed in {duration:.2f} seconds. Output: {len(rewritten)} chars, {word_count} words")
            
            return rewritten
            
        except Exception as e:
            logger.error(f"Lỗi khi viết lại nội dung: {str(e)}")
            return ""
            
    def switch_provider(self, provider: str) -> bool:
        """
        Chuyển đổi nhà cung cấp mô hình
        
        Args:
            provider (str): Nhà cung cấp mới ('openai', 'gemini' hoặc 'ollama')
            
        Returns:
            bool: True nếu chuyển đổi thành công, False nếu thất bại
        """
        if provider not in ["openai", "gemini", "ollama"]:
            logger.error(f"Nhà cung cấp không được hỗ trợ: {provider}")
            return False
            
        try:
            # Cập nhật cấu hình
            self.config["model_provider"] = provider
            
            # Lưu cấu hình nếu có đường dẫn
            if self.config_path:
                save_config(self.config, self.config_path)
                
            # Khởi tạo lại mô hình
            self._initialize_model()
            
            logger.info(f"Đã chuyển sang nhà cung cấp: {provider}")
            return True
            
        except Exception as e:
            logger.error(f"Lỗi khi chuyển đổi nhà cung cấp: {str(e)}")
            return False
            
    def update_config(self, provider: str, key: str, value: Any) -> bool:
        """
        Cập nhật cấu hình của nhà cung cấp
        
        Args:
            provider (str): Nhà cung cấp ('openai', 'gemini' hoặc 'ollama')
            key (str): Khóa cấu hình cần cập nhật
            value (Any): Giá trị mới
            
        Returns:
            bool: True nếu cập nhật thành công, False nếu thất bại
        """
        if provider not in ["openai", "gemini", "ollama"]:
            logger.error(f"Nhà cung cấp không được hỗ trợ: {provider}")
            return False
            
        try:
            # Cập nhật cấu hình
            if provider not in self.config:
                self.config[provider] = {}
                
            self.config[provider][key] = value
            
            # Lưu cấu hình nếu có đường dẫn
            if self.config_path:
                save_config(self.config, self.config_path)
                
            # Khởi tạo lại mô hình nếu đang sử dụng nhà cung cấp này
            if self.config.get("model_provider") == provider:
                self._initialize_model()
                
            logger.info(f"Đã cập nhật cấu hình {provider}.{key} = {value}")
            return True
            
        except Exception as e:
            logger.error(f"Lỗi khi cập nhật cấu hình: {str(e)}")
            return False
            
    def get_config(self) -> Dict[str, Any]:
        """
        Lấy cấu hình hiện tại
        
        Returns:
            Dict[str, Any]: Cấu hình hiện tại
        """
        return self.config
        
    def get_model_info(self) -> Dict[str, Any]:
        """
        Lấy thông tin về mô hình đang sử dụng
        
        Returns:
            Dict[str, Any]: Thông tin mô hình
        """
        if not self.model:
            return {"error": "Chưa khởi tạo mô hình"}
            
        return self.model.get_model_info()
        
    def get_available_providers(self) -> Dict[str, bool]:
        """
        Kiểm tra các nhà cung cấp khả dụng
        
        Returns:
            Dict[str, bool]: Trạng thái của các nhà cung cấp
        """
        api_keys = check_api_keys()
        ollama_available = is_ollama_available()
        
        return {
            "openai": api_keys.get("openai", False),
            "gemini": api_keys.get("gemini", False),
            "ollama": ollama_available
        }

# Hàm tiện ích để sử dụng nhanh chóng
def rewrite_content(
    content: str, 
    provider: str = "openai", 
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.7
) -> str:
    """
    Viết lại nội dung (hàm tiện ích)
    
    Args:
        content (str): Nội dung cần viết lại
        provider (str, optional): Nhà cung cấp ('openai', 'gemini' hoặc 'ollama'). Mặc định là 'openai'.
        api_key (str, optional): API key (cho OpenAI hoặc Gemini). Nếu None, sẽ sử dụng từ biến môi trường.
        model (str, optional): Tên mô hình. Nếu None, sẽ sử dụng mô hình mặc định.
        temperature (float, optional): Nhiệt độ của mô hình. Mặc định là 0.7.
        
    Returns:
        str: Nội dung đã viết lại
    """
    # Khởi tạo config
    config = {
        "model_provider": provider
    }
    
    # Cập nhật config tùy thuộc vào nhà cung cấp
    if provider == "openai":
        config["openai"] = {
            "api_key": api_key,
            "model": model or DEFAULT_MODEL_GPT,
            "temperature": temperature
        }
    elif provider == "gemini":
        config["gemini"] = {
            "api_key": api_key,
            "model": model or "gemini-1.5-flash",
            "temperature": temperature
        }
    elif provider == "ollama":
        config["ollama"] = {
            "model": model or DEFAULT_MODEL_OLLAMA,
            "temperature": temperature
        }
    
    # Tạo instance RewriteService với config
    service = RewriteService()
    
    # Cập nhật config và provider
    if api_key:
        service.update_config(provider, "api_key", api_key)
    if model:
        service.update_config(provider, "model", model)
    service.update_config(provider, "temperature", temperature)
    service.switch_provider(provider)
    
    # Viết lại nội dung
    return service.rewrite(content)
