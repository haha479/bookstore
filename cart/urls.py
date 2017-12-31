from django.conf.urls import url
from cart import views

urlpatterns = [
	url(r'^add/$',views.cart_add,name='add'),
	url(r'^$',views.cart_show,name='show'),
	url(r'^count/$',views.cart_count,name='count'),
	url(r'^del/$', views.cart_del, name='delete'),
	url(r'^update/$',views.cart_update,name='update')
]