#会员信息管理视图文件
from django.shortcuts import render
from django.http import HttpResponse
from myadmin.models import Member
from django.core.paginator import Paginator
from datetime import datetime

# Create your views here.



# 浏览会员信息
def index(request,pIndex=1):
    mod = Member.objects

    list = mod.filter(status__lt=9)
    #执行分页处理
    pIndex = int(pIndex)
    page = Paginator(list,5) #以5条每页创建分页对象
    maxpages = page.num_pages #最大页数
    #判断页数是否越界
    if pIndex > maxpages:
        pIndex = maxpages
    if pIndex < 1:
        pIndex = 1
    list2 = page.page(pIndex) #当前页数据
    plist = page.page_range   #页码数列表

    #封装信息加载模板输出
    context = {"memberlist":list2,'plist':plist,'pIndex':pIndex,'maxpages':maxpages}
    return render(request,"myadmin/member/index.html",context)

def delete(request,uid=0):
    # 信息删除
    try:
        ob = User.objects.get(id = uid)
        ob.status = 9
        ob.update_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ob.save()
        context={'info':"删除成功！"}

    except Exception as err:
        print(err)
        context={'info':"删除失败！"}
    return render(request,"myadmin/info.html",context)

