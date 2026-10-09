import os, sys

if os.path.exists(".env"):
    with open(".env") as f:
        for line in f:
            if "=" in line.strip() and not line.strip().startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ[k] = v

from google import genai

key = os.environ.get("GEMINI_API_KEY", "")
print(f"Key prefix: {key[:12]}...")
client = genai.Client(api_key=key)

print("\n--- Test 1: Embedding ---")
try:
    r = client.models.embed_content(model="gemini-embedding-2", contents="Hello test")
    print(f"  PASS: embedding length = {len(r.embeddings[0].values)}")
except Exception as e:
    print(f"  FAIL: {type(e).__name__}: {e}")

print("\n--- Test 2: Text Generation ---")
try:
    r2 = client.models.generate_content(
        model="gemini-3.5-flash",
        contents="Say hello in one word",
    )
    print(f"  PASS: response = {r2.text.strip()[:80]}")
except Exception as e:
    print(f"  FAIL: {type(e).__name__}: {e}")

print("\n--- Test 3: JSON Generation ---")
try:
    r3 = client.models.generate_content(
        model="gemini-3.5-flash",
        contents='Return valid JSON: {"status": "ok"}',
        config={"response_mime_type": "application/json"},
    )
    print(f"  PASS: json = {r3.text.strip()[:80]}")
except Exception as e:
    print(f"  FAIL: {type(e).__name__}: {e}")
