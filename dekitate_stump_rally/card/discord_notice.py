import requests
from .models import UserProfile # 作成したモデルをインポート
from django.conf import settings
from all_log.register import register_info_log,register_error_log

def send_stamp_notification(user, player, stamp,points_to_add, discord_user_id):
    BOT_TOKEN = settings.DISCORD_BOT_TOKEN
    CHANNEL_ID = '1494160947168804934' 
    
    headers = {
        'Authorization': f'Bot {BOT_TOKEN}',
        'Content-Type': 'application/json',
    }
    
    # ★ ユーザーに紐づくプロフィールを取得（なければ自動作成する安全な書き方）
    profile, created = UserProfile.objects.get_or_create(user=user)
    thread_id = profile.discord_thread_id
    
    # --------------------------------------------------------
    # ① スレッドがない場合は新規作成
    # --------------------------------------------------------
    if not thread_id:
        url_create_thread = f'https://discord.com/api/v10/channels/{CHANNEL_ID}/threads'
        data_thread = {
            # Discordのアカウント名（ユーザー名）をスレッド名にする
            'name': f'📜 {user.username} へのスタンプ通知',
            'type': 12, # プライベートスレッド
        }
        
        res = requests.post(url_create_thread, headers=headers, json=data_thread)
        if res.status_code in [200, 201]:
            thread_id = res.json()['id']
            # プロフィールに保存
            profile.discord_thread_id = thread_id
            profile.save()
            message_content = f"<@{discord_user_id}> 通知用スレッドを作成しました"
            data_msg = {
                'content': message_content
                }
            url_send_msg = f'https://discord.com/api/v10/channels/{thread_id}/messages'
            res = requests.post(url_send_msg, headers=headers, json=data_msg)
            if res.status_code not in [200, 201]:
                register_error_log('Embed送信エラー', f"Discordエラー: {res.text}", "", "debag,error")

        else:
            register_error_log('スレッド作成エラー',f"スレッドの作成に失敗しました{res.text}","","失敗,エラー,fail,error,server,discord")
            return
            
    url_add_member = f'https://discord.com/api/v10/channels/{thread_id}/thread-members/{discord_user_id}'
    requests.put(url_add_member, headers=headers)
    # --------------------------------------------------------
    # ② メッセージの送信
    # --------------------------------------------------------
    url_send_msg = f'https://discord.com/api/v10/channels/{thread_id}/messages'
    
    
    embed_data = {
            "title": "スタンプを取得しました",
            "description": f"{stamp.name}を押したことで{points_to_add}ポイント獲得",
            "color": 11403008,
            "fields": [
                {
                    "name": "スタンプ情報",
                    "value": f"{stamp.get_world_display()}\n:round_pushpin: ({stamp.x},{stamp.y},{stamp.z})",
                    "inline": True
                },
                {
                    "name": "獲得者",
                    "value": f"{player.last_known_name}",
                    "inline": True
                },
                {
                    "name": "所持ポイント",
                    "value": f"{player.points}",
                    "inline": True
                }
            ]
        }

    data_msg = {
        'content': "",
        "embeds":[embed_data]
    }
    
    res = requests.post(url_send_msg, headers=headers, json=data_msg)
    if res.status_code not in [200, 201]:
        register_error_log('Embed送信エラー', f"Discordエラー: {res.text}", "", "debag,error")