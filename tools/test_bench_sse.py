import urllib.request
import json

payload = {
    "basis": "synthetic",
    "mode": "quick",
    "scenarios": ["A"]
}

req = urllib.request.Request(
    "http://127.0.0.1:8000/api/benchmark/run",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)

res = urllib.request.urlopen(req)
print("Benchmark stream status:", res.status)

events = []
buffer = ""
for chunk in iter(lambda: res.read(1024), b""):
    buffer += chunk.decode("utf-8")
    while "\n\n" in buffer:
        part, buffer = buffer.split("\n\n", 1)
        for line in part.splitlines():
            if line.startswith("data:"):
                events.append(json.loads(line[5:].strip()))

print(f"Total SSE events received: {len(events)}")
types = [e.get("type") for e in events]
print("Event sequence:", types[:5], "...", types[-3:])
if "progress" in types:
    sample = next(e for e in events if e.get("type") == "progress")
    print("Sample progress record:", sample.get("record"))
