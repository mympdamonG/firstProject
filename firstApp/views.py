from django.contrib.auth import  authenticate, login, logout
from django.contrib.auth.forms import  AuthenticationForm, PasswordChangeForm, PasswordResetForm
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.core.paginator import Paginator
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
######make def
from firstApp.models import Users, firstAppUrls
from firstApp.forms import RegisterForm, LoginForm, UrlCreateForm

# Create your views here.

def index(request):
    user = Users.objects.filter(id=request.user.id).first()
    email = user.email if user else "Anonymous User!"
    print("logged in?" ,request.user.is_authenticated)
    
    if request.user.is_authenticated is False:
        email = "Anonymous User!"
        print(email)
    return render(request, "base.html", {"welcome_msg" : "Hello firstProject" })    




@csrf_exempt
def get_user(request, user_id):
    print(user_id)
    if request.method == "GET":
        abc = request.GET.get("abc") 
        xyz = request.GET.get("xyz")   
        user = Users.objects.filter(pk=user_id).first() 
        return render(request,"base.html",{"user":user, "params":[abc,xyz]})
    elif request.method == "POST":
        username = request.GET.get("username")

        if username:
            user = Users.objects.filter(pk=user_id).update(username=username)    
        return JsonResponse(status=201, data=dict(msg="YOU JUST REACHED WITH POST METHOD!"), safe=False)        

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        msg = "올바르지 않은 데이터입니다."
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username = username, password = raw_password)
            login(request, user)
            msg = "회원가입이 완료되었습니다.!"
        return render(request, "register.html",{"form": form,  "msg" : msg}) 
             
    else:
        form = RegisterForm()    
        return render(request, "register.html",{"form": form})                 

# def login_view(request):
#     if request.method == "POST":
#         form = AuthenticationForm(request, request.POST)
#         msg = "가입되어 있지 않거나 로그인 정보가 잘못되었습니다."
#         print(form.is_valid)
#         if form.is_valid():
#             username = form.cleaned_data.get("username")
#             raw_password = form.cleaned_data.get("password")
#             user = authenticate(username=username, password=raw_password)
#             if user is not None:
#                 msg = "로그인 성공!!!"
#                 login(request, user)
#         return render(request, "login.html",{"form":form,"msg":msg})  
#     else:
#         form = AuthenticationForm()
#         return render(request, "login.html",{"form":form})  

def login_view(request):
    is_ok = False
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            raw_password = form.cleaned_data.get("password")
            remember_me = form.cleaned_data.get("remember_me")
            msg = "올바른 유저ID와 패스워드를 입력하세요."
            try:
                user = Users.objects.get(email=email)
            except Users.DoesNotExist:
                msg = "500error올바른 유저ID와 패스워드를 입력하세요."
            else:
                if user.check_password(raw_password):
                    msg = None
                    login(request, user)
                    is_ok = True
                    request.session["remember_me"] = remember_me

                    # if not remember_me:
                    #      request.session.set_expirey(0)
    else:
        msg = None
        form = LoginForm()
    print("REMEMBER_ME: ", request.session.get("remember_me"))
    return render(request, "login.html", {"form": form, "msg": msg, "is_ok": is_ok})



def logout_view(request):
    
    logout(request)
    return redirect("login")

@login_required
def list_view(request):
    page = int(request.GET.get("p",1))
    users = Users.objects.all().order_by("-id") 
    paginator = Paginator(users,10)
    users = paginator.get_page(page)

    return render(request,"boards.html",{"users": users})  


@login_required
def url_create(request):
    msg = None
    if request.method == "POST":
        form = UrlCreateForm(request.POST)
        if form.is_valid():
            msg = f"{form.cleaned_data.get('nick_name')} 생성 완료!"
            messages.add_message(request, messages.INFO, msg)
            form.save(request)
            return redirect("url_list")
        else:
            form = UrlCreateForm()
    else:
        form = UrlCreateForm()
    return render(request, "url_create.html", {"form": form})


@login_required
def url_change(request, action, url_id):
    if request.method == "POST":
        url_data = firstAppUrls.objects.filter(id=url_id)
        if url_data.exists():
            if url_data.first().created_by_id != request.user.id:
                msg = "자신이 소유하지 않은 URL 입니다."
            else:
                if action == "delete":
                    msg = f"{url_data.first().nick_name} 삭제 완료!"
                    url_data.delete()
                    messages.add_message(request, messages.INFO, msg)
                elif action == "update":
                    msg = f"{url_data.first().nick_name} 수정 완료!"
                    form = UrlCreateForm(request.POST)
                    form.update_form(request, url_id)

                    messages.add_message(request, messages.INFO, msg)
        else:
            msg = "해당 URL 정보를 찾을 수 없습니다."

    elif request.method == "GET" and action == "update":
        url_data = firstAppUrls.objects.filter(pk=url_id).first()
        form = UrlCreateForm(instance=url_data)
        return render(request, "url_create.html", {"form": form, "is_update": True})

    return redirect("url_list")

def url_list(request):
    get_list = firstAppUrls.objects.order_by("-created_at").all()
    return render(request, "url_list.html", {"list": get_list})