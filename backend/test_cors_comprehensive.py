import requests

# Test CORS headers with a POST request simulation
headers = {
    'Origin': 'http://localhost:3000',
    'Access-Control-Request-Method': 'POST',
    'Access-Control-Request-Headers': 'content-type, authorization',
}

try:
    # Send an OPTIONS request to simulate a CORS preflight
    response = requests.options('http://localhost:8002/api/rentals/create', headers=headers)
    print("OPTIONS Request Status Code:", response.status_code)
    print("OPTIONS Response Headers:")
    for key, value in response.headers.items():
        print(f"  {key}: {value}")
        
    # Check for CORS headers
    cors_headers = ['access-control-allow-origin', 'access-control-allow-methods', 'access-control-allow-headers']
    found_cors_headers = [header for header in cors_headers if header in [k.lower() for k in response.headers.keys()]]
    
    if found_cors_headers:
        print("\nFound CORS headers:", found_cors_headers)
    else:
        print("\nNo CORS headers found in OPTIONS response")
        
except Exception as e:
    print(f"Error during OPTIONS request: {e}")

print("\n" + "="*50 + "\n")

# Also test with a direct POST request with Origin header
try:
    test_data = {
        "gear_id": "test-gear-id",
        "quantity": 1
    }
    
    post_headers = {
        'Origin': 'http://localhost:3000',
        'Content-Type': 'application/json'
    }
    
    response = requests.post('http://localhost:8002/api/rentals/create', json=test_data, headers=post_headers)
    print("POST Request Status Code:", response.status_code)
    print("POST Response Headers:")
    for key, value in response.headers.items():
        print(f"  {key}: {value}")
        
    # Check for CORS headers in POST response
    cors_origin_header = [k for k in response.headers.keys() if k.lower() == 'access-control-allow-origin']
    if cors_origin_header:
        print(f"\nCORS Allow-Origin header found: {response.headers[cors_origin_header[0]]}")
    else:
        print("\nNo CORS Allow-Origin header found in POST response")
        
except Exception as e:
    print(f"Error during POST request: {e}")