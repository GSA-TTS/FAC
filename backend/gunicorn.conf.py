# worker configurations
workers = 4
worker_class = "gthread"
threads = 20  # Total concurrency = 4 workers * 20 threads = 80 concurrent requests

# request management
max_requests = 500
max_requests_jitter = 50
timeout = 240

# NOTE: The post_fork hook and psycogreen imports have been completely removed.
# true threads do not require greenlet monkey-patching for database drivers.
