# sfa_crm/wsgi_outsourcing.py
import os
import sys

# 1. settings のパスを通す
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sfa_crm.settings')

# 2. Djangoの設定オブジェクトをインポート
from django.conf import settings
import django

# ★ここが重要：django.setup() の「前」に ROOT_URLCONF を外注用に上書きする
settings.ROOT_URLCONF = 'sfa_crm.urls_outsourcing'

# 3. その後でセットアップを実行
django.setup()

# 4. アプリケーションを取得
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()