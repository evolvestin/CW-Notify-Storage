import os
import requests
import concurrent.futures
import _thread
import objects


def glow():
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as future_executor:
        futures = [future_executor.submit(requests.get, future) for future in [517202]]
        for future in concurrent.futures.as_completed(futures):
            auth = objects.AuthCentre(os.environ['DEV-TOKEN'])
            auth.send_json(str(future.result()), 'file.html', 'html')
            _thread.exit()
