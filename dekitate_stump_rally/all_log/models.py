from django.db import models

# Create your models here.
class AllLog(models.Model):
    name = models.CharField('タイトル', max_length=20)
    LOG_TYPES = [
        ('info','情報'),
        ('create','データ追加'),
        ('error','エラー'),
        ('warn','警告'),
    ]
    player = models.CharField('プレイヤー',max_length=20,blank=True)
    type = models.CharField('タイプ',max_length=20,choices=LOG_TYPES,default='info')
    message = models.TextField('メッセージ')
    logtime = models.DateTimeField(auto_now_add=True)
    search_assist = models.TextField('検索補助',max_length=300,blank=True)
    def __str__(self):
        return self.name