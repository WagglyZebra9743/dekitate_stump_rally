from .models import Player

def player_info(request):
    # セッションに保存されたMCIDからプレイヤーを取得
    saved_mcid = request.session.get('saved_mcid')
    player = None
    if saved_mcid:
        player = Player.objects.filter(last_known_name=saved_mcid).first()
    
    # テンプレート内で 'current_player' という名前で使えるようにする
    return {'current_player': player}