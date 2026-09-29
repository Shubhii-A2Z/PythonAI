from groq import Groq
from dotenv import load_dotenv
from system_prompt import SYSTEM_PROMPT

load_dotenv()

client=Groq()

def main():
    messages=[
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    print('-'*50)
    print("TaskBuddy: Hey There! What's on your mind?")
    print('           Dump your tasks here, and I\'ll organize them for you!')
    print('-'*50)

    while True:
        try:
            user_input=input("\nYou: ").strip()
            if user_input.lower() in ["exit", "quit"]:
                print("\nTaskBuddy: GoodBye!")
                break

            messages.append({
                "role": "user",
                "content": user_input
            })

            response=client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=messages
            )

            reply=response.choices[0].message.content

            print(f"\nTaskBuddy: {reply}")

            messages.append({
                "role": "assistant",
                "content": reply
            })

        except KeyboardInterrupt:
            print("\nTaskBuddy: GoodBye!")
            break

if __name__=='__main__':
    main()