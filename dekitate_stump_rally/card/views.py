# card/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Stamp
from .forms import StampForm
import requests
import math
import time
from django.utils import timezone
from .models import Stamp, Player, StampLog, SystemSetting
from django.contrib import messages
from .utils import get_minecraft_data
from all_log.register import register_info_log,register_create_log,register_error_log,register_warn_log

def index(request):
    if request.method == 'POST':
        #入力したmcidを保存
        mcid = request.POST.get('mcid')
        
        #mcid未入力の時
        if not mcid:
            messages.error(request, "MCIDを入力してください。")
            register_error_log('スタンプ',"処理中止:mcid未入力","","スタンプ,stamp,システム,system,エラー,error,キャンセル,中止,cancel,nothing")
            return redirect('index')
        
        #キャッシュにmcidを保存
        request.session['saved_mcid'] = mcid

        setting = SystemSetting.objects.first()
        now = timezone.now() # 現在時刻を取得

        if setting:
            # 開始時間が設定されていて、まだ開始前の場合
            if setting.event_start_at and now < setting.event_start_at:
                messages.error(request, "イベントはまだ開始していません！")
                register_error_log('スタンプ',"イベント未開始",mcid,"スタンプ,stamp,システム,system,エラー,error,キャンセル,中止,cancel,unstarted")
                return redirect('index')
            
            # 終了時間が設定されていて、すでに終わっている場合
            if setting.event_end_at and now > setting.event_end_at:
                messages.error(request, "イベントは終了しました。ご参加ありがとうございました！")
                register_error_log('スタンプ',"イベント終了済み",mcid,"スタンプ,stamp,システム,system,エラー,error,キャンセル,中止,cancel,ended")
                return redirect('index')
        
        #MojangAPIからmcidとuuidを取得する
        uuid_str, correct_name = get_minecraft_data(mcid)
        if not uuid_str:
            messages.error(request, f"Minecraftアカウント '{mcid}' が見つかりません。")
            register_error_log('スタンプ',"処理中止:mcid未発見",mcid,f"スタンプ,stamp,システム,system,エラー,error,キャンセル,中止,cancel,not_found,{mcid}")
            return redirect('index')
        

        #データを確認
        player_check = Player.objects.filter(uuid=uuid_str).first()
        if player_check and not player_check.is_enable:
            messages.error(request, "mcidに関する問題が発生しました。運営に問い合わせてください。")
            register_warn_log('スタンプ',"処理中止:unavailable mcid",correct_name,f"スランプ,stamp,システム,system,警告,warn,キャンセル,中止,cancel,利用停止,ban,{correct_name},{uuid_str}")
            return redirect('index')

        #Dynmapから座標を取得
        current_timestamp = int(time.time() * 1000)
        DYNMAP_URL = f"http://maps.dekitateserver.com/survival/up/world/world/{current_timestamp}"
        try:
            response = requests.get(DYNMAP_URL, timeout=5)
            data = response.json()
        except:
            messages.error(request, "マップサーバーと通信できませんでした。")
            register_error_log('スタンプ',"システムエラー:マップ通信失敗",correct_name,f"スタンプ,stamp,システム,system,エラー,error,server,地図,マップ,map,通信,キャンセル,中止,cancel,{correct_name},{uuid_str}")
            return redirect('index')

        # サーバー上にプレイヤーがいるか探す
        player_data = None
        for p in data.get('players', []):
            if p['name'].lower() == correct_name.lower():
                player_data = p
                break

        if not player_data:
            messages.error(request, f" {correct_name} の座標取得に失敗しました.サバイバルにログインしているかを確認してください")
            register_error_log('スタンプ',"処理中止:プレイヤー座標取得失敗",correct_name,f"スタンプ,stamp,システム,system,エラー,error,キャンセル,中止,cancel,地図,マップ,map,not_found,{correct_name},{uuid_str}")
            return redirect('index')

        # 座標と【現在いるワールド】を取得する
        px, py, pz = player_data['x'], player_data['y'], player_data['z']
        p_world = player_data.get('world') # 'world' や 'world_the_end' などが入る

        # 近くのスタンプを探す
        hit_stamp = None
        stamps_with_distance = []
        for stamp in Stamp.objects.all():
            # ★ ここが重要！プレイヤーの現在ワールドと、スタンプの設置ワールドが同じかチェック
            if stamp.world == p_world:
                # ワールドが同じ場合のみ、距離を計算する
                distance = math.sqrt((px - stamp.x)**2 + (py - stamp.y)**2 + (pz - stamp.z)**2)
                stamps_with_distance.append((distance, stamp))
                if distance <= stamp.radius:
                    hit_stamp = stamp
                    break # 発見したらループを抜ける

        if not hit_stamp:
            # スタンプ範囲外だった場合、近い順に並び替えて上位3件を取得
            stamps_with_distance.sort(key=lambda x: x[0])
            nearby_data = []
            for dist, s in stamps_with_distance[:3]:
                nearby_data.append({
                    'name': s.name,
                    'desc': s.description,
                    'world': s.get_world_display(),
                    'coords': f"{s.x}, {s.y}, {s.z}",
                    'is_hidden': s.is_hidden,
                    'distance': round(dist, 1) # 距離を小数点第1位まで
                })
            # セッションに一時保存してリダイレクト
            request.session['nearby_stamps'] = nearby_data
            messages.warning(request, "スタンプの範囲内にいません！座標やワールドを確認してください。")
            register_info_log('スタンプ',f"処理終了:スタンプ範囲外{p_world}({px},{py},{pz}),以下の場所を提案{nearby_data}",correct_name,f"スタンプ,stamp,システム,system,終了,end,範囲外,out_of_area,not_found,{correct_name},{uuid_str}")
            return redirect('index')

        # 4. データ保存・ポイント計算
        player, created = Player.objects.get_or_create(
            uuid=uuid_str,
            defaults={'last_known_name': correct_name}
        )
        if created:
            register_create_log('プレイヤー',f"新規プレイヤー:{correct_name}を登録,{p_world}({px},{py},{pz})",correct_name,f"スタンプ,stamp,システム,system,登録,create,プレイヤー,player,{correct_name},{uuid_str}")
        # 名前が変わっていたら更新する
        if player.last_known_name != correct_name:
            register_info_log('プレイヤー',f"mcid更新{player.last_known_name}->{correct_name}",correct_name,f"スタンプ,stamp,システム,system,更新,update,プレイヤー,player,{correct_name},{uuid_str}")
            player.last_known_name = correct_name
            player.save()
        
        if request.user.is_authenticated and player.user is None:
            register_info_log('プレイヤー',f"discord:{request.user} = mcid:{correct_name}",correct_name,f"スタンプ,stamp,システム,system,更新,update,プレイヤー,player,{correct_name},{uuid_str},{request.user}")
            player.user = request.user
            player.save()

        log, log_created = StampLog.objects.get_or_create(player=player, stamp=hit_stamp)
        today = timezone.localtime().date()
        
        if log_created:
            # 初回ゲット
            points_to_add = 500 if hit_stamp.is_hidden else 100
            msg = f"🎉 {'隠し' if hit_stamp.is_hidden else ''}スタンプ『{hit_stamp.name}』を初ゲット！ {points_to_add}pt獲得！"
            register_info_log('スタンプ',f"初回獲得{hit_stamp.name} by {correct_name}({points_to_add})",correct_name,f"スタンプ,stamp,システム,system,{hit_stamp.name},{correct_name},{uuid_str}")
        else:
            # 2回目以降（今日すでに押しているかチェック）
            if timezone.localtime(log.last_pressed_at).date() < today:
                points_to_add = 10
                msg = f"📅 今日の『{hit_stamp.name}』スタンプ！ {points_to_add}pt獲得！"
                register_info_log('スタンプ',f"デイリー獲得{hit_stamp.name} by {correct_name}({points_to_add})",correct_name,f"スタンプ,stamp,システム,system,{hit_stamp.name},{correct_name},{uuid_str}")
                log.save() # 更新
            else:
                messages.info(request, f"『{hit_stamp.name}』は今日すでに押しています。日付が変わるまで待ちましょう")
                register_error_log('スタンプ',f"デイリーCT{hit_stamp.name} by {correct_name}",correct_name,f"処理中止,cancel,スタンプ,stamp,システム,system,{hit_stamp.name},{correct_name},{uuid_str}")
                return redirect('index')

        # ポイント加算
        player.points += points_to_add
        player.save()
        messages.success(request, msg)
        register_info_log('スタンプ',f"処理終了:「{msg}」",correct_name,f"スタンプ,stamp,システム,system,終了,end,{correct_name},{uuid_str}")
        return redirect('index')
    
    saved_mcid = request.session.get('saved_mcid', '')
    nearby_stamps = request.session.pop('nearby_stamps', None)

    return render(request, "card/index.html", {
        'saved_mcid': saved_mcid,
        'nearby_stamps': nearby_stamps
    })

