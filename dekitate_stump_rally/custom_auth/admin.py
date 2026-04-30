# custom_auth/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser

# ユーザー管理画面の見た目をカスタマイズするクラス
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'is_staff', 'is_superuser', 'is_active','can_call_staff')
    list_editable = ('can_call_staff',)
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name")}), 
        (_("Permissions"), {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            ),
        }),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

# カスタマイズしたクラスを適用して登録する
admin.site.register(CustomUser, CustomUserAdmin)