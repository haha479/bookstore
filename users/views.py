# -*- encoding:utf-8 -*-
from django.shortcuts import render,redirect
from django.core.urlresolvers import reverse
from users.models import *
from django.http import JsonResponse,HttpResponse
import re
from utils.decorators import login_required
from order.models import OrderInfo
from order.models import OrderGods
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from bookstore import settings
from django.core.mail import send_mail

# 注册页面
def register(request):
	return render(request, 'users/register.html')

# 注册校验
def register_handle(request):
	username = request.POST.get('user_name')
	password = request.POST.get('pwd')
	email = request.POST.get('email')
	# 进行数据校验
	if not all([username, password, email]):
		# 有数据为空
		return render(request, 'users/register.html', {'errmsg': '参数不能为空!'})

	# 判断邮箱是否合法
	if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
		# 邮箱不合法
		return render(request, 'users/register.html', {'errmsg': '邮箱不合法!'})
	passport = Passport.objects.add_one_passport(username=username,password=password,email=email)

	# 生成激活的token itsdangerous
	serializer = Serializer(settings.SECRET_KEY, 3600)
	token = serializer.dumps({'confirm': passport.id}) # 返回bytes
	token = token.decode()

	# 给用户的邮箱发送激活邮件
	send_mail('尚硅谷书城用户激活', '', settings.EMAIL_FROM, [email], html_message='<a href="http://127.0.0.1:8000/users/active/%s/">http://127.0.0.1:8000/users/active/</a>' % token)

	if passport == None:
		return render(request,'users/register.html',{"errmsg": '账号已经存在！'})
	return redirect(reverse('users:login'),)

# 登陆页面
def login(request):
	username = ""
	checked = ""
	context = {
		'username' : username,
		'checked' : checked
	}
	return render(request,'users/login.html',context)

def logout(request):
	"""用户退出登陆"""
	request.session.flush()
	# 跳转到首页
	return render(request,'book/index.html')

# 登陆校验
def login_check(request):
	username = request.POST.get("username")
	password = request.POST.get('password')
	remember = request.POST.get('remember')

	# 数据校验
	if not all([username,password,remember]):
		# 其中有数据为空
		return JsonResponse({'res':2})

	# 进行处理
	passport = Passport.objects.get_one_passport(username=username,password=password)

	# 如果存在为True
	if passport :
		next_url = request.session.get('url_path',reverse('book:index'))
		jres = JsonResponse({'res':1,'next_url':next_url})

		# 判断是否记住用户名
		if remember == True :
			# 将用户的信息存到cookie
			jres.set_cookie('username', username, max_age=7*24*3600)
		else :
			jres.delete_cookie("username")

		# 记住用户的登陆状态(将用户的登陆信息存到session)
		request.session['islogin'] = True
		request.session['username'] = username
		request.session['passport_id'] = passport.id
		return jres
	else :
		# 用户名或密码错误
		return JsonResponse({'res':0})


	# context = {'username':username,'password':password,'remember':remember}
	# return render(request,'users/index.html',context)

@login_required
def user(request):
	"""用户中心,信息页"""
	passport_id = request.session.get('passport_id')
	# 获取用户的基本信息
	addr = Address.objects.get_default_address(passport_id=passport_id)
	books_li = []
	context = {
		'addr' : addr,
		'page' : 'user',
		'books_li' : books_li,
	}

	return render(request,'users/user_center_info.html',context)


@login_required
def address(request):
	'''
		用户中心,地址页
		1.显示地址
		2.添加地址
	'''
	# 获取登陆用户的id
	passport_id = request.session.get('passport_id')
	if request.method == "GET":
		# 显示地址页面
		# 查询用户的默认地址
		print("*" * 30)
		addr = Address.objects.get_default_address(passport_id=passport_id)

		return render(request,'users/user_center_site.html',{'addr': addr, 'page':'address'})
	else :
		print("*" * 50)
		# 添加收货地址
		# 1.接收数据
		recipient_name = request.POST.get('username')
		recipient_addr = request.POST.get('addr')
		zip_code = request.POST.get('zip_code')
		recipient_phone = request.POST.get('phone')

		# 2.进行校验
		if not all([recipient_name,recipient_addr,zip_code,recipient_phone]):
			return render(request,'users/user_center_site.html',{'errmsg': '参数不能为空'})

		# 3.添加收货地址
		Address.objects.add_one_address(passport_id=passport_id,
										recipient_name=recipient_name,
										recipient_addr=recipient_addr,
										zip_code=zip_code,
										recipient_phone=recipient_phone)
		# 4.返回应答
		return redirect(reverse('users:address'))
@login_required
def order(request):
	'''用户中心-订单页'''
	# 查询用户的订单信息
	passport_id = request.session.get('passport_id')

	# 获取订单信息
	order_li = OrderInfo.objects.filter(passport_id=passport_id)

	# 遍历获取订单的商品信息
	# order->OrderInfo实例对象
	for order in order_li:
		# 根据订单id查询订单商品信息
		order_id = order.order_id
		order_books_li = OrderGods.objects.filter(order_id=order_id)

		# 计算商品的小计
		# order_books ->OrderBooks实例对象
		for order_books in order_books_li:
			count = order_books.count
			price = order_books.price
			amount = count * price
			# 保存订单中每一个商品的小计
			order_books.amount = amount

		# 给order对象动态增加一个属性order_goods_li,保存订单中商品的信息
		order.order_books_li = order_books_li

	context = {
		'order_li': order_li,
		'page': 'order'
	}

	return render(request, 'users/user_center_order.html', context)
















