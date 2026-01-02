from openai import OpenAI

client = OpenAI(api_key="sk-aQpnfpf9xb4_QVPHSYGc1wSjwABJs-NgFMmUZsTGQ2T3BlbkFJ8Z7K4NnjeAnYQx7rtQNe861Hjp0Uai5ovXQfko5lYA")

try:
    models = client.models.list()
    print("✅ API key is VALID and working")
    print(f"Models accessible: {len(models.data)}")
except Exception as e:
    print("❌ API key test FAILED")
    print(e)
