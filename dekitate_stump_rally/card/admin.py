from django.contrib import admin
from django.contrib.admin import RelatedOnlyFieldListFilter
from .models import Stamp,Player,StampLog,UserProfile,SystemSetting
from rangefilter.filters import DateTimeRangeFilter

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
    def get_actions(self, request):
        # まず元々のアクションのリストを取得する
        actions = super().get_actions(request)
        
        # もし「delete_selected」というアクションが含まれていたら、それを削除する
        if 'delete_selected' in actions:
            del actions['delete_selected']
            
        return actions

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    # 一覧画面で見たい項目
    list_display = ('last_known_name', 'uuid', 'points', 'user','is_enable')
    list_editable = ('is_enable',)
    # MCIDやUUIDで検索できるようにする
    search_fields = ('last_known_name', 'uuid')
    # 紐づいているDiscordユーザーの有無などで絞り込み
    list_filter = ('user',)
    def get_actions(self, request):
        # まず元々のアクションのリストを取得する
        actions = super().get_actions(request)
        
        # もし「delete_selected」というアクションが含まれていたら、それを削除する
        if 'delete_selected' in actions:
            del actions['delete_selected']
            
        return actions

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user','discord_thread_id')
    search_fields = ('user','discord_thread_id')
    def get_actions(self, request):
        # まず元々のアクションのリストを取得する
        actions = super().get_actions(request)
        
        # もし「delete_selected」というアクションが含まれていたら、それを削除する
        if 'delete_selected' in actions:
            del actions['delete_selected']
            
        return actions

# ==========================================
# スタンプ取得履歴の管理
# ==========================================
@admin.register(StampLog)
class StampLogAdmin(admin.ModelAdmin):
    list_display = ('stamp','get_player_name', 'first_pressed_at', 'last_pressed_at')
    search_fields = ('player__last_known_name', 'stamp__name', 'first_pressed_at', 'last_pressed_at')

    list_filter = (
        'stamp',
        'player__last_known_name',
        ('last_pressed_at', DateTimeRangeFilter),
        ('first_pressed_at', DateTimeRangeFilter),
    )

    # 名前だけを取り出す専用の表示ルール
    @admin.display(description='プレイヤー')
    def get_player_name(self, obj):
        return obj.player.last_known_name

@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display=('__str__','event_start_at','event_end_at','stamp_add_start_at','stamp_add_end_at')
    # すでに設定データが存在する場合は、新しいデータを追加させない
    def has_add_permission(self, request):
        if SystemSetting.objects.exists():
            return False
        return True
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context.update({
            'show_save_and_add_another': False, # 「続けて追加する」を非表示にする！
        })
        return super().render_change_form(request, context, add, change, form_url, obj)