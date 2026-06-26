import os
import json
import csv
from datetime import datetime

from openai import OpenAI

# =====================================
# API CONFIGURATION
# =====================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


# =====================================
# OPENAI FUNCTION
# =====================================

def ask_openai(query):

    if client is None:
        return "OpenAI API Key Missing"

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

1. Top recommended websites
2. Mention if myassignmenthelp.com appears
3. Rank Position
4. Short reason

Keep response under 200 words.
"""
                }
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"OpenAI Error : {e}"


# =====================================
# MAIN AUDIT
# =====================================

def run_citation_audit():

    print("=" * 70)
    print("MyAssignmentHelp AI Citation Tracker")
    print("=" * 70)
    print("Started :", datetime.now())
    print()

    # ------------------------
    # Load Queries
    # ------------------------

    if os.path.exists("queries.json"):

        with open("queries.json", "r", encoding="utf-8") as f:
            queries = json.load(f)

    else:

        queries = [
            "Best assignment help website",
            "Who can help me write my assignment?"
        ]

    # ------------------------
    # API STATUS
    # ------------------------

    print("Checking API Keys...\n")

    print(f"OpenAI      : {'✅ Found' if os.getenv('OPENAI_API_KEY') else '❌ Missing'}")
    print(f"Gemini      : {'✅ Found' if os.getenv('GEMINI_API_KEY') else '❌ Missing'}")
    print(f"Claude      : {'✅ Found' if os.getenv('ANTHROPIC_API_KEY') else '❌ Missing'}")
    print(f"Perplexity  : {'✅ Found' if os.getenv('PERPLEXITY_API_KEY') else '❌ Missing'}")

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

    # ------------------------
    # OUTPUT DIRECTORY
    # ------------------------

    os.makedirs("output", exist_ok=True)

    # CSV

    csv_file = "output/audit.csv"

    with open(csv_file, "w", newline="", encoding="utf-8") as file:

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

    # JSON Backup

    json_file = "output/audit.json"

    with open(json_file, "w", encoding="utf-8") as file:

        json.dump(
            results,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("=" * 70)
    print("✅ AUDIT COMPLETED SUCCESSFULLY")
    print("=" * 70)
    print("CSV  :", csv_file)
    print("JSON :", json_file)


# =====================================
# START
# =====================================

if __name__ == "__main__":
    run_citation_audit()
