import requests

API_KEY = "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"  # replace with your real key

print("🤖 Insurance AI Chatbot (Perplexity)")
print("Type anything. Type 'exit' to quit.\n")

url = "https://api.perplexity.ai/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        print("Bot: Goodbye 👋")
        break

    payload = {
        "model": "sonar-pro",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an insurance AI assistant helping with claims triage, "
                    "fraud risk assessment, and policy questions. "
                    "Always recommend human review for fraud flags."
                )
            },
            {
                "role": "user",
                "content": user_input
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        answer = response.json()["choices"][0]["message"]["content"]
        print("Bot:", answer, "\n")

    except requests.exceptions.HTTPError as e:
        error_text = response.text.lower()

        if "quota" in error_text or "429" in error_text:
            print("Bot: ❌ No credits left. Please check billing.")
        elif "invalid" in error_text or "auth" in error_text:
            print("Bot: ❌ Invalid API key.")
        elif "rate" in error_text:
            print("Bot: ⏳ Rate limited. Please wait.")
        else:
            print("Bot: ⚠️ API error:", response.text)

    except Exception as e:
        print("Bot: ⚠️ System error:", str(e))
