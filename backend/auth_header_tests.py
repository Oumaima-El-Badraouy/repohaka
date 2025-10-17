import requests
BASE='http://127.0.0.1:5000'

print('No auth:')
resp = requests.get(f'{BASE}/api/auth/me')
print(resp.status_code, resp.text)

print('\nEmptyBearer:')
resp = requests.get(f'{BASE}/api/auth/me', headers={'Authorization':'Bearer '})
print(resp.status_code, resp.text)

print('\nMalformed bearer:')
resp = requests.get(f'{BASE}/api/auth/me', headers={'Authorization':'Bearer abc.def.ghi'})
print(resp.status_code, resp.text)
