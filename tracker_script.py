import os
import json
import csv
import openai
from datetime import datetime
from openai import OpenAI

try:
    from google import genai
except ImportError:
    genai = None

try:
    import anthropic
except ImportError:
    anthropic = None

import requests

# ==================================================
# VERSION INFO
# ==================================================

print("=" * 70)
print("🚀 MyAssignmentHelp AI Citation Tracker - VERSION 3")
print("OpenAI SDK Version:", openai.__version__)
print("=" * 70)

# ==================================================
# API CONFIGURATION
# ==================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
gemini_client = genai.Client(api_key=GEMINI_API_KEY) if (genai and GEMINI_API_KEY) else None
claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) if (anthropic and ANTHROPIC_API_KEY) else None

AUDIT_PROMPT_TEMPLATE = """
You are an AI Search Visibility Auditor.

Search Query:
{query}

Your task is to evaluate AI search visibility for MyAssignmentHelp.com.

Return ONLY in the following format:

1. Top 10 recommended websites (ranked).
2. Does MyAssignmentHelp.com appear? (Yes/No)
3. Exact ranking position of MyAssignmentHelp.com.
4. List every competitor mentioned.
5. Why each website was recommended.
6. Search intent (Informational / Commercial / Transactional).
7. Confidence Score (0-100).
8. Mention if citations or sources were used.
9. Short summary (max 50 words).

Keep the response structured.
"""

# ==================================================
# COMPETITOR HELPERS
# ==================================================

def load_competitors():
    if os.path.exists("competitors.json"):
        with open("competitors.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def find_mentioned_competitors(answer_text, competitors):
    """Case-insensitive substring match of each competitor domain inside the answer."""
    if not answer_text:
        return []
    lowered = answer_text.lower()
    return [c for c in competitors if c.lower() in lowered]


# ==================================================
# OPENAI FUNCTION
# ==================================================

def ask_openai(query):

    if openai_client is None:
        return "❌ OpenAI API Key Missing"

    print("➡️ Sending request to OpenAI...")

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4.1-mini",
            temperature=0,
            messages=[
                {"role": "user", "content": AUDIT_PROMPT_TEMPLATE.format(query=query)}
            ]
        )

        answer = response.choices[0].message.content

        print("✅ Response received from OpenAI")

        return answer

    except Exception as e:
        print("❌ OpenAI Error:", str(e))
        return f"OpenAI Error: {str(e)}"


# ==================================================
# GEMINI FUNCTION
# ==================================================

def ask_gemini(query):

    if gemini_client is None:
        return "❌ Gemini API Key Missing"

    print("➡️ Sending request to Gemini...")

    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=AUDIT_PROMPT_TEMPLATE.format(query=query)
        )

        answer = response.text

        print("✅ Response received from Gemini")

        return answer

    except Exception as e:
        print("❌ Gemini Error:", str(e))
        return f"Gemini Error: {str(e)}"


# ==================================================
# CLAUDE FUNCTION
# ==================================================

def ask_claude(query):

    if claude_client is None:
        return "❌ Claude API Key Missing"

    print("➡️ Sending request to Claude...")

    try:
        response = claude_client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=300,
            temperature=0,
            messages=[
                {"role": "user", "content": AUDIT_PROMPT_TEMPLATE.format(query=query)}
            ]
        )

        answer = "".join(
            block.text for block in response.content if block.type == "text"
        )

        print("✅ Response received from Claude")

        return answer

    except Exception as e:
        print("❌ Claude Error:", str(e))
        return f"Claude Error: {str(e)}"


# ==================================================
# PERPLEXITY FUNCTION
# ==================================================

