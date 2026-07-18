
from openai import OpenAI

def ask_openai(query, client, prompt):

    if client is None:
        return "❌ OpenAI API Key Missing"

    print("➡️ Sending request to OpenAI...")

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": prompt.format(query=query)
                }
            ]
        )

        answer = response.choices[0].message.content

        print("✅ Response received from OpenAI")

        return answer

    except Exception as e:
        print("❌ OpenAI Error:", str(e))
        return f"OpenAI Error: {str(e)}"
