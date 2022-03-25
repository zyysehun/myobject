from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.core.paginator import Paginator
from datetime import datetime
import time,os

from myadmin.models import Category,Shop,Product

# 菜品分类信息

def index(request,pIndex=1):
    '''浏览信息'''
    smod = Product.objects
    mywhere=[]
    list = smod.filter(status__lt=9)

    # 获取、判断并封装关keyword键搜索
    kw = request.GET.get("keyword",None)
    if kw:
        # 查询店铺名称中只要含有关键字就可以
        list = list.filter(name__contains=kw)
        mywhere.append("keyword="+kw)

    # 获取并判断搜索菜品类别条件
    cid = request.GET.get("category_id",None)
    if cid:
        # 查询店铺名称中只要含有关键字就可以
        list = list.filter(category_id=cid)
        mywhere.append("keyword="+cid)

    # 获取、判断并封装状态status搜索条件
    status = request.GET.get('status','')
    if status != '':
        list = list.filter(status=status)
        mywhere.append("status="+status)

    #执行分页处理
    pIndex = int(pIndex)
    page = Paginator(list,10) #以10条每页创建分页对象
    maxpages = page.num_pages #最大页数
    #判断页数是否越界
    if pIndex > maxpages:
        pIndex = maxpages
    if pIndex < 1:
        pIndex = 1
    list2 = page.page(pIndex) #当前页数据
    plist = page.page_range   #页码数列表

    #遍历当前菜品信息并封装对应的店铺和菜品类别信息
    for vo in list2:
        sob = Shop.objects.get(id=vo.shop_id)
        vo.shopname = sob.name
        cob = Category.objects.get(id = vo.category_id)
        vo.categoryname = cob.name
    #封装信息加载模板输出
    context = {"productlist":list2,'plist':plist,'pIndex':pIndex,'maxpages':maxpages,'mywhere':mywhere}
    return render(request,"myadmin/product/index.html",context)

def loadCategory(request,sid):
    clist = Category.objects.filter(status__lt=9,shop_id=sid).values("id","name")
    #返回QuerySet对象，使用list强转成对应的菜品分类列表信息
    return JsonResponse({'data':list(clist)})

def add(request):
    '''加载添加页面'''
    slist = Shop.objects.values("id","name")
    context={"shoplist":slist}
    return render(request,"myadmin/product/add.html",context)

def insert(request):
    '''执行添加'''
    try:

        #图片的上传处理
        myfile = request.FILES.get("cover_pic",None)
        if not myfile:
            return HttpResponse("没有封面上传文件信息")
        cover_pic = str(time.time())+"."+myfile.name.split('.').pop()
        destination = open("./static/uploads/product/"+cover_pic,"wb+")
        for chunk in myfile.chunks():      # 分块写入文件  
            destination.write(chunk)  
        destination.close()

        ob = Product()
        ob.shop_id = request.POST['shop_id']
        ob.category_id = request.POST['category_id']
        ob.name = request.POST['name']
        ob.price= request.POST['price']
        ob.cover_pic = cover_pic

        ob.status = 1
        ob.create_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ob.update_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ob.save()
        context={"info":"添加成功！"}
    except Exception as err:
        print(err)
        context={"info":"添加失败"}
    return render(request,"myadmin/info.html",context)

def delete(request,pid=0):
    '''执行信息删除'''
    try:
        ob = Product.objects.get(id=pid)
        ob.status = 9
        ob.update_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ob.save()
        context = {'info':"删除成功！"}
    except Exception as err:
        print(err)
        context = {'info':"删除失败！"}
    return render(request,"myadmin/info.html",context)



def edit(request,pid):
    '''加载编辑信息页面'''
    try:
        ob = Product.objects.get(id=pid)
        slist = Shop.objects.values("id","name")
        context={"product":ob,"shoplist":slist}
        return render(request,"myadmin/product/edit.html",context)
    except Exception as err:
        context={"info":"没有找到要修改的信息！"}
        return render(request,"myadmin/info.html",context)

def update(request,pid):
    '''执行编辑信息'''
    try:

        #获取原图片
        oldpicname = request.POST['oldpicname']
        #图片的上传处理
        myfile = request.FILES.get("cover_pic",None)
        if not myfile:
            cover_pic = oldpicname
        else:
            cover_pic = str(time.time())+"."+myfile.name.split('.').pop()
            destination = open("./static/uploads/product/"+cover_pic,"wb+")
            for chunk in myfile.chunks():      # 分块写入文件  
                destination.write(chunk)  
            destination.close()

        ob = Product.objects.get(id=pid)
        ob.shop_id = request.POST['shop_id']
        ob.category_id = request.POST['category_id']
        ob.name = request.POST['name']
        ob.price = request.POST['price']
        ob.cover_pic = cover_pic
        ob.update_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ob.save()
        context={"info":"修改成功！"}

        #判断并删除老图片
        if myfile:
            os.remove("./static/uploads/product/"+oldpicname)

    except Exception as err:
         #判断并删除新图片
        if myfile:
            os.remove("./static/uploads/product/"+cover_pic)
        print(err)
        context={"info":"修改失败"}
    return render(request,"myadmin/info.html",context)