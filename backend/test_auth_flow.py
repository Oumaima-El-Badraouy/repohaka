import requests

BASE = 'http://127.0.0.1:5000'

# Login
resp = requests.post(f'{BASE}/api/auth/login', json={'email':'carol.student@uni.edu','password':'carolpass'})
print('LOGIN', resp.status_code, resp.text)

if resp.status_code == 200:
    data = resp.json()
    token = data.get('access_token')
    headers = {'Authorization': f'Bearer {token}'}
    me = requests.get(f'{BASE}/api/auth/me', headers=headers)
    print('ME', me.status_code, me.text)
else:
    print('Login failed; cannot test /me')