def rules(request):
    return render(request, "card/rules.html")

def play(request):
    return render(request, "card/play.html")

# --- 登録処理のビュー ---
def stamp_add_view(request):
    # スタンプ管理者グループに入っているかチェック
    is_manager = request.user.is_authenticated and request.user.groups.filter(name='スタンプ管理者').exists()
    
    # 管理者じゃなかったらエラーページを表示
    if not is_manager:
        cached_mcid = request.session.get('saved_mcid', '')
        user_info = f"({request.user})" if request.user.is_authenticated else ""
        register_warn_log('権限不足', f"追加ページへのアクセスに失敗{user_info}",cached_mcid, "スタンプ追加,stamp,失敗,fail,中止,cancel")
        return render(request, 'card/permission_denied.html')
    
    setting = SystemSetting.objects.first()
    now = timezone.now()
    if setting:

        if setting.stamp_add_start_at and now < setting.stamp_add_start_at:
            messages.error(request, "現在はスタンプの追加ができません")
            register_error_log('時間外', f"追加ページへ{user_info}が速くアクセスしようとした",cached_mcid, "スタンプ追加,stamp,失敗,fail,中止,cancel")
            return redirect('index')

        if setting.stamp_add_end_at and now > setting.stamp_add_end_at:
            register_error_log('時間外', f"追加ページへ{user_info}が遅くアクセスしようとした",cached_mcid, "スタンプ追加,stamp,失敗,fail,中止,cancel")
            return redirect('index')

    if request.method == 'POST':
        form = StampForm(request.POST)
        if form.is_valid():
            # 確認画面で「登録する」ボタンが押された場合
            if 'confirm' in request.POST:
                stamp = form.save(commit=False)
                stamp.author = request.user
                stamp.save() 
                register_create_log('スタンプ追加',f"以下のスタンプが{request.user}によって追加されました{stamp}","",f"スタンプ追加,stamp,成功,success,処理終了,end,{request.user}")
                return redirect('stamp_success', pk=stamp.pk) # 成功ページへ！
            
            # 入力画面で「確認する」ボタンが押された場合
            else:
                w = form.cleaned_data['world']
                x = form.cleaned_data['x']
                y = form.cleaned_data['y']
                z = form.cleaned_data['z']
                dynmap_url = f"https://maps.dekitateserver.com/survival/?worldname={w}&mapname=flat&zoom=6&x={x}&y={y}&z={z}"
                
                return render(request, 'card/stamp_confirm.html', {
                    'form': form,
                    'dynmap_url': dynmap_url,
                })
    else:
        form = StampForm()


    return render(request, 'card/stamp_add.html', {'form': form})


