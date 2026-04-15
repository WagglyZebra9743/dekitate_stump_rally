import requests
from all_log.register import register_error_log

def get_minecraft_data(mcid):
    """MCIDからUUIDと正しい綴りの名前を取得する"""
    url = f"https://api.mojang.com/users/profiles/minecraft/{mcid}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('id'), data.get('name') # uuid(ハイフンなし), 正しい名前
    except Exception as e:
        register_error_log('APIエラー',f"Mojang API Error: {e}","","エラー,error,API")
    return None, None