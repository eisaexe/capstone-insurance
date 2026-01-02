import logging
from enum import StrEnum

import requests

from perplexity_client.exceptions import PerplexityClientError

BASE_URL = "https://api.perplexity.ai"
COMPLETION_URL = "/chat/completions"

log = logging.getLogger(__name__)


class PerplexityModels(StrEnum):
    PPLX_7B_CHAT = "pplx-7b-chat"
    PPLX_70B_CHAT = "pplx-70b-chat"
    PPLX_7B_ONLINE = "pplx-7b-online"
    PPLX_70B_ONLINE = "pplx-70b-online"
    LLAMA_2_70B_CHAT = "llama-2-70b-chat"
    CODELLAMA_34B_INSTRUCT = "codellama-34b-instruct"
    MISTRAL_7B_INSTRUCT = "mistral-7b-instruct"
    MIXTRAL_8X7B_INSTRUCT = "mixtral-8x7b-instruct"


class PerplexityClient:
    def __init__(self, api_key: str, base_url: str = BASE_URL) -> None:
        self.api_key = api_key
        self.base_url = base_url

    def chat_completion(
            self,
            messages: list[dict[str, str]],
            model: PerplexityModels = PerplexityModels.MISTRAL_7B_INSTRUCT,
            **kwargs
    ) -> dict:
        payload = {
            "model": model.value,
            "messages": messages,
        }

        if kwargs.get("presence_penalty") and kwargs.get("frequency_penalty"):
            raise ValueError("You may use only one, frequency_penalty or presence_penalty. Not both.")

        match kwargs:
            case {"max_tokens": max_tokens}:
                payload = payload | {"max_tokens": max_tokens}
            case {"temperature": temperature}:
                if 2 < temperature or temperature < 0:
                    raise ValueError("Temperature must be between 0 and 2 included.")
                payload = payload | {"temperature": temperature}
            case {"top_p": top_p}:
                if 1 < top_p or top_p < 0:
                    raise ValueError("top_p must be between 0 and 1 included.")
                payload = payload | {"top_p": top_p}
            case {"top_k": top_k}:
                if 2048 < top_k or top_k < 0:
                    raise ValueError("top_k must be between 0 and 2048 included.")
                payload = payload | {"top_k": top_k}
            case {"presence_penalty": presence_penalty}:
                if 2.0 < presence_penalty or presence_penalty < -2.0:
                    raise ValueError("presence_penalty must be between -2.0 and 2.0 included.")
                payload = payload | {"presence_penalty": presence_penalty}
            case {"frequency_penalty": frequency_penalty}:
                payload = payload | {"frequency_penalty": frequency_penalty}

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {self.api_key}"
        }

        url = self.base_url + COMPLETION_URL

        try:
            response = requests.post(url, json=payload, headers=headers)
            return response.json()
        except requests.exceptions.ConnectionError as e:
            raise PerplexityClientError("There was a connection issue to Perplexity API.") from e
        except requests.exceptions.Timeout as e:
            raise PerplexityClientError("Request to Perplexity API timed-out.") from e
        except requests.exceptions.HTTPError as e:
            raise PerplexityClientError(f"Request to Perplexity API failed.") from e
        except requests.exceptions.RequestException as e:
            raise PerplexityClientError("Request to Perplexity API failed") from e
