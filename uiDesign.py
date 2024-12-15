import flet as ft
import requests
import urllib3
import base64
import prettytable

urlArray = []

# get tokens
def getTokens():
    # Reading file 
    file1 = open("C:\\Users\\Em\\AppData\\Local\\Riot Games\\Riot Client\\Config\\lockfile", "r")
    val = file1.read().split(':') 

     # Disable unverfied warnings 
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    #Get authentication token & val[2] is a port number
    url = f"https://127.0.0.1:{val[2]}/entitlements/v1/token"

     # Encoded string to Base64
    encoded = base64.b64encode(f"riot:{val[3]}".encode())

    #Headers file's
    headers = {
        "User-Agent": "insomnia/10.1.1", 
        "Authorization": "Basic" + " " + str(encoded)[2:-1] 
    }

    response = requests.get(url,data = "", headers=headers, verify=False)
    response_json = response.json()
    access_token = response_json.get("accessToken") # Access Token
    entitlements_token = response_json.get("token") # Entitlement Token

    return access_token, entitlements_token

def getSkins(access_token, entitlements_token):
    # Getting store skin Id's and name
    url =  "https://pd.ap.a.pvp.net/store/v3/storefront/c75e41da-1911-571e-b1fb-0780b254e54f"

    # payload = ""
    headers = {
        "X-Riot-ClientPlatform": "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9",

        "X-Riot-Entitlements-JWT": entitlements_token,

        "X-Riot-ClientVersion": "release-09.08-shipping-7-2916535",

        "Authorization": "Bearer " + access_token
    }

    # sending post request to get skin's infomaration
    response = requests.request("POST", url, data="{}", headers=headers)
   
    response_json = response.json()

    SkinsPanelLayout_token = response_json.get("SkinsPanelLayout")
    SkinId_token =  SkinsPanelLayout_token.get("SingleItemOffers")
    S_token = SkinsPanelLayout_token.get("SingleItemStoreOffers")
    

    #Getting skin's Names, Id and Cost
    for i in range(0,4):
        url2 = "https://valorant-api.com/v1/weapons/skinlevels/"+SkinId_token[i]
        response1 = requests.request("GET", url2, data="", headers=headers)

        response1_json = response1.json()
        SkinName_token = response1_json.get("data")
        Skin_token = SkinName_token.get("displayName")  # Skin name
        urlArray.append(SkinName_token.get("displayIcon"))  # Skin image URL
        
        #Displaying Skin Name, Icon, and Cost
        # t.add_row([list(S_token[i]['Cost'].values())[0], Skin_token, Icon_token])

    # print(t)




# Ui Design

def main(page: ft.Page):
    page.title = "Valorant Skin Store"
    # Get Tokens
    access_token, entitlements_token = getTokens()

    # Get Skin information
    getSkins(access_token, entitlements_token)
    print(urlArray)

    page.add(
        ft.Row(
            [
                ft.Column(
                    [
                        ft.Container(
                            content=ft.Image(
                                src=urlArray[0], 
                                fit=ft.ImageFit.CONTAIN
                            ),
                            # content=ft.Text("hello"),
                            alignment=ft.alignment.center,
                            border=ft.border.all(1, "red"),
                            # pedding=0.5,
                            expand=True,
                        ),
                    ],
                    
                    expand=True,
                ),
                ft.Column(
                    [
                        ft.Container(
                            content=ft.Image(
                                src=urlArray[1],
                                fit=ft.ImageFit.CONTAIN
                            ),
                            # content=ft.Text("skin 2"),
                            alignment=ft.alignment.center,
                            border=ft.border.all(1, "red"),
                            # bgcolor="blue",
                            expand=True,
                        )
                    ],
                    expand=True,
                ),
            ],
            expand=True,
        ),
        ft.Row(
            [
                ft.Column(
                    [
                        ft.Container(
                            content=ft.Image(
                                src=urlArray[2],
                                fit=ft.ImageFit.CONTAIN
                            ),
                            # content=ft.Text("skin 3"),
                            alignment=ft.alignment.center,
                            border=ft.border.all(1, "red"),
                            # bgcolor="green",
                            expand=True,
                        )
                    ],
                    expand=True,
                ),
                ft.Column(
                    [
                        ft.Container(
                            content=ft.Image(
                                src=urlArray[3],
                                fit=ft.ImageFit.CONTAIN
                            ),

                            # content=ft.Text("skin 4"),
                            alignment=ft.alignment.center,
                            border=ft.border.all(1, "red"),
                            # bgcolor="yellow",
                            expand=True,
                        )
                    ],
                    expand=True,
                ),
            ],
            expand=True,
        ),
    )





ft.app(main)
