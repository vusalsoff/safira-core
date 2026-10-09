import os, json, time
import requests

OLLAMA_BASE_URL = "http://localhost:11434"
MODEL = "qwen2.5:3b"

print("=== PHASE 1: Ollama Verification ===")

# Test 1: Is Ollama reachable?
print("\n[1] Checking Ollama server...")
try:
    r = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
    models = [m["name"] for m in r.json().get("models", [])]
    print(f"  PASS: Ollama running. Models available: {models}")
    if MODEL not in models:
        print(f"  WARN: {MODEL} not yet downloaded. Run: ollama pull {MODEL}")
except Exception as e:
    print(f"  FAIL: Ollama not reachable: {e}")
    exit(1)

# Test 2: Plain text generation latency
print(f"\n[2] Text generation latency test ({MODEL})...")
start = time.time()
payload = {"model": MODEL, "prompt": "Say hello in one sentence.", "stream": False}
try:
    r = requests.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload, timeout=120)
    elapsed = (time.time() - start) * 1000
    text = r.json().get("response", "").strip()
    print(f"  PASS: Response in {elapsed:.0f}ms: {text[:80]}")
except Exception as e:
    print(f"  FAIL: {e}")
    exit(1)

# Test 3: JSON output with SAFIRA ingest schema
print(f"\n[3] JSON schema test (SAFIRA ingest schema)...")
prompt = """You must respond ONLY with a valid JSON object. No explanation, no markdown, no code blocks. Raw JSON only.

You are SAFIRA Data Architect. Analyze this knowledge:
Content: "DNA double helix structure determines genetic inheritance."
Context: "Biology"
Library purpose: "Scientific research AI for life sciences."

Return JSON ONLY with exactly these keys:
{"extracted_meaning": "string", "placements": [{"type": "new", "name": "string", "description": "string", "parent_id": null}]}"""

start = time.time()
payload2 = {"model": MODEL, "prompt": prompt, "stream": False, "format": "json"}
try:
    r2 = requests.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload2, timeout=120)
    elapsed2 = (time.time() - start) * 1000
    raw = r2.json().get("response", "{}")
    parsed = json.loads(raw)
    has_meaning = "extracted_meaning" in parsed
    has_placements = "placements" in parsed
    print(f"  PASS: JSON parsed in {elapsed2:.0f}ms")
    print(f"  extracted_meaning present: {has_meaning}")
    print(f"  placements present: {has_placements}")
    print(f"  Sample meaning: {str(parsed.get('extracted_meaning',''))[:100]}")
except json.JSONDecodeError as e:
    print(f"  FAIL: Invalid JSON: {e}. Raw: {raw[:200]}")
except Exception as e:
    print(f"  FAIL: {e}")

# Test 4: RAM usage
print(f"\n[4] System RAM snapshot...")
import subprocess
result = subprocess.run(
    ["powershell", "-Command", "(Get-WmiObject Win32_OperatingSystem).FreePhysicalMemory / 1MB"],
    capture_output=True, text=True, timeout=10
)
free_gb = round(float(result.stdout.strip()), 2)
print(f"  Free RAM now: {free_gb:.2f} GB")

print("\n=== Verification Complete ===")
