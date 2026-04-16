
from django.db import models
from django.contrib.auth.models import AbstractUser

# Django標準のユーザー機能を拡張（AbstractUserを継承）します
class CustomUser(AbstractUser):
    # MinecraftのID（必須ではない・重複なし）
    mcid = models.CharField('Minecraft ID', max_length=50, blank=True, null=True, unique=True)
    
    # DiscordのID（Discord連携時に自動で入る想定）
    discord_id = models.CharField('Discord ID', max_length=100, blank=True, null=True, unique=True)

    note = models.TextField("メモ",blank=True,null=True)

    def __str__(self):
        return self.username