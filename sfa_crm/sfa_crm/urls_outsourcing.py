from django.urls import path, include

urlpatterns = [
    # 外注用アプリのみを読み込む
    path('outsourcing/', include('outsourcing.urls')),
]