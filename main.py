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


# ---------------------- Store Fetchers ----------------------
def getStore(access_token, entitlements_token, puuid, region):
    """Fetch entire store JSON"""
    url = f"https://pd.{region}.a.pvp.net/store/v3/storefront/{puuid}"
    headers = {
        "X-Riot-ClientPlatform": "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9",
        "X-Riot-Entitlements-JWT": entitlements_token,
        "X-Riot-ClientVersion": "release-09.08-shipping-7-2916535",
        "Authorization": f"Bearer {access_token}",
    }

    response = requests.post(url, headers=headers, json={})
    return response.json()


def parseDaily(store_json):
    """Parse daily offers"""
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
    """Parse all available bundles (featured + others)"""
    bundles = []

    # 1) Featured bundle
    if "FeaturedBundle" in store_json:
        fb = store_json["FeaturedBundle"]
        bundle_info = fb.get("Bundle", {})
        bundles.append({
            "data": bundle_info,
            "remaining": fb.get("BundleRemainingDurationInSeconds", 0),
            "items": bundle_info.get("Items", []),
        })

    # 2) Other bundles
    for b in store_json.get("Bundles", []):
        bundles.append({
            "data": b,
            "remaining": b.get("BundleRemainingDurationInSeconds", 0),
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
            bundle_name = res.json().get("data", {}).get("displayName", "Bundle")
        except Exception:
            pass

        # Total bundle price (discounted if available)
        total_price = bundle_info.get("TotalDiscountedCost") or bundle_info.get("TotalBaseCost") or {}
        bundle_price = list(total_price.values())[0] if total_price else 0

        skins = []
        for item in items:
            skin_id = item.get("Item", {}).get("ItemID")
            price = item.get("BasePrice", 0)
            try:
                skin_url = f"https://valorant-api.com/v1/weapons/skinlevels/{skin_id}"
                res = requests.get(skin_url)
                skin_data = res.json().get("data", {})
                skins.append({
                    "name": skin_data.get("displayName", "Unknown"),
                    "icon": skin_data.get("displayIcon"),
                    "price": price
                })
            except Exception:
                continue

        parsed.append({
            "name": bundle_name,
            "skins": skins,
            "bundle_price": bundle_price,
            "remaining": b["remaining"]
        })

    return parsed


# ---------------------- Helpers ----------------------
def format_time(seconds):
    """Convert seconds → HH:MM:SS"""
    hours = math.floor(seconds / 3600)
    minutes = math.floor((seconds % 3600) / 60)
    sec = seconds % 60
    return f"{hours:02}:{minutes:02}:{sec:02}"

def make_wallet_bar(wallet_data):
    # Extract balances
    vp = wallet_data.get("Balances", {}).get("85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741", 0)   # Valorant Points UUID
    rp = wallet_data.get("Balances", {}).get("e59aa87c-4cbf-517a-5983-6e81511be9b7", 0)   # Radianite Points UUID

    return ft.Container(
        bgcolor="#0f1923",  # Dark navy/grey background
        padding=15,
        border_radius=15,
        margin=ft.margin.only(bottom=20),
        content=ft.Row(
            [
                ft.Text(
                    "Your Wallet",
                    size=22,
                    weight="bold",
                    color="#f1f5f9",
                ),
                ft.Container(expand=True),

                # VP balance
                ft.Row(
                    [
                        ft.Image(
                            src="https://justvalorant.github.io/RP-to-VP-Calculator/vp.png", 
                            width=24,
                            height=24,
                            border_radius=15
                        ),
                        ft.Text(
                            f"{vp:,}",
                            size=18,
                            weight="bold",
                            color="#fbbf24",  # gold for VP
                        )
                    ],
                    spacing=8,
                ),

                ft.Container(width=10),  # spacing

                # RP balance
                ft.Row(
                    [
                        ft.Image(
                            src="https://justvalorant.github.io/RP-to-VP-Calculator/rp.png", 
                            width=24,
                            height=24,
                            border_radius=15
                            
                        ),
                        ft.Text(
                            f"{rp:,}",
                            size=18,
                            weight="bold",
                            color="#38bdf8",  # cyan for RP
                        )
                    ],
                    spacing=8,
                ),
            ],
            alignment="spaceBetween",
        ),
    )

def make_store_section(title, skins, remaining, extra_text=None):
    # Store background: dark grey, Valorant red accents
    return ft.Container(
        bgcolor="#0f1923",  # Dark navy/grey background
        padding=20,
        border_radius=15,
        content=ft.Column(
            [
                # Header row
                ft.Row(
                    [
                        ft.Text(
                            title,
                            size=24,
                            weight="bold",
                            color="#ff4655",  # Valorant red
                        ),
                        ft.Container(expand=True),
                        ft.Text(
                            format_time(remaining),
                            size=16,
                            color="#ffffff",
                        ),
                    ],
                    alignment="spaceBetween",
                ),

                # Skins grid
                ft.Row(
                    [
                        ft.Container(
                            bgcolor="#1f2a36",  # Slightly lighter dark
                            border_radius=10,
                            padding=10,
                            width=200,
                            content=ft.Column(
                                [
                                    ft.Image(skin["icon"], height=120, fit=ft.ImageFit.CONTAIN),
                                    ft.Text(
                                        skin["name"],
                                        size=16,
                                        color="#ffffff",
                                        weight="bold",
                                        text_align="center",
                                    ),
                                    ft.Text(
                                        f"{skin['price']:,} VP",
                                        size=14,
                                        color="#ffd700",  # Gold for VP
                                        text_align="center",
                                    ),
                                ],
                                horizontal_alignment="center",
                                spacing=5,
                            ),
                        )
                        for skin in skins if skin["icon"] # remove non icon elements
                    ],
                    wrap=True,
                    spacing=15,
                ),

                # Extra info (bundle price, etc.)
                ft.Text(
                    extra_text or "",
                    size=18,
                    weight="bold",
                    color="#50fa7b",  # Neon green (Valorant "discount" vibe)
                ),
            ],
            spacing=15,
        ),
    )



# ---------------------- Main App ----------------------
def main(page: ft.Page):
    page.title = "ValStore"
    page.scroll = "auto"

    # ---- Fetch wallet data (replace with your API call) ----
    wallet_data = {
        "Balances": {
            "85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741": 2306,  # VP
            "e59aa87c-4cbf-517a-5983-6e81511be9b7": 150,   # RP
        }
    }

    page.add(make_wallet_bar(wallet_data))

    try:
        access_token, entitlements_token, puuid, region = getTokens()
        store_json = getStore(access_token, entitlements_token, puuid, region)

        daily_skins, daily_remaining = parseDaily(store_json)
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

    except Exception as e:
        page.add(ft.Text(f"❌ Error: {e}", color="red", size=20))
        return

    # Daily offers
    page.add(
        make_store_section("Daily Store", daily_skins, daily_remaining)
    )

ft.app(main, assets_dir="assets")