from django.db import models

# Create your models here.
class AllLog(models.Model):
    name = models.CharField('タイトル', max_length=20)
    LOG_TYPES = [
        ('info','情報'),
        ('dataadd','データ追加'),
        ('error','エラー'),
        ('warn','警告'),
    ]
    type = models.CharField('タイプ',max_length=20,choices=LOG_TYPES,default='info')
    message = models.TextField('メッセージ', max_length=300)
    logtime = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name