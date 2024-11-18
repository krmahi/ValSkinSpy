import requests
import urllib3
import base64

file1 = open("C:\\Users\\Em\\AppData\\Local\\Riot Games\\Riot Client\\Config\\lockfile", "r")
val = file1.read().split(':')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = f"https://127.0.0.1:{val[2]}/entitlements/v1/token"

encoded = base64.b64encode(f"riot:{val[3]}".encode())
 
payload = ""    
headers = {
    "User-Agent": "insomnia/10.1.1",
    # "User-Agent": "Mozilla/5.0",
    # "Authorization": "Basic cmlvdDpNUlBoc3cxTlN1UFJEQnpBYmNxNm1nCg=="
    "Authorization": "Basic" + " " + str(encoded)[2:-1]
}

response = requests.get(url,data=payload, headers=headers, verify=False)

if response.status_code == 200:
    response_json = response.json()
    access_token = response_json.get("accessToken")
    entitlements_token = response_json.get("token")


# print(response.text)
print("Access Token: Bearer", access_token)
print("\n")
print("Entitlements Token:", entitlements_token)
