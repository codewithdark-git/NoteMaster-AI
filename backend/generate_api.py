import secrets

def generate_api_key():
    return secrets.token_hex(32)

api_key = generate_api_key()

with open('api.env', 'w') as file:
    file.write(f"ApiKey={api_key}\n")