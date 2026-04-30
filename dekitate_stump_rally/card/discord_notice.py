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


def discord_staff_call(user,player,discord_user_id):
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
            return 1
            
    url_add_member = f'https://discord.com/api/v10/channels/{thread_id}/thread-members/{discord_user_id}'
    requests.put(url_add_member, headers=headers)
    # --------------------------------------------------------
    # ② メッセージの送信
    # --------------------------------------------------------
    url_send_msg = f'https://discord.com/api/v10/channels/{thread_id}/messages'
    
    
    # ★ 純粋な「Embed（埋め込み）の中身」だけを定義する
    embed_content = {
        "title": "🆘 運営を呼びました",
        "description": "お問い合わせをしたい内容を入力してお待ちください",
        "color": 16711680, # 赤色
        "fields": [
            {
                "name": "24時間経っても反応がない場合",
                "value": "[こちら](https://www.dekitateserver.com/)から再度呼び出してください",
                "inline": False
            },
            {
                "name": "複数回呼んでも反応がない場合",
                "value": "<#1498565247458345011>で連絡をしてください",
                "inline": False
            }
        ]
    }

    # ★ ここで「メンション（content）」と「埋め込み（embeds）」を合体させる
    data_msg = {
        # メンションは content に入れる（roleメンションもこれで機能します）
        'content': f"{player.last_known_name} が <@&1498576707173482546> を呼びました",
        # embeds は「リスト」形式で渡す
        'embeds': [embed_content]
    }
    
    res = requests.post(url_send_msg, headers=headers, json=data_msg)
    if res.status_code not in [200, 201]:
        register_error_log('送信エラー', f"Discordエラー: {res.text}", "", "debag,error,discord")
        return 1
    CHANNEL_ID = "1499218681039814799"
    url_staff_call = f'https://discord.com/api/v10/channels/{CHANNEL_ID}/messages'

    notify_data = {
        # ここでロールをメンションし、作成したスレッドのリンクを貼る
        'content': f"<@&1498576707173482546> {player.last_known_name} が運営を呼びました\n スレッド <#{thread_id}>を確認してください"
    }
    # 親チャンネルに送信（これでスタッフの通知が鳴る！）
    res = requests.post(url_staff_call, headers=headers, json=notify_data)
    if res.status_code not in [200, 201]:
        register_error_log('送信エラー', f"Discordエラー: {res.text}", "", "debag,error,discord")
        return 1