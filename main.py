import flet as ft
import requests
import os
import yaml
import math

localAppData = os.environ.get("localappdata")

# ---------------------- Token Handling ----------------------
def getTokens():
    filePath = localAppData + "\\Riot Games\\Riot Client\\Data\\RiotGamesPrivateSettings.yaml"

    def get_accessToken(filePath):
        with open(filePath, "r") as inFile:
            data = yaml.full_load(inFile)

        cookies = data["riot-login"]["persist"]["session"]["cookies"]
        ssid_cookie = next((c["value"] for c in cookies if c.get("name") == "ssid"), None)

        if not ssid_cookie:
            raise Exception("❌ No ssid cookie found. Please log into Riot Client first.")
        return ssid_cookie

    ssid_value = get_accessToken(filePath)

    regionPath = localAppData + "\\Riot Games\\Riot Client\\Config\\RiotClientSettings.yaml"
    with open(regionPath, "r") as inFile:
        region = yaml.full_load(inFile)

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
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {access_token}"}
    response = requests.post(url1, headers=headers)
    entitlements_token = response.json().get("entitlements_token")

    # PUUID
    url2 = "https://auth.riotgames.com/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url2, headers=headers)
    puuid = response.json().get("sub")

    return access_token, entitlements_token, puuid, region

def getClientVersion():
    try:
        res = requests.get("https://valorant-api.com/v1/version")
        data = res.json().get("data", {})
        return data.get("riotClientVersion", "release-0.0-shipping-0-0000000")  # fallback
    except Exception:
        return "release-0.0-shipping-0-0000000"


