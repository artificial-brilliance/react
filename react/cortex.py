import os

from typing import cast, Any, Optional

import openai

openai.api_key = os.environ["OPENAI_API_KEY"]

class Cortex(object):
    def __init__(self, system_prompt: Optional[str]):
        self.messages = [] if system_prompt is None else [{
            "role": "system",
            "content": system_prompt,
        }]

    def process(self, message: str):
        self.messages.append({"role": "user", "content": message})
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.messages,
            temperature=0)
        result = cast(Any, completion).choices[0].message.content
        self.messages.append({"role": "assistant", "content": result})
        return result
