import json
import os
from dataclasses import dataclass
from typing import Literal
from pydantic import BaseModel

from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Provider:
    """One Provider described as pure DATA."""

    name: str
    env_var: str
    is_free: bool
    base_url: str | None
    model: str

PROVIDERS=[
    Provider("Groq", "GROQ_API_KEY", True, None, "openai/gpt-oss-120b"),
]


def select_provider()->Provider:
    for provider in PROVIDERS:
        if os.environ.get(provider.env_var):
            return provider
    expected=", ".join(p.env_var for p in PROVIDERS)
    raise RuntimeError(f"No provider key set. Add one of {expected} to your .env file")


def build_client(provider: Provider):
    from groq import Groq

    api_key=os.environ[provider.env_var]
    if provider.base_url is None:
        return Groq(api_key=api_key)
    return Groq(api_key=api_key, base_url=provider.base_url)


def llm_reply(prompt: str,*,max_tokens: int=300)->str:
    """Send one user prompt; return the assistant's text."""

    provider=select_provider()
    client=build_client(provider)

    result=client.chat.completions.create(
        model=provider.model,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return result.choices[0].message.content


class COTStep(BaseModel):
    """A step in the COT process"""

    content: str
    step_type: Literal["THINKING", "FINAL_OUTPUT"]


def parse_cot_step(raw_reply: str)->COTStep | str:
    """Parse a raw reply into COTStep"""

    try:
        parsed=json.loads(raw_reply) # Converting to python dictionary
        return COTStep(**parsed) # returning COTStep Object
    except json.JSONDecodeError:
        return f"Invalid JSON Format: {raw_reply}"


SYSTEM_PROMPT="""
You are an expert assistant that solves user query using chain of thoughts.
You work in different phases -> THINKING (You think about the next step to be executed) and FINAL_OUTPUT (You output the final answer to the user query)

Rules:
- Reply with ONLY one JSON object for one response - no other texts or comments.
- Produce only ONE step at a time.
- Do not produce the next step.
- Do not produce multiple JSON objects for a single response.
- Do not produce a JSON array for a single response.
- If the problem is solved, return FINAL_OUTPUT.
- Otherwise return THINKING.

JSON_SCHEMA=
{
    "content": "your thinking or final output",
    "step_type": "THINKING" | "FINAL_OUTPUT"
}
- Emit one small thinking/plan step at a time until you have the final answer ready.
- When done with your chain of thought reasoning, emit the FINAL_OUTPUT step with the final answer.

Example:

User:
Roger has 5 tennis balls. He buys 2 cans of tennis balls.
Each can has 3 tennis balls. How many tennis balls does he have?

Assistant response:
{"step_type":"THINKING","content":"Roger starts with 5 tennis balls."}

Next assistant response:
{"step_type":"THINKING","content":"He buys 2 cans, with 3 tennis balls in each can."}

Next assistant response:
{"step_type":"THINKING","content":"The two cans contain 2 × 3 = 6 tennis balls."}

Next assistant response:
{"step_type":"FINAL_OUTPUT","content":"Roger has 11 tennis balls."}
"""


def llm_json_reply(messages: list[dict])->str:
    provider=select_provider()
    client=build_client(provider)

    kwargs: dict={
        "model": provider.model,
        "max_tokens": 400,
        "messages": messages
    }

    result=client.chat.completions.create(**kwargs)
    return result.choices[0].message.content


class COTAssistant:
    """An assistant that solves user queries using chain of thoughts."""

    def __init__(self):
        self.messages: list[dict]=[{"role": "system", "content": SYSTEM_PROMPT}]
        self.MAX_STEPS=15
    
    def run(self, user_query: str)->str:
        self.messages.append({"role": "user", "content": user_query})
        # print(f"👉{user_query}\n")

        for step_number in range (self.MAX_STEPS):
            self.messages.append({"role": "user", "content": f"""
            This is solution step {step_number}.

            Give EXACTLY ONE next solution step.

            Your response MUST have:
            "step_type": "THINKING"

            Do NOT provide the final answer yet.
            Do NOT provide multiple steps."""})
            raw_reply=llm_json_reply(self.messages)
            self.messages.append({"role": "assistant", "content": raw_reply})
            parsed=parse_cot_step(raw_reply) # Converting raw json into COTStep object

            if isinstance(parsed, COTStep): # Checking if parsed is a valid COTStep object
                if parsed.step_type=="THINKING":
                    print(f"💡{parsed.content}\n")
                    continue
                elif parsed.step_type=="FINAL_OUTPUT":
                    print(f"🎯{parsed.content}\n")
                    return parsed.content
            else:
                print(f"❌{parsed}\n")
                return parsed
        
        return f"Failed to derive the answer in {self.MAX_STEPS} steps."


assistant=COTAssistant()


while True:
    user_query=input("👉Enter your question: ")
    if user_query.lower() in ["exit", "quit", "bye"]:
        break
    answer=assistant.run(user_query)
    print(f"🎯{answer}\n")
    print("--------------------------------\n")

