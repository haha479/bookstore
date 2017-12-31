# -*- encoding:utf-8 -*-
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from comments.models import Comments
from django.http import JsonResponse
import json


@csrf_exempt
def comments(request, book_id):
	if request.method == "GET":
		comments = Comments.objects.filter(book_id=book_id)

		res = []
		for c in comments:
			res.append({
				'create_time' : c.create_time,
				'user_id' : c.user_id,
				'content' : c.content,
			})

		return JsonResponse({
			'code' : 200,
			'data' : res,
		})

	elif request.method == 'POST':
		data = json.loads(request.body.decode('utf-8'))
		content = data.get('content')
		book_id = data.get('book_id')
		user_id = request.session.get('passport_id')

		c = Comments(content=content, book_id=book_id, passport_id=user_id)
		c.save()

		return JsonResponse({
			'code':200,
			'msg':'评论成功'
		})
