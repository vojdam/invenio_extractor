import os
import multiprocessing


workers = int(os.environ.get("WEB_CONCURRENCY", multiprocessing.cpu_count() * 2))

threads = int(os.environ.get("PYTHON_MAX_THREADS", 1))


bind = os.environ.get("WEB_BIND", "0.0.0.0:8080")


forwarded_allow_ips = "*"

secure_scheme_headers = {"X-Forwarded-Proto": "https"}
