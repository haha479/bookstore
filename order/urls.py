from django.conf.urls import url
from order import views

urlpatterns = [
	url(r'^place/$',views.order_place,name='place'),
	url(r'^commit/$',views.order_commit,name='commit')
]