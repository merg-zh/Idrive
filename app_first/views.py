from django.shortcuts import redirect, render
from app_first import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from app_first.models import data
from idrive.settings import STATICFILES_DIRS
import os

def TopView(request):
    form_login = forms.LoginForm()
    form_signin = UserCreationForm()
    ms = ""

    if request.method == 'POST':
        if request.POST['password'] != 'null':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('/home')
        elif request.POST['password1'] != "null":
            form = UserCreationForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                return redirect('/home')
            for i in User.objects.all():
                if request.POST['username'] == str(i):
                    ms = '※この名前はすでに使われています'

    if request.user.is_authenticated == True:
        return HomeView(request)
    else:
        return render(request, 'app_first/top.html',{'form_login':form_login, 'form_signin':form_signin, 'ms':ms})
import base64
def HomeView(request):
    username = str(request.user)
    if data.objects.filter(username = username).exists() == False:
        user_data = data.objects.create(username = username, title=[], play_list = [])
        os.mkdir(STATICFILES_DIRS[0] +"/"+username)
    else:
        user_data = data.objects.get(username = username)
    if request.method == "POST":
        if 'file' in request.FILES:
            names = []
            contents = []
            for f in request.FILES.getlist('file'):
                names.append(f.name)
                contents.append(f.read())
            for i,name in enumerate(names):
                name = name[:-4]
                if not name in user_data.title:
                    user_data.title.append(name)
                    with open(STATICFILES_DIRS[0] +"/"+username+"/"+name, "wb") as f:
                        f.write(contents[i])
        elif 'delete_post' in request.POST:
            delete_name = request.POST['st']
            num = user_data.title.index(delete_name)
            user_data.title.pop(num)
            os.remove(STATICFILES_DIRS[0] +"/"+username+"/"+delete_name+".mp3")
        elif 'createlist' in request.POST:
            new_list_name = request.POST['list_name']
            if user_data.play_list == []:
                user_data.play_list.append(new_list_name)
                user_data.play_list.append("null")
            else:
                text = user_data.play_list[0]
                if new_list_name not in text.split("$$"):
                    text += '$$' + new_list_name
                    user_data.play_list[0] = text
                    user_data.play_list[1] += "###null"
        elif 'append_playlist' in request.POST:
            text = (request.POST['name_cout']).split('$$')
            text2 = user_data.play_list[1].split("###")
            num = user_data.play_list[0].split('$$').index(text[0])
            if text2[num] == "null":
                text2[num] = text[1]
            else:
                text2[num] += "$$" + text[1]
            text2 = "###".join(text2)
            user_data.play_list[1] = text2
        elif 'delete_pl' in request.POST:
            text = (request.POST['list_name']).split("$$")
            if len(user_data.play_list[1].split("###")) == 1:
                user_data.play_list[1] = "null"
            else:
                text2 = user_data.play_list[1].split("###")
                num = int(text[1]) - 1
                if "$$" in text2[num]:
                    text3 = text2[num].split("$$")
                    text4 = user_data.title[int(text[0]) - 1]
                    text3.remove(text4)
                    text2[num] = "$$".join(text3)
                    user_data.play_list[1] = "###".join(text2)
                else:
                    text2[num] = "null"
                    user_data.play_list[1] = "###".join(text2)

    user_data.save()

    title = user_data.title
    if user_data.play_list != []:
        play_list = user_data.play_list[1]
    else:
        play_list = ""
    if user_data.play_list == []:
        pl = ""
    else:
        pl = (user_data.play_list[0]).split('$$')
    return render(request, 'app_first/Home.html', {'title':title, 'list_names':pl, 'play_list':play_list})

class LogoutView(LoginRequiredMixin, LogoutView):
    template_name = "app_first/top.html"

#'list_dir':os.listdir(STATICFILES_DIRS[0]+"/merg-zh")
