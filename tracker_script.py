import os
import json
import csv
import openai
from datetime import datetime
from openai import OpenAI

# ==================================================
# VERSION INFO
# ==================================================

print("=" * 70)
print("🚀 MyAssignmentHelp AI Citation Tracker - VERSION 2")
print("OpenAI SDK Version:", openai.__version__)
print("=" * 70)

# ==================================================
# API CONFIGURATION
# ==================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# ==================================================
# OPENAI FUNCTION
# ==================================================

def ask_openai(query):

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
                    "content": f"""
You are an AI Search Auditor.

Search Query:
{query}

Return ONLY:

1. Top 5 recommended websites.
2. Mention if myassignmenthelp.com appears.
3. Rank Position.
4. One short reason.

Maximum 150 words.
"""
                }
            ]
        )

        answer = response.choices[0].message.content

        print("✅ Response received from OpenAI")

        return answer

    except Exception as e:

        print("❌ OpenAI Error:", str(e))

        return f"OpenAI Error: {str(e)}"

# ==================================================
# MAIN AUDIT
# ==================================================

def run_citation_audit():

    print()
    print("=" * 70)
    print("MyAssignmentHelp AI Citation Tracker")
    print("=" * 70)
    print("Started :", datetime.now())
    print()

    # Load Queries

    if os.path.exists("queries.json"):

        with open("queries.json", "r", encoding="utf-8") as f:
            queries = json.load(f)

    else:

        queries = [
            "Best assignment help website",
            "Who can help me write my assignment?"
        ]

    # API Status

    print("Checking API Keys...\n")

    print(f"OpenAI     : {'✅ Found' if os.getenv('OPENAI_API_KEY') else '❌ Missing'}")
    print(f"Gemini     : {'✅ Found' if os.getenv('GEMINI_API_KEY') else '❌ Missing'}")
    print(f"Claude     : {'✅ Found' if os.getenv('ANTHROPIC_API_KEY') else '❌ Missing'}")
    print(f"Perplexity : {'✅ Found' if os.getenv('PERPLEXITY_API_KEY') else '❌ Missing'}")

    print("\nStarting OpenAI Citation Audit...\n")

    results = []

    for index, query in enumerate(queries, start=1):

        print("=" * 70)
        print(f"{index}. {query}")
        print("=" * 70)

        answer = ask_openai(query)

        print(answer)
        print()

        results.append({
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Query": query,
            "OpenAI Response": answer
        })

    # Save Output

    os.makedirs("output", exist_ok=True)

    csv_path = "output/audit.csv"

    with open(csv_path, "w", newline="", encoding="utf-8") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "Date",
                "Query",
                "OpenAI Response"
            ]
        )

        writer.writeheader()
        writer.writerows(results)

    json_path = "output/audit.json"

    with open(json_path, "w", encoding="utf-8") as file:

        json.dump(
            results,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("=" * 70)
    print("✅ AUDIT COMPLETED SUCCESSFULLY")
    print("=" * 70)
    print("CSV Saved  :", csv_path)
    print("JSON Saved :", json_path)

# ==================================================
# START
# ==================================================

if __name__ == "__main__":
    run_citation_audit()
