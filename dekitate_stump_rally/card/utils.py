import requests

def get_minecraft_data(mcid):
    """MCIDからUUIDと正しい綴りの名前を取得する"""
    url = f"https://api.mojang.com/users/profiles/minecraft/{mcid}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('id'), data.get('name') # uuid(ハイフンなし), 正しい名前
    except Exception as e:
        print(f"Mojang API Error: {e}")
    return None, None