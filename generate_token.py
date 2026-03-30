from kiteconnect import KiteConnect

API_KEY = "paste api key here"
API_SECRET = "paste secret key here"

kite = KiteConnect(api_key=API_KEY)

print("Login URL:", kite.login_url())

request_token = input("Paste request_token here: ")

data = kite.generate_session(request_token, api_secret=API_SECRET)

print("Access Token:", data["access_token"])