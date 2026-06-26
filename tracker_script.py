#!/usr/bin/env python3

import re
import json
from collections import defaultdict
from datetime import datetime

# ==========================================
# AI Bots & Platforms
# ==========================================

AI_PATTERNS = {

    # OpenAI
    "ChatGPT-User": r"ChatGPT-User",
    "GPTBot": r"GPTBot",
    "OAI-SearchBot": r"OAI-SearchBot",

    # Anthropic
    "ClaudeBot": r"ClaudeBot",
    "anthropic-ai": r"anthropic",

    # Google Gemini
    "Google-Extended": r"Google-Extended",
    "GoogleOther": r"GoogleOther",
    "Googlebot": r"Googlebot",

    # Perplexity
    "PerplexityBot": r"PerplexityBot",

    # Microsoft Copilot
    "bingbot": r"bingbot",

    # Meta
    "meta-externalagent": r"meta-externalagent",
    "meta-externalfetcher": r"meta-externalfetcher",

    # Common AI Crawlers
    "Bytespider": r"Bytespider",
    "CCBot": r"CCBot",
    "Amazonbot": r"Amazonbot",
    "Applebot": r"Applebot",

    # You.com
    "YouBot": r"YouBot",

    # Neeva
    "Neevabot": r"Neevabot",

    # DuckAssist
    "DuckAssistBot": r"DuckAssistBot",

}

# ==========================================
# AI Referrers
# ==========================================

AI_REFERRERS = {
    "chatgpt.com": "ChatGPT",
    "chat.openai.com": "ChatGPT",
    "openai.com": "OpenAI",
    "gemini.google.com": "Gemini",
    "bard.google.com": "Gemini",
    "perplexity.ai": "Perplexity",
    "claude.ai": "Claude",
    "copilot.microsoft.com": "Copilot",
    "you.com": "You.com",
}

# Apache Combined Log Regex
LOG_PATTERN = re.compile(
    r'(\S+) (\S+) (\S+) \[(.*?)\] "(.*?)" (\d+) (\S+) "(.*?)" "(.*?)"'
)


def detect_ai(user_agent, referer):
    detected = []

    # User-Agent Detection
    for name, pattern in AI_PATTERNS.items():
        if re.search(pattern, user_agent, re.IGNORECASE):
            detected.append(name)

    # Referrer Detection
    for domain, platform in AI_REFERRERS.items():
        if domain.lower() in referer.lower():
            detected.append(platform)

    return list(set(detected))


def parse_log(logfile):

    stats = defaultdict(int)
    details = []

    with open(logfile, "r", encoding="utf-8", errors="ignore") as f:

        for line in f:

            match = LOG_PATTERN.match(line)

            if not match:
                continue

            ip, _, _, date, request, status, size, referer, ua = match.groups()

            ai = detect_ai(ua, referer)

            if ai:

                for platform in ai:
                    stats[platform] += 1

                details.append({
                    "time": date,
                    "ip": ip,
                    "platform": ai,
                    "request": request,
                    "status": status,
                    "referer": referer,
                    "user_agent": ua
                })

    return stats, details


def print_report(stats):

    print("\n===============================")
    print(" AI TRAFFIC REPORT")
    print("===============================\n")

    total = 0

    for k, v in sorted(stats.items(), key=lambda x: x[1], reverse=True):
        total += v
        print(f"{k:25} {v}")

    print("\n-------------------------------")
    print(f"TOTAL AI REQUESTS : {total}")
    print("-------------------------------")


def export_json(details):

    filename = "ai_traffic_report.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(details, f, indent=4)

    print(f"\nDetailed report saved -> {filename}")


if __name__ == "__main__":

    logfile = input("Enter Apache/Nginx log path : ").strip()

    stats, details = parse_log(logfile)

    print_report(stats)

    export_json(details)
