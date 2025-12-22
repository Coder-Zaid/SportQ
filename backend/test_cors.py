import requests

# Test CORS headers
response = requests.options('http://localhost:8002/api/rentals/create')
print("Status Code:", response.status_code)
print("Headers:", response.headers)

# Check if CORS headers are present
if 'access-control-allow-origin' in response.headers:
    print("CORS headers are present!")
    print("Allowed origins:", response.headers['access-control-allow-origin'])
else:
    print("CORS headers are missing!")