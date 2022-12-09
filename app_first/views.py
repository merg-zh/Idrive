from django.shortcuts import redirect, render
from app_first import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from app_first.models import data
from idrive.settings import STATICFILES_DIRS
from yt_dlp import YoutubeDL
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
                    with open(STATICFILES_DIRS[0] +"/"+username+"/"+name+".mp3", "wb") as f:
                        f.write(contents[i])
        elif 'delete_post' in request.POST:
            text = request.POST['st'].split(",")
            delete_name = text[0]
            num = user_data.title.index(delete_name)
            user_data.title.pop(num)
            os.remove(STATICFILES_DIRS[0] +"/"+username+"/"+delete_name+".mp3")

            text.pop(0)
            for i in text:
                if i != "":
                    if len(user_data.play_list[1].split("###")) == 1:
                            user_data.play_list[1] = "null"
                    else:
                        text2 = user_data.play_list[1].split("###")
                        i = int(i)
                        if "$$" in text2[i]:
                            text3 = text2[i].split("$$")
                            text4 = user_data.title[int(num) - 1]
                            text3.remove(text4)
                            text2[i] = "$$".join(text3)
                            user_data.play_list[1] = "###".join(text2)
                        else:
                            text2[i] = "null"
                            user_data.play_list[1] = "###".join(text2)
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
        elif 'delete_playlist' in request.POST:
            text = request.POST['delete_playlist']
            num = int(text) - 1
            text2 = user_data.play_list
            if len(text2[0].split("$$")) == 1:
                user_data.play_list = ""
            else:
                text3 = text2[0].split("$$")
                text3.pop(num)
                text2[0] = "$$".join(text3)
                text3 = text2[1].split("###")
                text3.pop(num)
                text2[1] = '###'.join(text3)

    user_data.save()

    title = user_data.title
    if user_data.play_list != [] and user_data.play_list != "":
        play_list = user_data.play_list[1]
        pl = (user_data.play_list[0]).split('$$')
    else:
        play_list = ""
        pl = ""
        
    return render(request, 'app_first/Home.html', {'title':title, 'list_names':pl, 'play_list':play_list, 'volume':user_data.volume})

def Dy(request):
    username = str(request.user)
    user_data = data.objects.get(username = username)
    if 'download' in request.POST:
        link = request.POST['link']
        name = str(request.POST['name'])
        if link and name:
            ydl_opts = {
                "format": "mp3/bestaudio/best",
                "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                }
                ],
            }
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])
            dir_path = "" 
            dir_list = os.listdir(dir_path)
            path = ""
            for i in range(len(dir_list)):
              if ".mp3" == os.path.splitext(dir_list[i])[1]:
                path = os.path.join(dir_path, dir_list[i])
            os.rename(path, STATICFILES_DIRS[0] +"/"+username+"/"+name+".mp3")
            user_data.title.append(name)
            user_data.save()
    return render(request, 'app_first/Dy.html')

class LogoutView(LoginRequiredMixin, LogoutView):
    template_name = "app_first/top.html"

def Ajax_Append_List(request):
    user_data = data.objects.get(username = request.user)
    text = str(request.POST.get('name_cout')).split('$$')
    text2 = user_data.play_list[1].split("###")
    num = user_data.play_list[0].split('$$').index(text[0])
    if text2[num] == "null":
        text2[num] = text[1]
    else:
        test = text2[num].split("$$")
        jatch = False
        if text[1] in test:
            if test[test.index(text[1])] == test[1]:
                jatch = True
        
        if jatch == False:
            text2[num] += "$$" + text[1]
    text2 = "###".join(text2)
    user_data.play_list[1] = text2

    user_data.save()
    return HomeView(request)

def Ajax_Left_List(request):
    user_data = data.objects.get(username = request.user)
    text = (request.POST.get('song_name')).split("$$")
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
    return HomeView(request)

#'list_dir':os.listdir(STATICFILES_DIRS[0]+"/merg-zh")
