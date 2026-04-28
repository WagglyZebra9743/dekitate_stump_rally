import traceback
from .register import register_error_log

class ErrorLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 通常のアクセス時はそのまま通す
        return self.get_response(request)

    def process_exception(self, request, exception):
        # ★ プログラムがクラッシュ（黄色い画面）した瞬間に自動でここが実行される！
        
        # 1. どこのページでエラーが起きたか
        url = request.path
        
        # 2. 誰がエラーを出したか（ログインしていれば名前、していなければ空欄）
        player_name = request.user.username if request.user.is_authenticated else ""
        
        # 3. エラーの具体的な種類とメッセージ（例: NameError: name 'xxx' is not defined）
        error_title = f"{type(exception).__name__}: {str(exception)}"
        
        # 4. どこでエラーが起きたかの詳細な追跡ログ（黄色い画面に表示されるコードの場所）
        tb_str = traceback.format_exc()
        
        # ログに登録！
        register_error_log(
            name="システムクラッシュ",
            message=f"【発生URL】 {url}\n【エラー】 {error_title}\n\n【詳細】\n{tb_str}",
            player=player_name,
            search_assist="500,クラッシュ,crash,サーバーエラー,system_error,例外"
        )
        
        return None