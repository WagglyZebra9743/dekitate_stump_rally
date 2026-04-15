from django.utils import timezone
import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Stamp(models.Model):
    # ワールドの選択肢を定義
    WORLD_CHOICES = [
        ('world', 'オーバーワールド'),
        ('world_nether', 'ネザー'),
        ('world_the_end', 'ジ・エンド'),
    ]

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        verbose_name='作成者'
    )

    name = models.CharField('スタンプ名称', max_length=100)
    description = models.TextField('説明文', blank=True)
    
    # 選択肢形式のフィールド
    world = models.CharField('ワールド', max_length=20, choices=WORLD_CHOICES, default='world')
    
    # 座標（マイクラの座標は整数が扱いやすいので IntegerField を採用）
    x = models.IntegerField('X座標')
    y = models.IntegerField('Y座標')
    z = models.IntegerField('Z座標')

    # 許容半径
    radius = models.IntegerField('半径', default=10, validators=[MinValueValidator(1), MaxValueValidator(100)])

    # 隠しスタンプかどうか
    is_hidden = models.BooleanField('隠しスタンプ', default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Player(models.Model):
    # MinecraftのUUID（ダッシュなしの32文字で保存されることが多い）
    uuid = models.CharField('Minecraft UUID', max_length=36, unique=True)
    # 表示用のMCID（最後にスタンプを押した時の名前を保存しておく）
    last_known_name = models.CharField('最新のMCID', max_length=50)
    points = models.IntegerField('所持ポイント', default=0)
    
    # Discord連携用：allauthのCustomUserと紐付け
    # Discordログインしていないプレイヤーもいるため null=True にする
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='player_profiles'
    )

    is_enable = models.BooleanField('有効',default=True)

    def __str__(self):
        return f"{self.last_known_name} ({self.points} pt)"


class StampLog(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    stamp = models.ForeignKey(Stamp, on_delete=models.CASCADE)
    
    first_pressed_at = models.DateTimeField('初回取得日時', auto_now_add=True)
    last_pressed_at = models.DateTimeField('最終取得日時', auto_now=True)

    class Meta:
        # 1人のプレイヤーは、同じスタンプに対して1つの履歴しか持たない
        unique_together = ('player', 'stamp')

    def __str__(self):
        # mcid ではなく、last_known_name（最新のMCID）を表示するように変更
        return f"{self.player.last_known_name} -> {self.stamp.name}"