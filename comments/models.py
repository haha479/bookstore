# -*- encoding:utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from db.base_model import BaseModel
from users.models import Passport
from book.models import Books


class Comments(BaseModel):
	show = models.BooleanField(default=True,verbose_name='显示评论')
	content = models.CharField(max_length=1000,verbose_name='评论内容')
	passport = models.ForeignKey('users.Passport',)
	book = models.ForeignKey('book.Books')

	class Meta:
		db_table = 's_comments'
