from django.shortcuts import render,redirect
from utils.decorators import login_required
from django.core.urlresolvers import reverse
from users.models import Address
from book.models import Books
from order.models import OrderInfo
from order.models import OrderGods
from django_redis import get_redis_connection
from django.db import transaction
from django.http import HttpResponse,JsonResponse
from datetime import datetime
import time


@login_required
def order_place(request):
	'''显示提交订单页面'''
	# 接收数据
	books_ids = request.POST.getlist('books_ids')

	# 校验数据
	if not all(books_ids):
		# 跳转到购物车页面
		return redirect(reverse('cart:show'))

	# 用户收货地址
	passport_id = request.session.get('passport_id')
	addrs = Address.objects.all()
	# 用户要购买的商品信息
	books_li = []
	# 商品的总数目和总金额
	total_count = 0
	total_price = 0

	conn = get_redis_connection('default')
	cart_key = 'cart_%d' % passport_id

	for id in books_ids:
		# 根据id获取商品的信息
		book = Books.objects.get_books_by_id(books_id=id)
		# 从redis中获取用户要购买的商品的数目
		count = conn.hget(cart_key,id)
		book.count = count
		# 计算商品的小计(商品数量 * 价格)
		amount = int(book.count) * book.price
		book.amount = amount
		books_li.append(book)

		# 累计计算商品的总数目和总金额
		total_count += int(count)
		# 将所有商品的小计都相加到总金额
		total_price += book.amount

	# 商品运费和实付款
	transit_price = 10
	total_pay = total_price + transit_price

	# 1,2,3
	books_ids = ','.join(books_ids)
	# 组织模板上下文
	context = {
		'addrs' : addrs,
		'books_li': books_li,
		'total_count': total_count,
		'total_price': total_price,
		'transit_price': transit_price,
		'total_pay': total_pay,
		'books_ids': books_ids,
	}

	# 使用模板
	return render(request,'order/place_order.html',context=context)


@transaction.atomic
def order_commit(request):
	'''生成订单'''
	# 验证用户是否登陆
	if not request.session.has_key('islogin'):
		return JsonResponse({'res':0, 'errmsg': '用户为登陆'})

	# 接收数据
	addr_id = request.POST.get('addr_id')
	pay_method = request.POST.get('pay_method')
	books_id = request.POST.get('books_ids')

	# 进行数据检验
	if not all([addr_id, pay_method, books_id]):
		return JsonResponse({'res':1, 'errmsg': '数据不完整'})

	try:
		addr = Address.objects.get(id=addr_id)
	except Exception as e:
		# 地址信息出错
		return JsonResponse({'res':2, 'errmsg': '地址信息错误'})

	if int(pay_method) not in OrderInfo.PAY_METHOD_EMUM.values():
		return JsonResponse({'res': 3, 'errmsg': '不支持的支付方式'})

	# 订单创建
	# 组织订单信息
	passport_id = request.session.get('passport_id')
	# 订单id : 20171212...+ 用户的id
	order_id = datetime.now().strftime('%Y%m%d%H%M%S') + str(passport_id)
	# 运费
	transit_price = 10
	# 订单商品总数和总金额
	total_count = 0
	total_price = 0

	# 创建一个保存点
	sid = transaction.savepoint()
	try:
		# 向订单信息表中添加一条记录
		order = OrderInfo.objects.create(order_id=order_id,
										 passport_id = passport_id,
										 addr_id=addr_id,
										 total_count=total_count,
										 total_price=total_price,
										 transit_price=transit_price,
										 pay_method=pay_method)

		# 向订单商品表中添加订单商品的记录
		books_ids = books_id.split(',')
		conn = get_redis_connection('default')
		cart_key = 'cart_%d' % passport_id

		# 遍历获取用户购买的商品信息
		for id in books_ids:
			books = Books.objects.get_books_by_id(books_id=id)
			if books is None:
				transaction.savepoint_rollback(sid)
				return JsonResponse({'res':4, 'errmsg': '商品信息错误'})

			# 获取用户购买的商品数目
			count = conn.hget(cart_key, id)

			# 判断商品的库存
			if int(count) > books.stock:
				transaction.savepoint_rollback(sid)
				return JsonResponse({'res': 5, 'errmsg': '商品库存不足'})

			# 创建一条订单商品记录
			OrderGods.objects.create(order_id=order_id,
									 books_id=id,
									 count=count,
									 price=books.price
									 )

			# 增加商品的销量,　减少商品库存
			books.sales += int(count)
			total_price += int(count)
			books.save()

			# 累计计算商品的总数目和总额
			total_count += int(count)
			total_price += int(count) * books.price

		# 更新订单的商品总数目和总金额
		order.total_count = total_count
		order.total_price = total_price

	except Exception as e:
		# 操作数据库出错, 进行回滚操作
		transaction.savepoint_rollback(sid)
		return JsonResponse({'res': 7, 'errmsg': '服务器错误'})

	# 清楚购物车对应记录
	conn.hdel(cart_key, *books_ids)

	# 事物提交
	transaction.savepoint_commit(sid)
	# 返回应答
	return JsonResponse({'res': 6})



















