import unicodedata
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter
from django.contrib import admin
from .models import AllLog

@admin.register(AllLog)
class AllLogAdmin(admin.ModelAdmin):
    list_display = ('name','type','short_message','player','logtime')
    @admin.display(description='メッセージ')
    def short_message(self, obj):
        if not obj.message:
            return ""
            
        MAX_WIDTH = 50 
        current_width = 0
        result = ""
        for char in obj.message:
            # east_asian_width で文字の種類を判定
            # 'F'(Fullwidth), 'W'(Wide), 'A'(Ambiguous) は全角扱い
            char_width = 2 if unicodedata.east_asian_width(char) in 'FWA' else 1
            
            if current_width + char_width > MAX_WIDTH:
                return result + "..."
            
            result += char
            current_width += char_width

        # 制限幅に収まっていればそのまま返す
        return result
    list_filter=[
        'type',
        ('logtime', DateTimeRangeFilter),
        ]
    search_fields = ('name', 'message','player','search_assist')