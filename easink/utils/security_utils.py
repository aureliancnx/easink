import binascii
import os
import time
from array import array

limits = {}

# API RateLimit system.
def rate_limited(request, endpoint, timestamp):
    key_name = endpoint + get_client_ip(request)

    if key_name in limits and limits[key_name] > time.time():
        return True;

    limits[key_name] = time.time() + timestamp

    return False

# Get user IP address
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    return ip

def generate_token():
    return binascii.hexlify(os.urandom(16)).decode('utf-8')
