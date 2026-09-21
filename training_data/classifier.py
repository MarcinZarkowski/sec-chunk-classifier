from google.genai._gaos.types.interactions import codeexecutioncallarguments
from google.genai._gaos.types.interactions import codeexecutioncallarguments
import os
from  concurrent.futures import ThreadPoolExecutor
from typing import Any
from google import genai
from google.genai import types
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
import math
from .prompt import BatchClassificationResponse, get_batch_prompt

load_dotenv()

MODEL_ID = os.environ["MODEL_ID"]
MODEL_RPM = int(os.environ["LLM_RPM"])
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
RETRIABLE_HTTP_STATUS = {408, 429, 500, 502, 503, 504}
RETRIABLE_GOOGLE_STATUS = {"ABORTED", "DEADLINE_EXCEEDED", "INTERNAL", "RESOURCE_EXHAUSTED", "UNAVAILABLE"}


class LlmError(RuntimeError):
    """Permanent provider failure."""


class LlmTransientError(RuntimeError):
    """Provider remained unavailable after retries."""


class LlmProvider:
    """Gemini structured-output client with a shared per-instance RPM limit."""

    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        self._client = genai.Client(api_key = GEMINI_API_KEY)
        self.thread_pool = ThreadPoolExecutor(max_workers=math.ceil(MODEL_RPM / 60 * 3.3))

    async def invoke_llm(self, prompt, extraction_schema):
        import asyncio
        loop = asyncio.get_running_loop()
        def _call():
            future = self.thread_pool.submit(
                self._client.models.generate_content,
                model=MODEL_ID,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_json_schema=extraction_schema,
                ),
            )
            return future.result()
        return await loop.run_in_executor(None, _call)

llm = LlmProvider()

async def classify_chunks(chunks):
    prompt = get_batch_prompt(chunks)
    return await llm.invoke_llm(prompt, BatchClassificationResponse.model_json_schema())
    