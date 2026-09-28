from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Groq() class is used to make a client object
client=Groq()

response=client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {
            "role": "user",
            "content": "Explain in one line about binary search"
        }
    ]
)

print(response.choices[0].message.content)