# ---------------------- Wallet Fetchers ----------------------
def getWallet(access_token, entitlements_token, puuid, region, client_version):
    url = f"https://pd.{region}.a.pvp.net/store/v1/wallet/{puuid}"
    headers = {
        "X-Riot-ClientPlatform": "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9",
        "X-Riot-Entitlements-JWT": entitlements_token,
        "X-Riot-ClientVersion": client_version,
        "Authorization": f"Bearer {access_token}",
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

# ---------------------- Store Fetchers ----------------------
def getStore(access_token, entitlements_token, puuid, region, client_version):
    url = f"https://pd.{region}.a.pvp.net/store/v3/storefront/{puuid}"
    headers = {
        "X-Riot-ClientPlatform": "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9",
        "X-Riot-Entitlements-JWT": entitlements_token,
        "X-Riot-ClientVersion": client_version,
        "Authorization": f"Bearer {access_token}",
    }

    response = requests.post(url, headers=headers, json={})
    return response.json()


def parseDaily(store_json):
    panel = store_json.get("SkinsPanelLayout", {})
    skin_ids = panel.get("SingleItemOffers", [])
    costs = panel.get("SingleItemStoreOffers", [])
    remaining = panel.get("SingleItemOffersRemainingDurationInSeconds", 0)

    skins = []
    for i, skin_id in enumerate(skin_ids):
        try:
            skin_url = f"https://valorant-api.com/v1/weapons/skinlevels/{skin_id}"
            res = requests.get(skin_url)
            skin_info = res.json().get("data", {})
            skins.append({
                "name": skin_info.get("displayName", "Unknown"),
                "icon": skin_info.get("displayIcon"),
                "price": list(costs[i]["Cost"].values())[0] if i < len(costs) else 0
            })
        except Exception:
            continue

    return skins, remaining


def parseBundles(store_json):
    bundles = []
    if "FeaturedBundle" in store_json:
        fb = store_json["FeaturedBundle"]
        for b in fb.get("Bundles", []):
            bundles.append({
                "data": b,
                "remaining": b.get("DurationRemainingInSeconds", 0),
                "items": b.get("Items", []),
            })

    parsed = []
    for b in bundles:
        bundle_info = b["data"]
        items = b["items"]

        # Resolve bundle name
        bundle_id = bundle_info.get("DataAssetID")
        bundle_name = "Bundle"
        try:
            res = requests.get(f"https://valorant-api.com/v1/bundles/{bundle_id}")
            bundle_name = res.json().get("data", {}).get("displayName", "Featured Bundle")
        except Exception:
            pass

        # Total bundle price
        total_price = bundle_info.get("TotalDiscountedCost") or bundle_info.get("TotalBaseCost") or {}
        bundle_price = list(total_price.values())[0] if total_price else 0

        skins = []
        for item in items:
            # ✅ Only weapons
            if item.get("Item", {}).get("ItemTypeID") != "e7c63390-eda7-46e0-bb7a-a6abdacd2433":
                continue

            skin_id = item.get("Item", {}).get("ItemID")
            price = item.get("BasePrice", 0)

            skin_name = "Unknown Skin"
            skin_icon = None

            try:
                res = requests.get(f"https://valorant-api.com/v1/weapons/skinlevels/{skin_id}")
                if res.status_code == 200:
                    skin_data = res.json().get("data", {})
                    if skin_data:
                        skin_name = skin_data.get("displayName", "Unknown Skin")
                        skin_icon = skin_data.get("displayIcon")
            except Exception:
                pass

            if not skin_icon:
                skin_icon = "assets/images/icon_windows.png"

            skins.append({
                "name": skin_name,
                "icon": skin_icon,
                "price": price
            })

        parsed.append({
            "name": bundle_name,
            "skins": skins,
            "bundle_price": bundle_price,
            "remaining": b["remaining"]
        })

    return parsed


# ---------------------- Night Market Parser ----------------------
def parseNightMarket(store_json):
    nm = store_json.get("BonusStore")
    if not nm:
        return None

    offers = []
    for offer in nm.get("BonusStoreOffers", []):
        reward = offer["Offer"]["Rewards"][0]
        skin_id = reward["ItemID"]

        # Try fetching skin details
        skin_name = "Unknown Skin"
        skin_icon = None
        try:
            res = requests.get(f"https://valorant-api.com/v1/weapons/skinlevels/{skin_id}")
            if res.status_code == 200:
                data = res.json().get("data", {})
                skin_name = data.get("displayName", "Unknown Skin")
                skin_icon = data.get("displayIcon")
        except Exception:
            pass

        base_price = list(offer["Offer"]["Cost"].values())[0]
        discounted_price = list(offer["DiscountCosts"].values())[0]

        offers.append({
            "name": skin_name,
            "icon": skin_icon,
            "base_price": base_price,
            "discounted_price": discounted_price,
            "discount_percent": offer["DiscountPercent"],
        })

    return {"offers": offers, "remaining": nm.get("BonusStoreRemainingDurationInSeconds", 0)}


# ---------------------- Helpers ----------------------
def format_time(seconds):
    hours = math.floor(seconds / 3600)
    minutes = math.floor((seconds % 3600) / 60)
    sec = seconds % 60
    return f"{hours:02}:{minutes:02}:{sec:02}"


def make_wallet_bar(wallet_data):
    vp = wallet_data.get("Balances", {}).get("85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741", 0)   # Valorant Points
    rp = wallet_data.get("Balances", {}).get("e59aa87c-4cbf-517a-5983-6e81511be9b7", 0)   # Radianite Points
    kc = wallet_data.get("Balances", {}).get("85ca954a-41f2-ce94-9b45-8ca3dd39a00d", 0)   # Kingdom Credits

    return ft.Container(
        bgcolor="#0f1923",  
        padding=15,
        border_radius=15,
        margin=ft.margin.only(bottom=20),
        content=ft.Row(
            [
                ft.Text("Your Wallet", size=22, weight="bold", color="#f1f5f9"),
                ft.Container(expand=True),
                ft.Row([ft.Image(src="assets/images/VP.png", width=24, height=24), ft.Text(f"{vp:,}", size=18, weight="bold", color="#fbbf24")]),
                ft.Container(width=15),
                ft.Row([ft.Image(src="assets/images/RP.png", width=24, height=24), ft.Text(f"{rp:,}", size=18, weight="bold", color="#38bdf8")]),
                ft.Container(width=15),
                ft.Row([ft.Image(src="assets/images/KC.png", width=24, height=24), ft.Text(f"{kc:,}", size=18, weight="bold", color="#a78bfa")]),
            ],
            alignment="spaceBetween",
        ),
    )


def make_store_section(title, skins, remaining, extra_text=None):
    return ft.Container(
        bgcolor="#0f1923",  
        padding=20,
        border_radius=15,
        content=ft.Column(
            [
                ft.Row(
                    [ft.Text(title, size=24, weight="bold", color="#ff4655"), ft.Container(expand=True), ft.Text(format_time(remaining), size=16, color="#ffffff")],
                    alignment="spaceBetween",
                ),
                ft.Row(
                    [
                        ft.Container(
                            bgcolor="#1f2a36",  
                            border_radius=10,
                            padding=10,
                            width=200,
                            content=ft.Column(
                                [
                                    ft.Image(skin["icon"], height=120, fit=ft.ImageFit.CONTAIN),
                                    ft.Text(skin["name"], size=16, color="#ffffff", weight="bold", text_align="center"),
                                    ft.Text(str(skin["price"]), size=14, color="#ffd700", text_align="center"),
                                ],
                                horizontal_alignment="center",
                                spacing=5,
                            ),
                        )
                        for skin in skins if skin["icon"]
                    ],
                    wrap=True,
                    spacing=15,
                ),
                ft.Text(extra_text or "", size=18, weight="bold", color="#50fa7b"),
            ],
            spacing=15,
        ),
    )


def make_night_market_section(nm):
    return ft.Container(
        bgcolor="#1a1f2e",
        padding=20,
        border_radius=15,
        margin=ft.margin.only(bottom=20),
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("🃏 Night Market", size=24, weight="bold", color="#c084fc"),
                        ft.Container(expand=True),
                        ft.Text(format_time(nm["remaining"]), size=16, color="#ffffff"),
                    ],
                    alignment="spaceBetween",
                ),
                ft.Row(
                    [
                        ft.Container(
                            bgcolor="#2a2f45",
                            border_radius=10,
                            padding=10,
                            width=200,
                            content=ft.Column(
                                [
                                    ft.Image(offer["icon"], height=120, fit=ft.ImageFit.CONTAIN),
                                    ft.Text(offer["name"], size=16, color="#ffffff", weight="bold", text_align="center"),
                                    ft.Text(f"{offer['discounted_price']:,} VP", size=14, color="#50fa7b", text_align="center"),
                                    ft.Text(f"(was {offer['base_price']:,} VP, -{offer['discount_percent']}%)", size=12, color="#f87171", italic=True, text_align="center"),
                                ],
                                horizontal_alignment="center",
                                spacing=5,
                            ),
                        )
                        for offer in nm["offers"] if offer["icon"]
                    ],
                    wrap=True,
                    spacing=15,
                ),
            ],
            spacing=15,
        ),
    )


# ---------------------- Main App ----------------------
def main(page: ft.Page):
    page.title = "ValStore"
    page.scroll = "auto"

    try:
        access_token, entitlements_token, puuid, region = getTokens()
        client_version = getClientVersion()

        wallet_data = getWallet(access_token, entitlements_token, puuid, region, client_version)
        page.add(make_wallet_bar(wallet_data))

        store_json = getStore(access_token, entitlements_token, puuid, region, client_version)

        # Night Market first
        night_market = parseNightMarket(store_json)
        if night_market:
            page.add(make_night_market_section(night_market))

        # Bundles
        bundles = parseBundles(store_json)
        for bundle in bundles:
            page.add(
                make_store_section(
                    bundle["name"],
                    bundle["skins"],
                    bundle["remaining"],
                    extra_text=f"Total Bundle Price: {bundle['bundle_price']:,} VP"
                ),
                ft.Divider(height=20, color="transparent"),
            )

        # Daily
        daily_skins, daily_remaining = parseDaily(store_json)
        page.add(make_store_section("Daily Store", daily_skins, daily_remaining))

    except Exception as e:
        page.add(ft.Text(f"❌ Error: {e}", color="red", size=20))
        return


ft.app(main, assets_dir="assets")