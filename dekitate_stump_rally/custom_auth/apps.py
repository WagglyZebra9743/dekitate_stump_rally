from django.apps import AppConfig


class CustomAuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'custom_auth'

    def ready(self):
        from django.contrib import admin
        from allauth.account.models import EmailAddress
        from allauth.socialaccount.models import SocialToken, SocialAccount
        from allauth.socialaccount.admin import SocialAccountAdmin

        # 1. 完全に使わない機能を消す
        try:
            admin.site.unregister(EmailAddress)
            admin.site.unregister(SocialToken)
        except admin.sites.NotRegistered:
            pass

        # 2. ソーシャルアカウント画面をカスタマイズする
        try:
            # 一旦、標準のソーシャルアカウント管理画面を解除する
            admin.site.unregister(SocialAccount)
        except admin.sites.NotRegistered:
            pass

        # 標準の画面(SocialAccountAdmin)を引き継ぎつつ、一部だけ変更するクラスを作る
        class CustomSocialAccountAdmin(SocialAccountAdmin):
            exclude = ('extra_data',) # 「エクストラデータ」を入力フォームから除外！

        # カスタマイズした画面を登録し直す
        admin.site.register(SocialAccount, CustomSocialAccountAdmin)