def ask_perplexity(query):

    if not PERPLEXITY_API_KEY:
        return "❌ Perplexity API Key Missing"

    print("➡️ Sending request to Perplexity...")

    try:
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "sonar",
                "temperature": 0,
                "messages": [
                    {"role": "user", "content": AUDIT_PROMPT_TEMPLATE.format(query=query)}
                ]
            },
            timeout=60
        )

        response.raise_for_status()
        data = response.json()
        answer = data["choices"][0]["message"]["content"]

        print("✅ Response received from Perplexity")

        return answer

    except Exception as e:
        print("❌ Perplexity Error:", str(e))
        return f"Perplexity Error: {str(e)}"


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

    # Load Competitors

    competitors = load_competitors()

    # API Status

    print("Checking API Keys...\n")

    print(f"OpenAI     : {'✅ Found' if OPENAI_API_KEY else '❌ Missing'}")
    print(f"Gemini     : {'✅ Found' if GEMINI_API_KEY else '❌ Missing'}")
    print(f"Claude     : {'✅ Found' if ANTHROPIC_API_KEY else '❌ Missing'}")
    print(f"Perplexity : {'✅ Found' if PERPLEXITY_API_KEY else '❌ Missing'}")

    print(f"\nCompetitors Loaded : {len(competitors)}\n")

    print("\nStarting Multi-Engine Citation Audit...\n")

    results = []
    competitor_totals = {c: 0 for c in competitors}

    for index, query in enumerate(queries, start=1):

        print("=" * 70)
        print(f"{index}. {query}")
        print("=" * 70)

        openai_answer = ask_openai(query)
        print(openai_answer)
        print()

        gemini_answer = ask_gemini(query)
        print(gemini_answer)
        print()

        claude_answer = ask_claude(query)
        print(claude_answer)
        print()

        perplexity_answer = ask_perplexity(query)
        print(perplexity_answer)
        print()

        # Competitor detection per engine

        openai_competitors = find_mentioned_competitors(openai_answer, competitors)
        gemini_competitors = find_mentioned_competitors(gemini_answer, competitors)
        claude_competitors = find_mentioned_competitors(claude_answer, competitors)
        perplexity_competitors = find_mentioned_competitors(perplexity_answer, competitors)

        for engine_list in [
            openai_competitors,
            gemini_competitors,
            claude_competitors,
            perplexity_competitors,
        ]:
            for c in engine_list:
                competitor_totals[c] = competitor_totals.get(c, 0) + 1

        myassignmenthelp_found = (
            "myassignmenthelp.com" in openai_answer.lower()
            or "myassignmenthelp.com" in gemini_answer.lower()
            or "myassignmenthelp.com" in claude_answer.lower()
            or "myassignmenthelp.com" in perplexity_answer.lower()
        )

        results.append({
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Query": query,
            "MyAssignmentHelp Found": "Yes" if myassignmenthelp_found else "No",
            "OpenAI Response": openai_answer,
            "OpenAI Competitors Mentioned": ", ".join(openai_competitors),
            "Gemini Response": gemini_answer,
            "Gemini Competitors Mentioned": ", ".join(gemini_competitors),
            "Claude Response": claude_answer,
            "Claude Competitors Mentioned": ", ".join(claude_competitors),
            "Perplexity Response": perplexity_answer,
            "Perplexity Competitors Mentioned": ", ".join(perplexity_competitors),
        })
    # Save Output

       os.makedirs("output", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = f"output/audit_{timestamp}.csv"

    fieldnames = [
        "Date",
        "Query",
        "MyAssignmentHelp Found",
        "OpenAI Response",
        "OpenAI Competitors Mentioned",
        "Gemini Response",
        "Gemini Competitors Mentioned",
        "Claude Response",
        "Claude Competitors Mentioned",
        "Perplexity Response",
        "Perplexity Competitors Mentioned",
    ]

    with open(csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    json_path = f"output/audit_{timestamp}.json"

    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4, ensure_ascii=False)

    # Save competitor summary (mentions across all engines & queries)

    competitor_summary_path = f"output/competitor_summary_{timestamp}.json"

    sorted_summary = dict(
        sorted(competitor_totals.items(), key=lambda item: item[1], reverse=True)
    )

    with open(competitor_summary_path, "w", encoding="utf-8") as file:
        json.dump(sorted_summary, file, indent=4, ensure_ascii=False)

    print("=" * 70)
    print("✅ AUDIT COMPLETED SUCCESSFULLY")
    print("=" * 70)
    print("CSV Saved                :", csv_path)
    print("JSON Saved                :", json_path)
    print("Competitor Summary Saved  :", competitor_summary_path)
    print()
    print("Competitor Mention Totals (across all engines & queries):")
    for competitor, count in sorted_summary.items():
        print(f"  {competitor:30s} : {count}")


# ==================================================
# START
# ==================================================

if __name__ == "__main__":
    run_citation_audit()
