import aiohttp
import asyncio
import sys

"""
  Load testing for the FAC API
"""

async def fetch_url(session, url, stop_event):
  """ Does a single request; halts all on non-200 """
  if stop_event.is_set():
    return None

  try:
    async with session.get(url) as response:
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

async def run_load_test(url, total_requests):
  stop_event = asyncio.Event()

  session_headers = {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiYXBpX2ZhY19nb3YiLCJjcmVhdGVkIjoiMjAyMy0wOS0xOVQxMDowMToxMi4zNTkzNTEifQ.uHOTzHp7sN_8tLftFYcva-5m6CQMrauY0DyIPAIZXpw',
    'X-Api-Key': 'R7SYmSzraSfsF9OvgwxadjjmfSUg3TgdKZP7KbuI',
    'Accept-Profile': 'api_v1_1_0',
  }

  async with aiohttp.ClientSession(headers=session_headers) as session:
    req_tasks = []

    for _ in range(total_requests):
      req_tasks.append(fetch_url(session, url, stop_event))

    results = await asyncio.gather(*req_tasks)

    if stop_event.is_set():
      print("\n--- TEST ABORTED DUE TO ERROR ---")
    else:
      print("\n--- Load Test Complete ---")

    success_count = len([r for r in results if r == 200])
    print(f"Successful (200 OK): {success_count}")

if __name__ == "__main__":
  allowed_envs = ["local", "preview", "dev", "staging"]
  env = sys.argv[1]

  if env not in allowed_envs:
    print(f"Allowed envs are {allowed_envs}")
    sys.exit(1)

  total_requests = int(sys.argv[2])

  if env == "local":
    target_url = "http://localhost:3000/general?report_id=eq.2026-06-GSAFAC-0000027412"
  else:
    target_url = f"https://api-{env}.fac.gov/general?report_id=eq.2026-06-GSAFAC-0000027412"

  print(f"Targeting {target_url} with {total_requests} requests")

  asyncio.run(run_load_test(target_url, total_requests))