def stamp_success_view(request, pk):
    # IDを元に、データベースからたった今登録したスタンプの情報を取ってくる
    stamp = get_object_or_404(Stamp, pk=pk)
    
    return render(request, 'card/stamp_success.html', {'stamp': stamp})

def stamp_list(request):
    # 1. 全スタンプ取得（隠しも含む）
    stamps = Stamp.objects.all().order_by('created_at')
    # 2. 全プレイヤー数
    total_players_count = Player.objects.count()
    
    saved_mcid = request.session.get('saved_mcid')
    player = Player.objects.filter(last_known_name=saved_mcid).first() if saved_mcid else None

    for stamp in stamps:
        # このスタンプを押した人数
        pressed_count = StampLog.objects.filter(stamp=stamp).count()
        stamp.pressed_count = pressed_count
        
        # 達成率(%)の計算
        if total_players_count > 0:
            stamp.ratio = round((pressed_count / total_players_count) * 100, 1)
        else:
            stamp.ratio = 0
            
        # 自分が押したかどうか
        stamp.is_pressed = StampLog.objects.filter(player=player, stamp=stamp).exists() if player else False

    return render(request, 'card/stamp_list.html', {'stamps': stamps})

def player_info(request):
    saved_mcid = request.session.get('saved_mcid')
    if not saved_mcid:
        messages.warning(request, "まずはトップページでMCIDを入力してください。")
        return redirect('index')
    
    player = get_object_or_404(Player, last_known_name=saved_mcid)
    
    # ポイントランキングの順位を計算（自分よりポイントが多い人数 + 1）
    rank = Player.objects.filter(points__gt=player.points).count() + 1
    
    # 一つ上の順位のポイント（自分より高いポイントの中で一番小さい値）
    upper = Player.objects.filter(points__gt=player.points).order_by('points').first()
    
    # 一つ下の順位のポイント（自分より低いポイントの中で一番大きい値）
    lower = Player.objects.filter(points__lt=player.points).order_by('-points').first()
    
    # 押したスタンプの一覧を取得
    stamp_logs = StampLog.objects.filter(player=player).order_by('-last_pressed_at')
    
    today = timezone.localtime().date()
    for log in stamp_logs:
        # 最後に押した日が今日より前なら True
        log.can_press_today = timezone.localtime(log.last_pressed_at).date() < today

    context = {
        'player': player,
        'rank': rank,
        'upper_points': upper.points if upper else "-",
        'lower_points': lower.points if lower else "-",
        'stamp_logs': stamp_logs,
    }
    return render(request, 'card/player_info.html', context)