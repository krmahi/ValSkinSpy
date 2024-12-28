import flet as ft
import requests
import urllib3
import base64
import prettytable
import yaml

urlArray = []
nameArray = []
n = 19

cost = []
cs = str(cost)

s = str(n)


# get tokens
def getTokens():
    filePath = "C:\\Users\\Em\\AppData\\Local\\Riot Games\\Riot Client\\Data\\RiotGamesPrivateSettings.yaml"

    def get_accessToken(filePath):
        with open(filePath, "r") as f:
            data = yaml.full_load(f)
            return data["riot-login"]["persist"]["session"]["cookies"][1]["value"]

    ssid_value = get_accessToken(filePath)

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

    return access_token, entitlements_token


def getSkins(access_token, entitlements_token):
    # Getting store skin Id's and name
    url = "https://pd.ap.a.pvp.net/store/v3/storefront/c75e41da-1911-571e-b1fb-0780b254e54f"

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

        # Displaying Skin Name, Icon, and Cost
        # t.add_row([list(costs[i]['Cost'].values())[0], Skin_token, Icon_token])

    # print(t)


# Ui Design


def main(page: ft.Page):

    page.title = "Valorant Skin Store"
    page.window_icon = "c:\\Users\\Em\\Downloads\\LeagueofLegends_ArcaneJinx.ico"

    page.window_full_screen = False
    page.window_maximizable = True
    page.window_maximizable = True

    # Get Tokens
    access_token, entitlements_token = getTokens()

    # Get Skin information
    getSkins(access_token, entitlements_token)
    print(urlArray)

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
                        # ft.Text(s,font_family="VALORANT", size=18),
                        ft.Text(f"Cost: {cost[0]}", size=18, font_family="VALORANT"),
                    ]
                ),
                ft.Column(
                    [
                        ft.Container(
                            content=ft.Image(src=urlArray[0], fit=ft.ImageFit.CONTAIN),
                            # content=ft.Text("hello"),
                            alignment=ft.alignment.center,
                            # border=ft.border.all(1, "red"),
                            # pedding=0.5,
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
                                        # ft.Text(s,font_family="VALORANT", size=18),
                                    ]
                                ),
                               
                                # ft.Column(
                                #     [
                                #         # ft.Text(s,font_family="VALORANT", size=18),
                                #         ft.Text(f"Cost: {cost[0]}", size=18, font_family="VALORANT"),
                                #     ]
                                # )
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
                                # ft.Text(s,font_family="VALORANT", size=18),
                                ft.Text(
                                    f"Cost: {cost[1]}", size=18, font_family="VALORANT"
                                ),
                            ]
                        ),
                        ft.Container(
                            content=ft.Image(src=urlArray[1], fit=ft.ImageFit.CONTAIN),
                            # content=ft.Text("skin 2"),
                            alignment=ft.alignment.center,
                            # border=ft.border.all(1, "red"),
                            # bgcolor="blue",
                            expand=True,
                        ),
                        # ft.Text(nameArray[1],font_family="VALORANT", size=18),
                        ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text(
                                            nameArray[1],
                                            font_family="VALORANT",
                                            size=18,
                                        ),
                                        # ft.Text(s,font_family="VALORANT", size=18),
                                    ]
                                ),
                                # ft.Column(
                                #     [
                                #         # ft.Text(s,font_family="VALORANT", size=18),
                                #         ft.Text(f"                                       Cost: {cost[1]}", size=18, font_family="VALORANT"),
                                #     ]
                                # )
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
                        # ft.Text(s,font_family="VALORANT", size=18),
                        ft.Text(f"Cost: {cost[2]}", size=18, font_family="VALORANT"),
                    ]
                ),
                ft.Column(
                    [
                        ft.Container(
                            content=ft.Image(src=urlArray[2], fit=ft.ImageFit.CONTAIN),
                            # content=ft.Text("skin 3"),
                            alignment=ft.alignment.center,
                            # border=ft.border.all(1, "red"),
                            # bgcolor="green",
                            expand=True,
                        ),
                        # ft.Text(nameArray[2],font_family="VALORANT", size=18),
                        ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text(nameArray[2],
                                            font_family="VALORANT",
                                            size=18,
                                        ),
                                        # ft.Text(s,font_family="VALORANT", size=18),
                                    ]
                                ),
                                # ft.Column(
                                #     [
                                #         # ft.Text(s,font_family="VALORANT", size=18),
                                #         ft.Text(f"Cost: {cost[2]}", size=18, font_family="VALORANT"),
                                #     ]
                                # )
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
                                # ft.Text(s,font_family="VALORANT", size=18),
                                ft.Text(
                                    f"Cost: {cost[3]}", size=18, font_family="VALORANT"
                                ),
                            ]
                        ),
                        ft.Container(
                            content=ft.Image(src=urlArray[3], fit=ft.ImageFit.CONTAIN),
                            # content=ft.Text("skin 4"),
                            alignment=ft.alignment.center,
                            # border=ft.border.all(1, "red"),
                            # bgcolor="yellow",
                            expand=True,
                        ),
                        # ft.Text(nameArray[3],font_family="VALORANT", size=18),
                        ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text(
                                            nameArray[3],
                                            font_family="VALORANT",
                                            size=18,
                                        ),
                                        # ft.Text(s,font_family="VALORANT", size=18),
                                    ]
                                ),
                                # ft.Column(
                                #     [
                                #         # ft.Text(s,font_family="VALORANT", size=18),
                                #         ft.Text(f"Cost: {cost[3]}", size=18, font_family="VALORANT"),
                                #     ]
                                # )
                            ],
                        ),
                    ],
                    expand=True,
                ),
            ],
            expand=True,
        ),
    )


ft.app(main)
