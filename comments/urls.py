from django.conf.urls import url
from comments import views

urlpatterns = [
	url(r'^comment/(?P<book_id>\d+)$',views.comments, name='comment')
]
