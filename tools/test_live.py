import urllib.request
import json

payload = {
    "source": {
        "type": "synthetic",
        "resolution": 512
    },
    "filter_key": "gaussian",
    "p_workers": 4,
    "warm_pool": True
}

req = urllib.request.Request(
    "http://127.0.0.1:8000/api/live/process",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)

res = urllib.request.urlopen(req)
data = json.loads(res.read().decode("utf-8"))

print("Live process status:", res.status)
print("Is identical:", data.get("is_identical"))
print("Max diff:", data.get("max_diff"))
print("Ts:", data.get("t_serial"), "Tp:", data.get("t_parallel"), "Speedup:", data.get("speedup"))
print("CPU util:", data.get("cpu_utilization"))
print("Images returned:", list(data.get("images", {}).keys()))
