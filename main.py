import flet as ft
import requests
import urllib3
import base64
import os

# import prettytable
import yaml

urlArray = []
nameArray = []
cost = []

localAppData = os.environ.get("localappdata")

# get tokens
def getTokens():
    # for accessToken
    filePath = localAppData+"\\Riot Games\\Riot Client\\Data\\RiotGamesPrivateSettings.yaml"

    def get_accessToken(filePath):
        inFile = open(filePath, "r")
        data = yaml.full_load(inFile)
        inFile.close()
        return data["riot-login"]["persist"]["session"]["cookies"][1]["value"]
        
    ssid_value = get_accessToken(filePath)

    regionPath = localAppData + "\\Riot Games\\Riot Client\\Config\\RiotClientSettings.yaml"

    inFile = open(regionPath, "r")
    region = yaml.full_load(inFile)
    inFile.close()

    region = region["install"]["player-affinity"]["product"]["valorant"]["live"]

    # ACCESS TOKEN
    url = "https://auth.riotgames.com/authorize?redirect_uri=https%3A%2F%2Fplayvalorant.com%2Fopt_in&client_id=play-valorant-web-prod&response_type=token%20id_token&nonce=1&scope=account%20openid"

    cookies = {"ssid": ssid_value}

    response = requests.get(url, cookies=cookies)
    start = response.url.find("access_token=") + len("access_token=")
    end = response.url.find("&", start)
    access_token = response.url[start:end]

    # ENTITLEMENT TOKEN
    url1 = "https://entitlements.auth.riotgames.com/api/token/v1"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    response = requests.post(url1, headers=headers)
    response_json = response.json()
    entitlements_token = response_json.get("entitlements_token")

    # puuid
    url2 = "https://auth.riotgames.com/userinfo"

    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    # requests.get = requests.get(url2, headers=headers)
    response = requests.request("get", url2, headers=headers)

    response_json = response.json()
    # print(response_json)
    puuid = response_json.get("sub")
    
    return access_token, entitlements_token, puuid, region

def getSkins(access_token, entitlements_token, puuid, region):
   
    # Getting store skin Id's and name
    url = f"https://pd.{region}.a.pvp.net/store/v3/storefront/{puuid}"

    # payload = ""
    headers = {
        "X-Riot-ClientPlatform": "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9",
        "X-Riot-Entitlements-JWT": entitlements_token,
        "X-Riot-ClientVersion": "release-09.08-shipping-7-2916535",
        "Authorization": f"Bearer {access_token}",
    }

    # sending post request to get skin's infomaration
    response = requests.request("POST", url, data="{}", headers=headers)
    response_json = response.json()

    SkinsPanelLayout_token = response_json.get("SkinsPanelLayout")
    SkinId_token = SkinsPanelLayout_token.get("SingleItemOffers")
    costs = SkinsPanelLayout_token.get("SingleItemStoreOffers")


    # Getting skin's Names, Id and Cost
    for i in range(0, 4):
        url2 = "https://valorant-api.com/v1/weapons/skinlevels/" + SkinId_token[i]
        response1 = requests.request("GET", url2, data="", headers=headers)

        response1_json = response1.json()
        SkinName_token = response1_json.get("data")
        nameArray.append(SkinName_token.get("displayName"))  # Skin name
        urlArray.append(SkinName_token.get("displayIcon"))  # Skin image URL
        cost.append(list(costs[i]["Cost"].values())[0])


# Ui Design
def main(page: ft.Page):
    page.title = "ValSkinSpy"

    page.fonts = {
        "VALORANT": "/fonts/VALORANT.ttf"
    }

    page.window_full_screen = False
    page.window_maximizable = True
    page.window_maximizable = True

    # Get Tokens
    access_token, entitlements_token, puuid, region = getTokens()

    # Get Skin information
    getSkins(access_token, entitlements_token, puuid, region)

    # Keyboard event handler
    def on_keyboard_event(event: ft.KeyboardEvent):
        if event.key == "F":
            page.window_full_screen = True
            page.update()

        elif event.key == "M":
            page.window_minimized = True
            page.update()

        elif event.key == "Escape":
            page.window_close()

    page.on_keyboard_event = on_keyboard_event

    # page.on_keyboard_event = on_keyboard_event

    page.add(
        ft.Row(
            [
                ft.Column(
                    [
                        ft.Column(
                            [
                                ft.Text(
                                    f"Cost: {cost[0]}", size=18, font_family="VALORANT"
                                ),
                            ]
                        ),
                        ft.Container(
                            content=ft.Image(src=urlArray[0], fit=ft.ImageFit.CONTAIN),
                            alignment=ft.alignment.center,
                            expand=True,
                        ),
                        ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text(
                                            nameArray[0],
                                            font_family="VALORANT",
                                            size=18,
                                        ),
                                    ]
                                ),
                            ],
                        ),
                    ],
                    expand=True,
                ),
                ft.VerticalDivider(color="red"),
                ft.Column(
                    [
                        ft.Column(
                            [
                                ft.Text(
                                    f"Cost: {cost[1]}", size=18, font_family="VALORANT"
                                ),
                            ]
                        ),
                        ft.Container(
                            content=ft.Image(src=urlArray[1], fit=ft.ImageFit.CONTAIN),
                            alignment=ft.alignment.center,
                            expand=True,
                        ),
                        ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text(
                                            nameArray[1],
                                            font_family="VALORANT",
                                            size=18,
                                        ),
                                    ]
                                ),
                            ],
                        ),
                    ],
                    expand=True,
                ),
            ],
            expand=True,
        ),
        ft.Divider(color="red"),
        ft.Row(
            [
                ft.Column(
                    [
                        ft.Column(
                            [
                                ft.Text(
                                    f"Cost: {cost[2]}", size=18, font_family="VALORANT"
                                ),
                            ]
                        ),
                        ft.Container(
                            content=ft.Image(src=urlArray[2], fit=ft.ImageFit.CONTAIN),
                            alignment=ft.alignment.center,
                            expand=True,
                        ),
                        ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text(
                                            nameArray[2],
                                            font_family="VALORANT",
                                            size=18,
                                        ),
                                    ]
                                ),
                            ],
                        ),
                    ],
                    expand=True,
                ),
                ft.VerticalDivider(color="red"),
                ft.Column(
                    [
                        ft.Column(
                            [
                                ft.Text(
                                    f"Cost: {cost[3]}", size=18, font_family="VALORANT"
                                ),
                            ]
                        ),
                        ft.Container(
                            content=ft.Image(src=urlArray[3], fit=ft.ImageFit.CONTAIN),
                            alignment=ft.alignment.center,
                            expand=True,
                        ),
                        ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text(
                                            nameArray[3],
                                            font_family="VALORANT",
                                            size=18,
                                        ),
                                    ]
                                ),
                            ],
                        ),
                    ],
                    expand=True,
                ),
            ],
            expand=True,
        ),
    )


ft.app(main, assets_dir="assets")
