# bot.py
import requests
import os
import logging

logger = logging.getLogger(__name__)

class ChatBot:
    def __init__(
        self,
        hf_token: str,
        model: str = "mistralai/Mixtral-8x7B-Instruct-v0.1",
        api_url: str = "https://api-inference.huggingface.co/models"
    ):
        self.headers = {
            "Authorization": f"Bearer {hf_token}",
            "Content-Type": "application/json"
        }
        self.url = f"{api_url}/{model}"

    def get_response(self, message: str) -> str:
        payload = {"inputs": f"<s>[INST] {message} [/INST]"}
        try:
            # requests will JSON‑dump + UTF‑8 encode the body 
            resp = requests.post(self.url, headers=self.headers, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            # HF inference may return dict or list
            if isinstance(data, dict):
                return data.get("generated_text", "")
            if isinstance(data, list) and data:
                return data[0].get("generated_text", "")
            return str(data)
        except Exception as e:
            logger.error("API error", exc_info=True)
            raise RuntimeError("API isteği başarısız") from e
