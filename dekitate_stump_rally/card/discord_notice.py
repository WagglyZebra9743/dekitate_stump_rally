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
    
    # ユーザーに紐づくプロフィールを取得（なければ自動作成する）
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
            'invitable':False,
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
                register_error_log('送信エラー', f"Discordエラー: {res.text}", "", "debag,error,discord")

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
            "thumbnail": {
                "url": f"https://mc-heads.net/avatar/{player.uuid}"
            },
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
        register_error_log('送信エラー', f"Discordエラー: {res.text}", "", "debag,error,discord")


def staff_call(user, player, discord_user_id):
    BOT_TOKEN = settings.DISCORD_BOT_TOKEN
    CHANNEL_ID = '1494160947168804934' 
    
    headers = {
        'Authorization': f'Bot {BOT_TOKEN}',
        'Content-Type': 'application/json',
    }
    
    # ユーザーに紐づくプロフィールを取得（なければ自動作成する）
    profile, created = UserProfile.objects.get_or_create(user=user)
    thread_id = profile.discord_thread_id
    
    #スレッドがない場合は新規作成
    if not thread_id:
        url_create_thread = f'https://discord.com/api/v10/channels/{CHANNEL_ID}/threads'
        data_thread = {
            # Discordのアカウント名（ユーザー名）をスレッド名にする
            'name': f'📜 {user.username} へのスタンプ通知',
            'invitable':False,
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
                register_error_log('送信エラー', f"Discordエラー: {res.text}", "", "debag,error,discord")

        else:
            register_error_log('スレッド作成エラー',f"スレッドの作成に失敗しました{res.text}","","失敗,エラー,fail,error,server,discord")
            return 'スレッド作成時にエラーが発生しました.<a href="https://discord.com/channels/1494160585129070692/1498565247458345011" target="_blank">#お問い合わせ総合</a>で連絡をしてください'
            
    url_add_member = f'https://discord.com/api/v10/channels/{thread_id}/thread-members/{discord_user_id}'
    requests.put(url_add_member, headers=headers)
    # --------------------------------------------------------
    # ② メッセージの送信
    # --------------------------------------------------------
    url_send_msg = f'https://discord.com/api/v10/channels/{thread_id}/messages'
    
    
    embed_data = {
        "content": "<@&1498576707173482546>",
        "tts": False,
        "embeds": [
            {
            "id": 52580940,
            "description": "お問い合わせをしたい内容を入力してお待ちください",
            "fields": [
                {
                    "id": 875959258,
                    "name": "24時間以内に反応がない場合",
                    "value": "[こちら](https://www.dekitateserver.com/)から再度呼び出してください"
                }
            ],
            "title": "運営を呼びました",
            "color": 16711680
            }
        ],
        "components": [],
        "actions": {},
        "flags": 0
    }

    data_msg = {
        'content': "",
        "embeds":[embed_data]
    }
    
    res = requests.post(url_send_msg, headers=headers, json=data_msg)
    if res.status_code not in [200, 201]:
        register_error_log('送信エラー', f"Discordエラー: {res.text}", "", "debag,error,discord")