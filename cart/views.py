from django.shortcuts import render
from django.http import JsonResponse
from book.models import Books
from django_redis import get_redis_connection
from utils.decorators import login_required


def cart_add(request):
	'''
		向购物车中添加数据
		将购物车-书的id-书的数量,以字典的形式使用hset存入redis数据库
	'''
	# 判断用户是否登陆
	if not request.session.has_key('islogin'):
		return JsonResponse({'res':0,'errmsg':'请先登陆'})

	# 接收数据
	books_id = request.POST.get('books_id')
	books_count = request.POST.get('books_count')


	# 进行数据检验
	if not all([books_id,books_count]):
		return JsonResponse({'res':1,'errmsg':"数据不完整"})

	books = Books.objects.get_books_by_id(books_id=books_id)
	if books is None :
		# 商品不存在
		return JsonResponse({'res':2,'errmsg':'商品不存在'})

	try :
		count = int(books_count)
	except Exception as e:
		# 商品数目不合法
		return JsonResponse({'res':3,'errmsg':'商品数量必须为数字'})

	# 添加商品到购物车
	# 每个用户的购物车记录用一条hash数据保存,格式:cart_用户id:商品id 商品数量
	conn = get_redis_connection('default') # 链接redis数据库

	cart_key = 'cart_%d' % request.session.get('passport_id') # 通过用户的id创建指定的购物车来存入redis

	res = conn.hget(cart_key, books_id)
	if res is None:
		# 如果用户的购物车中没有添加过该商品,则添加数据
		res = count
	else :
		# 如果用户的购物车中已经添加过该商品, 则累计商品数目
		res = int(res) + count

	# 判断商品的库存
	if res > books.stock:
		# 库存不足
		return JsonResponse({'res':4, 'errmsg': '商品库存不足'})
	else :
		conn.hset(cart_key, books_id, res)

	# 返回结果
	return JsonResponse({'res': 5})


def cart_count(request):
	'''判断用户购物车中商品的数目'''
	# 判断用户是否登陆
	if not request.session.has_key('islogin'):
		return JsonResponse({'res': 0})

	# 计算用户购物车商品的数量
	conn = get_redis_connection('default')
	cart_key = 'cart_%d' % request.session.get('passport_id')

	res = 0
	res_list = conn.hvals(cart_key)

	for i in res_list:
		res += int(i)

	# 返回结果
	return JsonResponse({'res': res})


@login_required
def cart_show(request):
	'''显示用户购物车页面'''
	passport_id = request.session.get('passport_id')
	# 获取用户购物车的记录
	conn = get_redis_connection('default')
	cart_key = 'cart_%d' % passport_id
	res_dict = conn.hgetall(cart_key)

	books_li = []
	# 保存所有商品的总数
	total_count = 0
	# 保存所有商品的总价格
	total_price = 0

	# 遍历res_dict获取商品的数据
	for id, count in res_dict.items():
		# 根据id获取商品的信息
		books = Books.objects.get_books_by_id(books_id=id)
		# 保存商品的数目
		books.count = count
		# 保存商品的小计
		books.amount = int(count) * books.price
		books_li.append(books)

		total_count += int(count)
		total_price += int(count) * books.price

	# 定义模板上下文
	context = {
		'books_li' : books_li,
		'total_count' : total_count,
		'total_price' : total_price,
	}

	return render(request,'cart/cart.html',context=context)

def cart_del(request):
	'''
		删除用户购物车中商品的信息
		删除redis数据库中的购物车-书id-对应的值
	'''
	# 判断用户是否登陆
	if not request.session.has_key('islogin'):
		return JsonResponse({'res': 0, 'errmsg': '请先登陆'})

	# 接收数据
	books_id = request.POST.get('books_id')

	# 检验商品是否存放
	if not all([books_id]):
		return JsonResponse({'res': 1, 'errmsg': '数据不完整'})

	books = Books.objects.get_books_by_id(books_id=books_id)
	if books is None:
		return JsonResponse({'res': 2, 'errmsg': '商品不存在'})

	# 删除购物车商品信息
	conn = get_redis_connection('default')
	cart_key = 'cart_%d' % request.session.get('passport_id')
	conn.hdel(cart_key, books_id)

	# 返回信息
	return JsonResponse({'res': 3})

def cart_update(request):
	'''
		更新购物车商品数目
		** 只要是购物车中商品的数量变化了都会触发该函数
	'''
	# 判断用户是否登陆
	if not request.session.has_key('islogin'):
		return JsonResponse({'res': 0, 'errmsg': '请先登陆'})

	# 接收数据
	books_id = request.POST.get('books_id')
	books_count = request.POST.get('books_count')

	# 数据的检验
	if not all([books_id, books_count]):
		return JsonResponse({'res': 1,'errmsg': '数据不完整'})

	books = Books.objects.get_books_by_id(books_id=books_id)
	if books is None:
		return JsonResponse({'res': 2, 'errmsg': '商品不存在'})

	try :
		books_count = int(books_count)
	except Exception as e:
		return JsonResponse({'res': 3, 'errmsg': '商品数目必须为数字'})

	# 更新操作
	conn = get_redis_connection('default')
	cart_key = 'cart_%d' % request.session.get('passport_id')

	# 判断商品库存
	if books_count > books.stock:
		return JsonResponse({'res': 4, 'errmsg': '商品库存不足'})

	conn.hset(cart_key, books_id, books_count)

	return JsonResponse({'res': 5})


























