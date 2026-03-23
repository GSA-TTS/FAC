import aiohttp
import asyncio
import time
import argparse


parser = argparse.ArgumentParser(description="Load testing for the FAC")


async def fetch_url(url, body, session, stop_event):
  """ Does a single API request; halts all on non-200 """
  if stop_event.is_set():
    return None

  if body:
    method = session.post
  else:
    method = session.get

  try:
    async with method(url, json=body) as response:
      status = response.status

      if status != 200:
        print(f"Received {status}; stopping")
        print(response)
        stop_event.set()
      else:
        print('.', end="")

      await response.release()

      return status
  except Exception as e:
    # Silently fail if we are already stopping
    if not stop_event.is_set():
      print(f"Request failed: {e}")

    return None


async def run_load_test(url, body, total_requests, headers):
  stop_event = asyncio.Event()

  async with aiohttp.ClientSession(headers=headers) as session:
    req_tasks = []

    for _ in range(total_requests):
      req_tasks.append(fetch_url(url, body, session, stop_event))

    results = await asyncio.gather(*req_tasks)

    if stop_event.is_set():
      print("\n--- TEST ABORTED DUE TO ERROR ---")
    else:
      print("\n--- Load Test Complete ---")

    success_count = len([r for r in results if r == 200])
    print(f"Successful (200 OK): {success_count}")


if __name__ == "__main__":
  parser.add_argument("--env", required=True, type=str, help="Environment", choices=["local", "preview", "dev", "staging"])
  parser.add_argument("--api_or_app", required=True, type=str, help="API or App", choices=["api", "app"])
  parser.add_argument("--total_requests", required=True, type=int, help="Number of requests to make")
  parser.add_argument("--jwt", required=False, type=str, help="JWT (API only)")
  parser.add_argument("--api_key", required=False, type=str, help="API key (API only)")
  parser.add_argument("--limit", required=False, type=int, help="API query limit (API only)")
  parser.add_argument("--year", required=False, type=int, help="Year to query (App only)")
  args = parser.parse_args()

  jwt = args.jwt
  api_key = args.api_key
  limit = args.limit
  api_or_app = args.api_or_app
  env = args.env
  total_requests = args.total_requests

  if api_or_app == "api":
    if env == "local":
      host = "http://localhost:3000"
    else:
      host = f"https://api-{env}.fac.gov"

    target_url = f"{host}/general?limit={limit}"
    body = {}
  else: # app
    if env == "local":
      host = "http://localhost:8000"
    else:
      host = f"https://fac-{env}.app.cloud.gov"

    url = f"{host}/dissemination/search"
    body = { "audit_year": "2024" }

  print(f"Targeting {url} with {total_requests} requests")

  if api_or_app == "api":
    headers = {
      'Authorization': f'Bearer {jwt}',
      'X-Api-Key': api_key,
      'Accept-Profile': 'api_v1_1_0',
    }
  else:
    headers = {}

  start_time = time.perf_counter()

  asyncio.run(run_load_test(url, body, total_requests, headers))

  end_time = time.perf_counter()

  elapsed_time = end_time - start_time
  print(f"Execution time: {elapsed_time:.4f} seconds")
