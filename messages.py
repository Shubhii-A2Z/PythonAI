from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client=Groq()

messages_example=[
    {
        "role": "system",
        "content": """
        You are a Time and Space Complexity Analysis Assistant

        Your Job:
        - Analyze the time and space complexity of code or algorithms.
        - Explain the reasoning in simple terms.
        - Use Big-O notation clearly.
        - If there are loops, recursion, sorting, hashing, or extra data structures, mention their impact.

        Guardrails:
        - Do not write full solutions unless explicitly asked.
        - Do not optimize the algorithm unless the user asks for optimization.
        - Do not explain unrelated DSA concepts.
        - If input code is incomplete, say what assumptions you are making.
        - Keep the answer begineer friendly and concise.

        Output format:
        1. Time Complexity:
        2. Space Complexity:
        3. Explaination:
        """
    },
    {
        "role": "user",
        "content": """
        What is the time complexity of this code?

        def find_sum():
            total=0
            for num in arr:
                total+=num
            return total
        """
    },
    {
        "role": "assistant",
        "content": """
        1. Time Complexity: O(n)
        
        2. Space Complexity: O(1)
        
        3. Explaination: 
        The loop runs once for every element in the array, so if the array has n elements, the time complexity is O(n).
        Only one extra variable in total is used, hence space complexity is O(1).
        """
    },
    {
        # This dictionary contains the actual question from the user to the LLM.
        "role": "user",
        "content": """
         What is the time complexity of this code?

        def binary_search(arr, target):
            left=0, right=len(arr)-1
            while left<=right:
                mid=(left+right)//2
                if arr[mid]==target:
                    return mid
                elif arr[mid]<target:
                    left=mid+1
                else right=mid-1
            return -1
        """
    }
]

response=client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=messages_example
)

print(response.choices[0].message.content)