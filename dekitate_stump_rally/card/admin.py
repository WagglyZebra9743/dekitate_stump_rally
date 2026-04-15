from django.contrib import admin
from django.contrib.admin import RelatedOnlyFieldListFilter
from .models import Stamp,Player, StampLog

@admin.register(Stamp)
class StampAdmin(admin.ModelAdmin):
    # 一覧画面に表示する項目
    list_display = ('name', 'world', 'author', 'created_at','id')
    
    # フィルター機能（ワールド別、作成者別で絞り込めるようにする）
    list_filter = (
        'world', 
        ('author', RelatedOnlyFieldListFilter),
        'is_hidden'
    )
    
    # 検索機能（スタンプ名で検索可能にする）
    search_fields = ('name', 'description')

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    # 一覧画面で見たい項目
    list_display = ('last_known_name', 'uuid', 'points', 'user','is_enable')
    list_editable = ('is_enable',)
    # MCIDやUUIDで検索できるようにする
    search_fields = ('last_known_name', 'uuid')
    # 紐づいているDiscordユーザーの有無などで絞り込み
    list_filter = ('user',)

# ==========================================
# スタンプ取得履歴の管理
# ==========================================
@admin.register(StampLog)
class StampLogAdmin(admin.ModelAdmin):
    list_display = ('stamp','get_player_name', 'first_pressed_at', 'last_pressed_at')
    list_filter = ('stamp',)
    search_fields = ('player__last_known_name', 'stamp__name')

    # 👇 新しく「名前だけを取り出す専用の表示ルール」を作ります
    @admin.display(description='プレイヤー')
    def get_player_name(self, obj):
        return obj.player.last_known_name