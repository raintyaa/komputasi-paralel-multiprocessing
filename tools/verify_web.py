import urllib.request
import json

urls = [
    '/',
    '/static/css/tokens.css',
    '/static/css/style.css',
    '/static/js/icons.js',
    '/static/assets/vendor/chart.umd.min.js',
    '/static/assets/vendor/tailwind-play.js',
    '/static/js/app.js',
    '/static/js/live.js',
    '/static/js/benchmark.js',
    '/static/js/charts.js',
    '/api/system/specs',
    '/api/live/config',
    '/api/live/dataset/1024',
    '/api/benchmark/config',
    '/api/benchmark/results/latest',
    '/api/benchmark/results/summary'
]

for u in urls:
    try:
        res = urllib.request.urlopen("http://127.0.0.1:8000" + u)
        print(f"[OK 200] {u} ({len(res.read())} bytes)")
    except Exception as e:
        print(f"[FAIL] {u} -> {e}")
