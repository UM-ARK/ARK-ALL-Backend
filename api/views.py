import os

import json

import time
import uuid

import jwt
from pathlib import Path
from passlib.hash import pbkdf2_sha256
from datetime import datetime, timedelta, timezone
#import datetime

from spider import ummoodle_basicInfo
from utils import send_email
from threading import Thread

from django.shortcuts import render
from django.core.paginator import Paginator
from django.conf import settings

from django.views.decorators.csrf import csrf_protect


from data.models import *
import re

from mongoengine import *
from django.http import HttpResponse, JsonResponse


# Create your views here.
from data.models import Activity, OfficialUser, Club, Student, AppInfo
from data.enum import Faculty, Major, AccountStatus, ActivityType, ClubTag, NoticeType


SECRET_KEY = settings.SECRET_KEY
BASE_DIR = settings.BASE_DIR
STATIC_URL = settings.STATIC_URL
TOKEN_EXPIRED_TIME = 360 #hours
MAX_REFRESH_TOKEN_TIME =30 #day
COOKIE_MAX_AGE= MAX_REFRESH_TOKEN_TIME#day
SERVER_HOST = ""
TRUE_STRING_LIST = ["true","1","yes","True"]
China_timezone = timezone(timedelta(hours=8))
class Message:
    def __init__(self,code,message,content):
        self.code=code
        self.message=message
        self.content=content

    def build(self):
        res={
            "code":self.code,
            "message":self.message,
            "content":self.content
        }
        print((self.content[0]))
        return json.dumps(res)

def check_login():
    pass

# Todo
def signup(request):
    pass

# Todo
def email_var(request):
    pass

# Todo
def login(request):
    pass

# Todo
def get_news(request):
    pass

# Todo
def get_university_bus(request):
    pass



def API_result(code,detail="",token="",dtoken="",content="",return_HTTP=True):
    if code == -1:
        return HttpResponse(json.dumps(content), content_type='application/json')

    result={"code":str(code)}
    if code == 1:
        result["message"] = "success"
    if code == 10:
        result["message"] = "partial success"
    if code == 2:
        result["message"] = "data does not exist"
    if code == 20:
        result["message"] = "required parameter is empty"
    if code == 3:
        result["message"] = "token has expired"
    if code == 31:
        result["message"] = "refresh Token expired"
    if code == 400:
        result["message"] = " Bad Request"
    if code == 401:
        result["message"] = "wrong account or password"
    if code == 402:
        result["message"] = "Authentication failed"
    if code == 900:
        result["message"] = "unknown error"

    if detail!= "":
        result["detail"]=str(detail)
    if dtoken!= "":
        result["dtoken"] = dtoken
    if content!="":
        result["content"] = content

    if return_HTTP:
        response = HttpResponse(json.dumps(result),content_type='application/json')
        if token != "":
            response.set_cookie("ARK_TOKEN", token, max_age=COOKIE_MAX_AGE*60*60*24)
            return response
        else:
            return response
    else:
        return result




### web page
##@csrf_protect
def register_club_page(request):
    return render(request, "register_club_page.html")
def club_signin_page(request):
    return render(request, "sign_in_club_page.html", {'HOSTNAME': SERVER_HOST})
def renewal_token_page(request):
    return render(request, "renewal_token_page.html", {'HOSTNAME': SERVER_HOST})
def update_club_info_page(request):
    return render(request, "update_club_info_page.html", {'HOSTNAME': SERVER_HOST})
def upload_club_photos_page(request):
    return render(request, "upload_club_photos_page.html", {'HOSTNAME': SERVER_HOST})
def delete_club_photos_page(request):
    return render(request, "delete_club_photos_page.html", {'HOSTNAME': SERVER_HOST})
def create_activity_page(request):
    return render(request, "create_activity_page.html", {'HOSTNAME': SERVER_HOST})
def update_activity_info_page(request):
    return render(request, "update_activity_info_page.html", {'HOSTNAME': SERVER_HOST})
def delete_activity_page(request):
    return render(request, "delete_activity_page.html", {'HOSTNAME': SERVER_HOST})
def student_signin_page(request):
    return render(request, "student_signin_page.html", {'HOSTNAME': SERVER_HOST})

def student_add_follow_club_page(request):
    return render(request, "student_add_follow_club_page.html", {'HOSTNAME': SERVER_HOST})
def student_del_follow_club_page(request):
    return render(request, "student_del_follow_club_page.html", {'HOSTNAME': SERVER_HOST})
def get_follow_club_page(request):
    return render(request, "get_follow_club_page.html", {'HOSTNAME': SERVER_HOST})

def student_add_follow_activity_page(request):
    return render(request, "student_add_follow_activity_page.html", {'HOSTNAME': SERVER_HOST})
def student_del_follow_activity_page(request):
    return render(request, "student_del_follow_activity_page.html", {'HOSTNAME': SERVER_HOST})
def get_follow_activity_page(request):
    return render(request, "get_follow_activity_page.html", {'HOSTNAME': SERVER_HOST})
def get_club_info_page(request):
    return render(request, "get_club_info.html", {'HOSTNAME': SERVER_HOST})
def get_club_info_page2(request):
    return render(request, "get_club_info2.html", {'HOSTNAME': SERVER_HOST})



## API
##@csrf_protect
def register_new_club(request):
    input_token = request.POST.get("token")
    db_token = AppInfo.objects.all().values_list("admin_register_new_club_token")
    db_token = db_token.to_json()
    db_token = json.loads(db_token)[0]
    if input_token != db_token["admin_register_new_club_token"] or input_token == "":
        return API_result(400, detail="Insufficient permissions, refused to register")


    account = request.POST.get("account")
    password = request.POST.get("password")
    name = request.POST.get("name")
    tag = request.POST.get("tag")

    if account in Club.objects.all().values_list("club_account"):
        return API_result(400,detail="data already exists")
    if name in Club.objects.all().values_list("name"):
        return API_result(400, detail="data already exists")

    new_club = Club()

    id = str(uuid.uuid4())
    new_club.club_id = id

    new_club.club_account = account
    o_pw = password
    pw = pbkdf2_sha256.hash(o_pw)
    new_club.club_password = pw

    new_club.name = name
    new_club.tag = ClubTag(tag)

    ###########################
    storage_path = '/data/static/images/club/' + id + '/'
    image_url_path = STATIC_URL+'images/club/' + id + '/'
    post_filelist_name = "logo"
    ## handle_uploaded_file'
    if post_filelist_name in request.FILES:
        cover_image_file = request.FILES[post_filelist_name]
        ## handle_uploaded_file'
        image_path =  str(BASE_DIR).replace('\\', '/') + storage_path
        os.makedirs(image_path, exist_ok=True)
        sub_file_name = os.path.splitext(cover_image_file.name)[1]
        destination = open(os.path.join(image_path, "logo"+sub_file_name), 'wb+')
        for chunk in cover_image_file.chunks():
            destination.write(chunk)
        destination.close()
        new_club.logo_url = SERVER_HOST + image_url_path + "logo"+sub_file_name
    else:
        API_result(400,detail="lost logo file")

    new_club.club_num = club_num_increment()
    new_club.save()
    result = {
        'code': '1',
        'message': 'success',
        'id': id,
        #'account': account,
        #'password': o_pw
    }

    #return HttpResponse(json.dumps(result),content_type='application/
    return API_result(-1,content=result)

def club_signin(request):
    account = request.POST.get('account')
    password = request.POST.get('password')


    ##account and password verify
    try:
        club_account = Club.objects.get(club_account=account)
        #if club_account.club_password != password:
        if not pbkdf2_sha256.verify(password, club_account.club_password):
            return API_result(401)
    except Club.DoesNotExist:
        return API_result(401)


    id = club_account.club_id
    Club.objects(pk=id).update_one(set__login_time=datetime.now().timestamp())
    name = club_account.name
    iat = datetime.now(tz=timezone.utc)
    token = f_get_token(id,name,iat,"club",TOKEN_EXPIRED_TIME)

    club_obj = Club.objects.get(pk=id)
    content = club_obj.to_json()
    content = json.loads(content)
    ### Filter unnecessary data
    if "_id" in content:
        del content['_id']
    if 'club_password' in content:
        del content['club_password']
    if 'club_account' in content:
        del content['club_account']

    return API_result(1,token=token,content=content)

### JWT
def f_get_token(id,name,iat,role,expired_time = 24):
    data = {
        "exp": datetime.now(tz=timezone.utc) + timedelta(hours=expired_time),
        "iss": "ARK",
        "sub": id,
        "name": name,
        "iat": iat,
        "role": role,
    }

    # 加密 py3加密后是字节型数据
    encoded = jwt.encode(data, SECRET_KEY, algorithm='HS256')

    return encoded

def renewal_token(request):
    ## verify token
    #token = request.META.get('HTTP_AUTHORIZATION')
    token = request.COOKIES['ARK_TOKEN']
    token_check_result = f_check_token(token)
    if token_check_result["code"] == "1":
        pre_token_data = token_check_result["dtoken"]
        token = f_get_token(pre_token_data["sub"], pre_token_data["name"], pre_token_data["iat"],pre_token_data["role"] ,TOKEN_EXPIRED_TIME)
    elif token_check_result["code"] != "1":
        #return HttpResponse(json.dumps(token_check_result),content_type='application/json')
        return API_result(-1, content=token_check_result)

    return API_result(1,token=token)

def f_check_token(token):
    encoded_jwt = token

    now_iat = datetime.now(tz=timezone.utc)
    try:
        decode = jwt.decode(encoded_jwt,options={"verify_signature": False})
    except jwt.ExpiredSignatureError:
        return API_result(3,return_HTTP=False)
    except Exception:
        return API_result(402,return_HTTP=False)

    if now_iat - datetime.fromtimestamp(decode["iat"], tz=timezone.utc) > timedelta(days=MAX_REFRESH_TOKEN_TIME):
        return API_result(31, return_HTTP=False)

    try:
       decode = jwt.decode(encoded_jwt, SECRET_KEY, algorithms=['HS256'],options={"require": ["exp", "iss", "iat"]})
    except jwt.ExpiredSignatureError:
        return API_result(3,return_HTTP=False)
    except Exception as e:
        return API_result(900,detail=e,return_HTTP=False)

    return API_result(1,dtoken=decode,return_HTTP=False)


### club info
def f_set_page(request,data_list,page=1):
    # set page
    if request.GET.get("num_of_item"):
        paginator = Paginator(data_list, request.GET.get("num_of_item"))
        if request.GET.get("page"):
            if int(request.GET.get("page")) <= paginator.num_pages:
                page = request.GET.get("page")
            else:
                return API_result(2, detail="out of page number",return_HTTP=False)

        #page_content = paginator.page(page).object_list
        #num_pages = paginator.num_pages
        result = {
            "code":"1",
            "page_content":paginator.page(page).object_list,
            "num_pages":paginator.num_pages,
        }
    else:
        result = {
            "code": "1",
            "page_content":data_list,
            "num_pages":1,
        }
    return result

def f_upload_photos(request,post_filelist_name,storage_path,image_url_path):
    #club = Club.objects(pk=id)
    images_list = request.FILES.getlist(post_filelist_name)

    ## handle_uploaded_file'
    #club_images_path = str(BASE_DIR).replace('\\','/')+'/data/static/images/club/'+id+'/club_images/'
    images_path = str(BASE_DIR).replace('\\', '/') + storage_path
    images_url_list=[]
    os.makedirs(images_path, exist_ok=True)
    for image in images_list:
        images_url_list.append(SERVER_HOST+image_url_path+image.name)
        destination = open(os.path.join(images_path,image.name), 'wb+')
        for chunk in image.chunks():
            destination.write(chunk)
        destination.close()

    #db_entity.update_one(push_all__club_photos_list=images_url_list)
    return images_url_list
    pass
def f_delete_photos(request,post_filelist_name,storage_path):
    file_path_list = request.POST.get(post_filelist_name)
    try:
        file_path_list = json.loads(file_path_list)
    except Exception:
        result = {'code': '400'}
        return result
    images_path = str(BASE_DIR).replace('\\', '/') + storage_path
    can_not_remove = []
    removed_list =[]
    for file in file_path_list:
        image_name = file.split('/')[-1]
        try:
            os.remove(images_path+image_name)
            #db_entity.update_one(pull__club_photos_list=file)
            removed_list.append(file)
        except Exception:
            can_not_remove.append(file)

    if len(can_not_remove)>0:
        result = {
            'code': '10',
            'removed_list': removed_list,
            'can_not_remove': can_not_remove,

        }
        return result
    result = {
        'code': '1',
        'removed_list': removed_list,
    }
    return result
    pass

def f_upload_a_photo(request,post_file_name,storage_path,image_url_path):
    if post_file_name not in request.FILES:
        return ""

    image = request.FILES[post_file_name]
    images_path = str(BASE_DIR).replace('\\', '/') + storage_path
    image_url = SERVER_HOST + image_url_path + image.name
    os.makedirs(images_path, exist_ok=True)
    destination = open(os.path.join(images_path, image.name), 'wb+')
    for chunk in image.chunks():
        destination.write(chunk)
    destination.close()
    return image_url

def f_change_image(request,post_file_name,storage_path,image_url_path,remove_file_name):
    images_path = str(BASE_DIR).replace('\\', '/') + storage_path
    #file_name = Activity.objects.get(pk=activity_id).cover_image_url.split("/")[-1]
    os.remove(images_path + remove_file_name)
    ## handle_uploaded_file
    cover_image_file = request.FILES[post_file_name]
    os.makedirs(images_path, exist_ok=True)
    destination = open(os.path.join(images_path, cover_image_file.name), 'wb+')
    for chunk in cover_image_file.chunks():
        destination.write(chunk)
    destination.close()
    return SERVER_HOST+image_url_path+cover_image_file.name


def create_appinfo(request):
    new_appInfo = AppInfo()
    new_appInfo.id =  str(uuid.uuid4())
    carousel ={
        "url":"sdfs/sdfdsf"
    }
    carousel_list = [carousel]
    new_appInfo.index_head_carousel=carousel_list

    new_appInfo.API_version = "1.1.1"
    new_appInfo.app_version = "1.1.1"
    new_appInfo.save()
    return API_result(1)

def get_appinfo(request):
    resutl = AppInfo.objects.all().values_list("API_version","app_version","index_head_carousel")
    resutl=resutl.to_json()
    resutl=json.loads(resutl)[0]
    return API_result(1,content=resutl)

###!!!need to rewrite structure!!!
def get_club_info(request,mode):
    clubs = ""
    if mode == 'all':
        try:
            clubs_obj = Club.objects.all().values_list("club_num","logo_url","name","tag")
            clubs = clubs_obj.to_json()
            clubs = json.loads(clubs)

            #set page
            page =f_set_page(request, clubs)
            if page["code"] == "1":
                clubs = page["page_content"]
                num_pages = page["num_pages"]
            else:
                #return HttpResponse(json.dumps(page),content_type='application/json')
                return API_result(-1, content=page)

            ### Filter unnecessary data
            for club in clubs:
                # if '_id' in club:
                #     del club['_id']
                if 'club_password' in club:
                    del club['club_password']
                if 'club_account' in club:
                    del club['club_account']
        except Club.DoesNotExist:
            return API_result(2)
        # except Exception as e:
        #     return API_result(900,detail=e)


        result = API_result(1,content=clubs,return_HTTP=False)
        result["num_pages"]=num_pages

        if "ARK_TOKEN" in request.COOKIES:
            token = request.COOKIES['ARK_TOKEN']
            token_check_result = f_check_token(token)
            if token_check_result["code"] == "1":
                ####check student is follow
                # if token_check_result["dtoken"]["role"] == "student":
                #     for a in clubs:
                #         a["isFollow"] = a["_id"] in Student.objects().get(pk=token_check_result["dtoken"]["sub"]).follow_club_list
                ####----------------------
                pre_token_data = token_check_result["dtoken"]
                token = f_get_token(pre_token_data["sub"], pre_token_data["name"], pre_token_data["iat"],pre_token_data["role"], TOKEN_EXPIRED_TIME)
                response = HttpResponse(json.dumps(result),content_type='application/json')
                response.set_cookie("ARK_TOKEN", token, max_age=COOKIE_MAX_AGE*60*60*24)
                return response

        #return HttpResponse(json.dumps(result),content_type='application/json')
        return API_result(-1, content=result)

    if mode == 'club_num':
        id = request.GET.get('club_num')
        try:
            clubs_obj = Club.objects.get(club_num=id)
            clubs = clubs_obj.to_json()
            clubs = json.loads(clubs)

            ### Filter unnecessary data
            # if '_id' in clubs:
            #     del clubs['_id']
            if 'club_password' in clubs:
                del clubs['club_password']
            if 'club_account' in clubs:
                del clubs['club_account']

        except Club.DoesNotExist:
            return API_result(2)
        except Exception as e:
            return API_result(900,detail=e)

        if "ARK_TOKEN" in request.COOKIES:
            token = request.COOKIES['ARK_TOKEN']
            token_check_result = f_check_token(token)
            if token_check_result["code"] == "1":
                ####check student is follow
                if token_check_result["dtoken"]["role"] == "student":
                    clubs["isFollow"] = Club.objects.get(club_num=id).club_id in Student.objects().get(pk=token_check_result["dtoken"]["sub"]).follow_club_list
                ####----------------------
                    return API_result(1, content=clubs, token=token)
        return API_result(1, content=clubs)

    return API_result(400)
    pass

def edit_club_info(request):
    ## verify token
    #token = request.META.get('HTTP_AUTHORIZATION')
    token = request.COOKIES['ARK_TOKEN']
    token_check_result = f_check_token(token)
    if token_check_result["code"] != "1":
        #return HttpResponse(json.dumps(token_check_result),content_type='application/json')
        return API_result(-1, content=token_check_result)
    id =token_check_result["dtoken"]["sub"]
    name = token_check_result["dtoken"]["name"]
    if name not in Club.objects.all().values_list("name"):
        return API_result(400,detail="test")

    #get Club db_entity
    try:
        Club.objects.get(pk=id)
        club = Club.objects(pk=id)
    except Club.DoesNotExist:
        return API_result(2)
    except Exception as e:
        return API_result(900,detail=e)

    ## set introText to database
    intro = request.POST.get('intro')
    club.update_one(set__intro=intro)

    ## set contact to database
    contact = request.POST.get('contact')
    try:
        contact = json.loads(contact)
    except ValueError as e:
        return API_result(400,detail="malformed request")
    club.update_one(set__contact=contact)


    ##handle_uploaded_photo'
    db_entity = club
    storage_path="/data/static/images/club/"+id+"/club_images/"
    image_url_path=STATIC_URL+"images/club/"+id+"/club_images/"

    ### upload_photos
    post_filelist_name="add_club_photos"
    add_list = f_upload_photos(request,post_filelist_name,storage_path,image_url_path)
    for images_url in add_list:
        if images_url not in Club.objects.get(pk=id).club_photos_list:
            db_entity.update_one(push__club_photos_list=images_url)
    ### delete_photos
    post_filelist_name="del_club_photos"
    return_info = f_delete_photos(request, post_filelist_name, storage_path)
    removed_list = return_info["removed_list"]
    for file in removed_list:
        db_entity.update_one(pull__club_photos_list=file)

    pre_token_data = token_check_result["dtoken"]
    token = f_get_token(pre_token_data["sub"], pre_token_data["name"], pre_token_data["iat"],pre_token_data["role"], TOKEN_EXPIRED_TIME)
    return API_result(1,token=token)
    pass

### Activity info
def create_activity(request):
    ## verify token
    #token = request.META.get('HTTP_AUTHORIZATION')
    token = request.COOKIES['ARK_TOKEN']
    token_check_result = f_check_token(token)
    if token_check_result["code"] != "1":
        #return HttpResponse(json.dumps(token_check_result),content_type='application/json')
        return API_result(-1, content=token_check_result)

    club_id = token_check_result["dtoken"]["sub"]
    if club_id not in Club.objects.all().values_list("club_id"):
        return API_result(400)


    try:
        new_activity = Activity()
        activity_id = str(uuid.uuid4())
        new_activity.activity_id = activity_id
        new_activity.title = request.POST.get('title')
        new_activity.type = ActivityType(request.POST.get('type'))
        new_activity.location = request.POST.get('location')
        new_activity.introduction = request.POST.get('introduction')
        startdatetime = request.POST.get('startdatetime') + '+08:00'
        enddatetime = request.POST.get('enddatetime') + '+08:00'
        new_activity.startdatetime = datetime.timestamp(datetime.fromisoformat(startdatetime))
        new_activity.enddatetime = datetime.timestamp(datetime.fromisoformat(enddatetime))
        new_activity.can_follow= (request.POST.get('can_follow') in TRUE_STRING_LIST)


        link = request.POST.get('link')
        new_activity.link = link
        # if link != "" or link !="[]":
        #     if not re.match(r'^https?:/{2}\w.+$', link):
        #         return API_result(400, detail="link: URL invalid")
        #     else:
        #         new_activity.link = link

        club_id = token_check_result["dtoken"]["sub"]
        new_activity.created_by = club_id

        ## handle_uploaded_file'
        if 'cover_image_file' in request.FILES:
            cover_image_file = request.FILES['cover_image_file']
            ## handle_uploaded_file'
            activity_image_path = str(BASE_DIR).replace('\\','/')+'/data/static/images/activity/'+activity_id+'/'
            os.makedirs(activity_image_path, exist_ok=True)
            destination = open(os.path.join(activity_image_path,cover_image_file.name), 'wb+')
            for chunk in cover_image_file.chunks():
                destination.write(chunk)
            destination.close()

            new_activity.cover_image_url = SERVER_HOST+STATIC_URL+"images/activity/"+activity_id+"/"+cover_image_file.name

        ## handle_uploaded_file'
        relate_image_file = request.FILES.getlist('add_relate_image')
        relate_images_url_list = []
        for image in relate_image_file:
            url = SERVER_HOST+STATIC_URL+"images/activity/"+activity_id+"/"+image.name
            relate_images_url_list.append(url)
            destination = open(os.path.join(activity_image_path,image.name), 'wb+')
            for chunk in image.chunks():
                destination.write(chunk)
            destination.close()

        new_activity.relate_image_url = relate_images_url_list

        new_activity.timestamp = datetime.now(tz=timezone.utc).timestamp()
        new_activity.state = 1
        new_activity.save()
    except Exception as e:
        return API_result(900,detail=e)

    content={
        "id":activity_id
    }
    pre_token_data = token_check_result["dtoken"]
    token = f_get_token(pre_token_data["sub"], pre_token_data["name"], pre_token_data["iat"],pre_token_data["role"], TOKEN_EXPIRED_TIME)

    ##sent email
    Email_subject = "UMall - NEW Activity of " + Club.objects.get(club_id=club_id).name
    Email_content = "<img src='https://umall.one/static/logo.png'  width='150' >" +\
                    "<br><h3>"+Club.objects.get(club_id=club_id).name+"新活動</h3>"+\
                    "<br>標題: "+request.POST.get('title')+ \
                    "<br>發布者: " + Club.objects.get(club_id=club_id).name + \
                    "<br> 發布日期和時間: "+datetime.now(China_timezone).strftime("%m/%d/%Y, %H:%M:%S")+\
                    "<br>請打開app查看詳情"
    Email_add_list = Student.objects(follow_club_list__all=[club_id]).values_list("Student_email")

    Email_add_list = Email_add_list.to_json()
    Email_add_list = json.loads(Email_add_list)

    t1 = Thread(target=f_sent_email_by_list,args=(Email_subject,Email_content,Email_add_list))
    t1.start()


    return API_result(1,content=content,token=token)
    pass
def edit_activity(request):
    ## verify token
    token = request.COOKIES['ARK_TOKEN']
    token_check_result = f_check_token(token)
    if token_check_result["code"] != "1":
        #return HttpResponse(json.dumps(token_check_result),content_type='application/json')
        return API_result(-1, content=token_check_result)

    ######################################################################################################
    activity_id = request.POST.get("id")
    ## check the activity is exist
    try:
        Activity.objects.get(pk=activity_id)
    except Activity.DoesNotExist:
        return API_result(2)

    ## check the activity is delete
    if Activity.objects.get(pk=activity_id).state == 2:
        return API_result(400,detail="activity has deleted,can not change")

    ## check the activity is create by this club
    club_id = token_check_result["dtoken"]["sub"]
    if club_id != Activity.objects.get(pk=activity_id).created_by:
        return API_result(400)
    ######################################################################################################

    ##edit_activity operation
    activity = Activity.objects(pk=activity_id)
    title = request.POST.get('title')
    activity.update_one(set__title=title)
    location = request.POST.get('location')
    activity.update_one(set__location=location)
    introduction = request.POST.get('introduction')
    activity.update_one(set__introduction=introduction)
    startdatetime = request.POST.get('startdatetime') + '+08:00'
    enddatetime = request.POST.get('enddatetime') + '+08:00'
    activity.update_one(set__startdatetime=datetime.timestamp(datetime.fromisoformat(startdatetime)))
    activity.update_one(set__enddatetime=datetime.timestamp(datetime.fromisoformat(enddatetime)))
    can_follow = request.POST.get('can_follow') in TRUE_STRING_LIST
    activity.update_one(set__can_follow=can_follow)

    type = ActivityType(request.POST.get('type'))
    activity2 =Activity.objects.get(pk=activity_id)
    activity2.type = ActivityType(type)
    activity2.save()

    link = request.POST.get('link')
    activity.update_one(set__link=link)
    # if link != "":
    #     if not re.match(r'^https?:/{2}\w.+$', link):
    #         return API_result(400, detail="link: URL invalid")
    #     else:
    #         activity.update_one(set__link=link)
    # else:
    #     activity.update_one(unset__link=link)


    ## handle_uploaded_file
    ## change_image
    if 'cover_image_file' in request.FILES:
        storage_path = '/data/static/images/activity/' + activity_id + '/'
        image_url_path = STATIC_URL+'images/activity/' + activity_id + '/'
        cover_image_file="cover_image_file"
        remove_file_name = Activity.objects.get(pk=activity_id).cover_image_url.split("/")[-1]
        new_cover_image_URL=f_change_image(request, cover_image_file, storage_path, image_url_path,remove_file_name)
        activity.update_one(set__cover_image_url=new_cover_image_URL)



    ##handle_uploaded_photo'
    db_entity = activity
    storage_path="/data/static/images/activity/"+activity_id+"/"
    image_url_path=STATIC_URL+"images/activity/"+activity_id+"/"
    ### upload_photos
    post_filelist_name="add_relate_image"
    add_list = f_upload_photos(request,post_filelist_name,storage_path,image_url_path)
    for images_url in add_list:
        if images_url not in Activity.objects.get(pk=activity_id).relate_image_url:######
            db_entity.update_one(push__relate_image_url=images_url)
    ### delete_photos
    post_filelist_name="del_relate_image"
    return_info = f_delete_photos(request, post_filelist_name, storage_path)
    removed_list = return_info["removed_list"]
    for file in removed_list:
        db_entity.update_one(pull__relate_image_url=file)

    pre_token_data = token_check_result["dtoken"]
    token = f_get_token(pre_token_data["sub"], pre_token_data["name"], pre_token_data["iat"],pre_token_data["role"], TOKEN_EXPIRED_TIME)
    return API_result(1,token=token)
    pass
def delete_activity(request):
    ## verify token
    #token = request.META.get('HTTP_AUTHORIZATION')
    token = request.COOKIES['ARK_TOKEN']
    token_check_result = f_check_token(token)
    if token_check_result["code"] != "1":
        #return HttpResponse(json.dumps(token_check_result),content_type='application/json')
        return API_result(-1, content=token_check_result)

    ######################################################################################################
    activity_id = request.POST.get("id")
    ## check the activity is exist
    try:
        Activity.objects.get(pk=activity_id)
    except Activity.DoesNotExist:
        return API_result(2)

    ## check the activity is delete
    if Activity.objects.get(pk=activity_id).state == 2:
        return API_result(400,detail="activity has deleted,can not change")

    ## check the activity is create by this club
    club_id = token_check_result["dtoken"]["sub"]
    if club_id != Activity.objects.get(pk=activity_id).created_by:
        return API_result(400)
    ######################################################################################################


    activity = Activity.objects(pk=activity_id)
    activity.update_one(set__state=2)
    pre_token_data = token_check_result["dtoken"]
    token = f_get_token(pre_token_data["sub"], pre_token_data["name"], pre_token_data["iat"],pre_token_data["role"], TOKEN_EXPIRED_TIME)
    return API_result(1, token)
    pass

def get_activity(request,mode):
    filter_mode_array = ["sort_by","filter","showend"]
    now = datetime.now(tz=timezone.utc).timestamp()
    if mode=="all":
        url_query_array=request.META['QUERY_STRING'].split("&")
        print(url_query_array)
        if url_query_array[0] !='' or request.GET.get("showend") not in TRUE_STRING_LIST:
            #print("------------2")
            for url_query_parm in url_query_array:
                url_query_parm=url_query_parm.split("=")
                if url_query_parm[0] in filter_mode_array:
                    activity_obj = Activity.objects(state=1).order_by("-startdatetime")
                    #print("****************")
                    break

        if "activity_obj" not in locals():
            #print("-----------------")
            activity_obj1 = Activity.objects(state=1, enddatetime__gte=now).order_by("startdatetime")
            activity_obj2 = Activity.objects(state=1, enddatetime__lt=now).order_by("startdatetime")

            activitys1 = activity_obj1.to_json()
            activitys1 = json.loads(activitys1)

            activitys1.sort(key=lambda x: abs(datetime.now().timestamp() - x["startdatetime"]))

            activitys2 = activity_obj2.to_json()
            activitys2 = json.loads(activitys2)
            activitys1.extend(activitys2)
            activitys = activitys1


    if mode == "club_name":
        s = request.GET.get("s")
        club = Club.objects.get(name=s)
        activity_obj = Activity.objects(created_by=club.club_id, state=1).order_by("-startdatetime")
    if mode == "club_num":
        club_num = request.GET.get("club_num")
        club = Club.objects.get(club_num=club_num)
        activity_obj = Activity.objects(created_by=club.club_id, state=1).order_by("-startdatetime")
    if mode == "id":
        id = request.GET.get("id")
        activity_obj = Activity.objects(pk=id,state=1)


    if "activity_obj" in locals():
        sort_by = request.GET.get("sort_by")
        if sort_by == "postdate":
            if request.GET.get("rule") == "ascending":
                activity_obj=activity_obj.order_by("timestamp")
            if request.GET.get("rule") == "descending":
                activity_obj = activity_obj.order_by("-timestamp")

        if sort_by == "startdate":
            if request.GET.get("rule") == "ascending":
                activity_obj=activity_obj.order_by("startdatetime")
            if request.GET.get("rule") == "descending":
                activity_obj = activity_obj.order_by("-startdatetime")

        filter = request.GET.get("filter")
        if filter == "type":
            activity_obj=activity_obj.filter(type=ActivityType(request.GET.get("ActivityType")))

        showend = request.GET.get("showend")
        if showend == "false":
            activity_obj = activity_obj.filter(enddatetime__gte=now)


    if "activity_obj" in locals():
        activitys_json = activity_obj.to_json()
        activitys = json.loads(activitys_json)

    if len(activitys)==0:
        return API_result(2)

    # set page
    page = f_set_page(request, activitys)
    if page["code"] == "1":
        activitys = page["page_content"]
        num_pages = page["num_pages"]
    else:
        #return HttpResponse(json.dumps(page),content_type='application/json')
        return API_result(-1, content=page)

    #transform timestamp to utc
    #transform club id to club num
    if isinstance(activitys, list):
        for act in activitys:
            act["timestamp"] = str(datetime.fromtimestamp(act["timestamp"], tz=timezone.utc))
            act["startdatetime"] = str(datetime.fromtimestamp(act["startdatetime"], tz=timezone.utc))
            act["enddatetime"] = str(datetime.fromtimestamp(act["enddatetime"], tz=timezone.utc))
            act["created_by"] = Club.objects.get(pk=act["created_by"]).club_num
    else:
        activitys["timestamp"] = str(datetime.fromtimestamp(activitys["timestamp"], tz=timezone.utc))
        activitys["startdatetime"] = str(datetime.fromtimestamp(activitys["startdatetime"], tz=timezone.utc))
        activitys["enddatetime"] = str(datetime.fromtimestamp(activitys["enddatetime"], tz=timezone.utc))
        activitys["created_by"] = Club.objects.get(pk=activitys["created_by"]).club_num


    result = API_result(1, content=activitys, return_HTTP=False)
    result["num_pages"] = num_pages

    if "ARK_TOKEN" in request.COOKIES:
        token = request.COOKIES['ARK_TOKEN']
        token_check_result = f_check_token(token)
        if token_check_result["code"] == "1":
            #XXXXXXXXXXXXXXXXXXXXXXX
            ####check student is follow
            if token_check_result["dtoken"]["role"] == "student" and mode == "id":
                for a in result["content"]:
                   a["isFollow"] = a["_id"] in Student.objects().get(pk=token_check_result["dtoken"]["sub"]).follow_activity_list
            ####------------------------
            if len(result["content"])==1 and mode=="id":
                result["content"]=result["content"][0]
            # XXXXXXXXXXXXXXXXXXXXXXX


            pre_token_data = token_check_result["dtoken"]
            token = f_get_token(pre_token_data["sub"], pre_token_data["name"], pre_token_data["iat"],pre_token_data["role"],
                                TOKEN_EXPIRED_TIME)
            response = HttpResponse(json.dumps(result),content_type='application/json')
            response.set_cookie("ARK_TOKEN", token, max_age=COOKIE_MAX_AGE * 60 * 60 * 24)
            return response

    #return HttpResponse(json.dumps(result),content_type='application/json')
    ####------------------------
    if len(result["content"]) == 1 and mode=="id":
        result["content"] = result["content"][0]
    return API_result(-1, content=result)
    pass


def student_signin(request):
    #Verify student's ummoodle
    cookies = request.POST.get("cookies")
    basicInfo = ummoodle_basicInfo.basicInfo(cookies)
    try:
        student_basic_info = basicInfo.get_all_basic_info()  # return student_no:strint
        sid = student_basic_info["student_no"]
        sname = student_basic_info["student_name"].replace(" ","")
        semail = student_basic_info["email"]
        siconurl = student_basic_info["icon_url"]
    #     sid = basicInfo.get_student_no()
    #     sname = "test"
    #     semail = "test@test.com"
    #     siconurl = "http://test.com"
    except Exception as e:
        return API_result(402)

    ##Check if the student already has an account
    try:
        student_info=Student.objects.get(pk=sid)
        Student.objects(pk=sid).update_one(set__login_time=datetime.now().timestamp())
    except Student.DoesNotExist:
        new_student = Student()
        new_student.student_id = sid
        new_student.name = sname
        new_student.Student_email = semail
        new_student.icon_url = siconurl
        new_student.login_time = datetime.now().timestamp()
        new_student.save()
        pass

    id = sid
    name = sname
    iat = datetime.now(tz=timezone.utc)
    token = f_get_token(id,name,iat,"student",TOKEN_EXPIRED_TIME)
    #content = Student.objects(pk=sid).values_list("name","Student_email","icon_url")
    content = Student.objects.get(pk=sid)
    content = content.to_json()
    content = json.loads(content)
    return API_result(1,token=token,content=content)

def student_add_follow_club(request):
    ## verify token
    #token = request.META.get('HTTP_AUTHORIZATION')
    token = request.COOKIES['ARK_TOKEN']
    token_check_result = f_check_token(token)
    if token_check_result["code"] != "1":
        #return HttpResponse(json.dumps(token_check_result),content_type='application/json')
        return API_result(-1, content=token_check_result)

    ######################################################################################################
    student_id = token_check_result["dtoken"]["sub"]
    student_name = token_check_result["dtoken"]["name"]
    if student_id not in Student.objects.all().values_list("student_id") or \
        student_name not in Student.objects.all().values_list("name"):
        return API_result(400)

    student = Student.objects(pk=student_id)
    follow_club = request.POST.get("club")
    # if follow_club not in Club.objects.all().values_list("name"):
    #     return API_result(2)
    club = Club.objects.get(club_num=follow_club)
    club_id = club.club_id
    if club_id not in Club.objects.all().values_list("club_id"):
        return API_result(2)

    if club_id in Student.objects.get(pk=student_id).follow_club_list:
        return API_result(400,detail="data already exists")
    ######################################################################################################

    student.update_one(push__follow_club_list=club_id)
    pre_token_data = token_check_result["dtoken"]
    token = f_get_token(pre_token_data["sub"], pre_token_data["name"], pre_token_data["iat"],pre_token_data["role"], TOKEN_EXPIRED_TIME)
    return API_result(1,token=token)
def student_del_follow_club(request):
    ## verify token
    #token = request.META.get('HTTP_AUTHORIZATION')
    token = request.COOKIES['ARK_TOKEN']
    token_check_result = f_check_token(token)
    if token_check_result["code"] != "1":
        #return HttpResponse(json.dumps(token_check_result),content_type='application/json')
        return API_result(-1, content=token_check_result)

    ######################################################################################################
    student_id = token_check_result["dtoken"]["sub"]
    student_name = token_check_result["dtoken"]["name"]
    if student_id not in Student.objects.all().values_list("student_id") or \
        student_name not in Student.objects.all().values_list("name"):
        return API_result(400)

    student = Student.objects(pk=student_id)
    follow_club = request.POST.get("club")
    # if follow_club not in Club.objects.all().values_list("name"):
    #     return API_result(400)
    club = Club.objects.get(club_num=follow_club)
    club_id = club.club_id
    if club_id not in Club.objects.all().values_list("club_id"):
        return API_result(2)
    if club_id not in Student.objects.get(pk=student_id).follow_club_list:
        return API_result(2)
    ######################################################################################################

    student.update_one(pull__follow_club_list=club_id)
    pre_token_data = token_check_result["dtoken"]
    token = f_get_token(pre_token_data["sub"], pre_token_data["name"], pre_token_data["iat"],pre_token_data["role"], TOKEN_EXPIRED_TIME)
    return API_result(1,token=token)
def get_follow_club(request):
    ## verify token
    #token = request.META.get('HTTP_AUTHORIZATION')
    token = request.COOKIES['ARK_TOKEN']
    token_check_result = f_check_token(token)
    if token_check_result["code"] != "1":
        #return HttpResponse(json.dumps(token_check_result),content_type='application/json')
        return API_result(-1, content=token_check_result)
    pre_token_data = token_check_result["dtoken"]

    if pre_token_data["role"]=="student":
        student_id = token_check_result["dtoken"]["sub"]
        student_name = token_check_result["dtoken"]["name"]
        if student_id not in Student.objects.all().values_list("student_id") or \
            student_name not in Student.objects.all().values_list("name"):
            return API_result(400)

        ###use follow_club_name list to query full info by club
        #content = Student.objects.get(pk=student_id).follow_club_list
        content=[]
        follow_club_list=Student.objects.get(pk=student_id).follow_club_list
        for follow_club_id in follow_club_list:
            try:
                clubs_obj = Club.objects(club_id=follow_club_id).values_list("club_num", "logo_url", "name", "tag")
                clubs = clubs_obj.to_json()
                clubs = json.loads(clubs)[0]
                content.append(clubs)
            except Exception:
                pass

    if pre_token_data["role"]=="club":
        club_id = token_check_result["dtoken"]["sub"]
        club_name = token_check_result["dtoken"]["name"]
        if club_id not in Club.objects.all().values_list("club_id") or \
            club_name not in Club.objects.all().values_list("name"):
            return API_result(400)

        #content = Student.objects(__raw__={"follow_club_list" : {"$all" : ['ARK']}}).values_list("name")
        content = Student.objects(follow_club_list__all=[club_id]).values_list("name","student_id")
        content=content.to_json()
        content = json.loads(content)

    # set page
    page = f_set_page(request, content)
    if page["code"] == "1":
        content = page["page_content"]
        num_pages = page["num_pages"]
    else:
       ## return HttpResponse(json.dumps(page),content_type='application/json')
        return API_result(-1, content=page)

    result = API_result(1, content=content, return_HTTP=False)
    result["num_pages"] = num_pages

    token = f_get_token(pre_token_data["sub"], pre_token_data["name"], pre_token_data["iat"],pre_token_data["role"], TOKEN_EXPIRED_TIME)
    response = HttpResponse(json.dumps(result),content_type='application/json')
    response.set_cookie("ARK_TOKEN", token, max_age=COOKIE_MAX_AGE*60*60*24)

    return response



def student_add_follow_activity(request):
    ## verify token
    #token = request.META.get('HTTP_AUTHORIZATION')
    token = request.COOKIES['ARK_TOKEN']
    token_check_result = f_check_token(token)
    if token_check_result["code"] != "1":
        #return HttpResponse(json.dumps(token_check_result),content_type='application/json')
        return API_result(-1, content=token_check_result)

    ######################################################################################################
    student_id = token_check_result["dtoken"]["sub"]
    student_name = token_check_result["dtoken"]["name"]
    if student_id not in Student.objects.all().values_list("student_id") or \
        student_name not in Student.objects.all().values_list("name"):
        return API_result(400)

    student = Student.objects(pk=student_id)
    follow_activity = request.POST.get("activity_id")
    if Activity.objects.get(pk=follow_activity).state == 2:
         return API_result(400,detail="Activity has been deleted")
    if Activity.objects.get(pk=follow_activity).state != 1:
         return API_result(400,detail="Activity can not follow ")
    if not Activity.objects.get(pk=follow_activity).can_follow:
         return API_result(400,detail="Activity are not allowed to follow")
    if follow_activity not in Activity.objects.all().values_list("activity_id"):
        return API_result(2)
    if follow_activity in Student.objects.get(pk=student_id).follow_activity_list:
        return API_result(400,detail="Data already exists")
    ######################################################################################################

    student.update_one(push__follow_activity_list=follow_activity)
    pre_token_data = token_check_result["dtoken"]
    token = f_get_token(pre_token_data["sub"], pre_token_data["name"], pre_token_data["iat"],pre_token_data["role"], TOKEN_EXPIRED_TIME)
    return API_result(1,token=token)
def student_del_follow_activity(request):
    ## verify token
    #token = request.META.get('HTTP_AUTHORIZATION')
    token = request.COOKIES['ARK_TOKEN']
    token_check_result = f_check_token(token)
    if token_check_result["code"] != "1":
        # return HttpResponse(json.dumps(token_check_result),content_type='application/json')
        return API_result(-1, content=token_check_result)

    ######################################################################################################
    student_id = token_check_result["dtoken"]["sub"]
    student_name = token_check_result["dtoken"]["name"]
    if student_id not in Student.objects.all().values_list("student_id") or \
        student_name not in Student.objects.all().values_list("name"):
        return API_result(400)

    student = Student.objects(pk=student_id)
    follow_activity = request.POST.get("activity_id")
    if follow_activity not in Activity.objects.all().values_list("activity_id"):
        return API_result(2)
    if follow_activity not in Student.objects.get(pk=student_id).follow_activity_list:
        return API_result(2)
    ######################################################################################################
    student.update_one(pull__follow_activity_list=follow_activity)
    pre_token_data = token_check_result["dtoken"]
    token = f_get_token(pre_token_data["sub"], pre_token_data["name"], pre_token_data["iat"],pre_token_data["role"], TOKEN_EXPIRED_TIME)
    return API_result(1,token=token)


def get_follow_activity(request):
    ## verify token
    #token = request.META.get('HTTP_AUTHORIZATION')
    token = request.COOKIES['ARK_TOKEN']
    token_check_result = f_check_token(token)
    if token_check_result["code"] != "1":
        # return HttpResponse(json.dumps(token_check_result),content_type='application/json')
        return API_result(-1, content=token_check_result)
    pre_token_data = token_check_result["dtoken"]

    if pre_token_data["role"]=="student":
        ######################################################################################################
        student_id = token_check_result["dtoken"]["sub"]
        student_name = token_check_result["dtoken"]["name"]
        if student_id not in Student.objects.all().values_list("student_id") or \
            student_name not in Student.objects.all().values_list("name"):
            return API_result(400)
        ######################################################################################################

        ###use follow_activity_id list to query full info by activity
        #content = Student.objects.get(pk=student_id).follow_activity_list
        content=[]
        follow_activity_list=Student.objects.get(pk=student_id).follow_activity_list
        for follow_activity_id in follow_activity_list:
            try:
                activity_obj = Activity.objects(activity_id=follow_activity_id).values_list( "title","created_by","cover_image_url","startdatetime","enddatetime","timestamp")
                activity = activity_obj.to_json()
                activity = json.loads(activity)[0]
                activity["timestamp"] = str(datetime.fromtimestamp(activity["timestamp"], tz=timezone.utc))
                activity["startdatetime"] = str(datetime.fromtimestamp(activity["startdatetime"], tz=timezone.utc))
                activity["enddatetime"] = str(datetime.fromtimestamp(activity["enddatetime"], tz=timezone.utc))
                activity["created_by"] = Club.objects.get(pk=activity["created_by"]).club_num
                content.append(activity)
            except Exception:
                pass
    if pre_token_data["role"]=="club":
        ######################################################################################################
        club_id = token_check_result["dtoken"]["sub"]
        club_name = token_check_result["dtoken"]["name"]
        if club_id not in Club.objects.all().values_list("club_id") or \
            club_name not in Club.objects.all().values_list("name"):
            return API_result(400)
        ######################################################################################################
        activity_id = request.GET.get("activity_id")
        if activity_id not in Activity.objects.all().values_list("activity_id"):
            return API_result(2,detail="activity not exists")
        content = Student.objects(follow_activity_list__all=[activity_id]).values_list("name","student_id")
        content=content.to_json()
        content = json.loads(content)


    # set page
    page = f_set_page(request, content)
    if page["code"] == "1":
        content = page["page_content"]
        num_pages = page["num_pages"]
    else:
        #return HttpResponse(json.dumps(page),content_type='application/json')
        return API_result(-1, content=page)


    result = API_result(1, content=content, return_HTTP=False)
    result["num_pages"] = num_pages

    token = f_get_token(pre_token_data["sub"], pre_token_data["name"], pre_token_data["iat"],pre_token_data["role"], TOKEN_EXPIRED_TIME)
    response = HttpResponse(json.dumps(result),content_type='application/json')
    response.set_cookie("ARK_TOKEN", token, max_age=COOKIE_MAX_AGE*60*60*24)
    return response


def create_notice(request):
    ## verify token
    token = request.COOKIES['ARK_TOKEN']
    token_check_result = f_check_token(token)
    if token_check_result["code"] != "1":
        #return HttpResponse(json.dumps(token_check_result),content_type='application/json')
        return API_result(-1, content=token_check_result)

    ## check role is club
    club_id =token_check_result["dtoken"]["sub"]
    if token_check_result["dtoken"]["sub"] not in Club.objects.values_list("club_id"):
        return API_result(400)


    new_notice = Notice()

    notice_id = str(uuid.uuid4())
    new_notice.notice_id = notice_id

    now = datetime.now(China_timezone).timestamp()
    new_notice.post_datetime = now

    notice_for = request.POST.get("notice_for")
    new_notice.notice_for = notice_for

    notice_type = request.POST.get("notice_type")
    new_notice.notice_type=NoticeType(notice_type)

    title = request.POST.get("title")
    new_notice.title = title

    new_notice.created_by=club_id

    if "link" in request.POST:
        link = request.POST.get("link")
        new_notice.link=link

    if "activity_id" in request.POST:
        activity_id = request.POST.get("activity_id")
        if activity_id in Activity.objects.values_list("activity_id"):
            new_notice.activity_id=activity_id
        else:
            return API_result(2,detail="activity_id not exist in database")

    ## upload_image
    storage_path = "/data/static/images/notice/"+notice_id+"/"
    image_url_path = STATIC_URL+"images/notice/"+notice_id+"/"
    post_file_name = "image"
    image_url=f_upload_a_photo(request,post_file_name,storage_path,image_url_path)
    new_notice.image_url = image_url

    new_notice.state=1
    new_notice.save()

    content={
        "id":notice_id
    }
    pre_token_data = token_check_result["dtoken"]
    token = f_get_token(pre_token_data["sub"], pre_token_data["name"], pre_token_data["iat"],pre_token_data["role"], TOKEN_EXPIRED_TIME)

    ##sent email
    Email_subject = "UMall - NEW notice of " + Club.objects.get(club_id=club_id).name
    Email_content = "<img src='https://umall.one/static/logo.png'  width='150' >" +\
                    "<br><h3>新公告</h3>"+\
                    "<br>發布者: "+Club.objects.get(club_id=club_id).name+\
                    "<br>內容: "+title+\
                    "<br>告示類型: "+notice_for+\
                    "<br> 發布日期和時間: "+datetime.now(China_timezone).strftime("%m/%d/%Y, %H:%M:%S")+\
                    "<br>請打開app查看詳情"
    if notice_for == "CLUB":
        Email_add_list = Student.objects(follow_club_list__all=[club_id]).values_list("Student_email")
    elif notice_for == "ACTIVITY" and "activity_id" in request.POST:
        Email_add_list = Student.objects(follow_activity_list__all=[activity_id]).values_list("Student_email")
        print(Email_add_list)
    else:
        print("[====> some_error : 1")

    Email_add_list = Email_add_list.to_json()
    Email_add_list = json.loads(Email_add_list)

    t1 = Thread(target=f_sent_email_by_list,args=(Email_subject,Email_content,Email_add_list))
    t1.start()

    return API_result(1,content=content,token=token)

def f_sent_email_by_list(Email_subject,Email_content,Email_add_list):
    for email_add in Email_add_list:
        send_email.send_mail(Email_subject, Email_content, email_add["Student_email"], "")
    return 0





def edit_notice(request):
    ## verify token
    token = request.COOKIES['ARK_TOKEN']
    token_check_result = f_check_token(token)
    if token_check_result["code"] != "1":
        #return HttpResponse(json.dumps(token_check_result),content_type='application/json')
        return API_result(-1, content=token_check_result)

    ######################################################################################################
    ## check role is club
    club_id =token_check_result["dtoken"]["sub"]
    if token_check_result["dtoken"]["sub"] not in Club.objects.values_list("club_id"):
        return API_result(400)

    ## check notice has exist
    notice_id = request.POST.get("notice_id")
    if notice_id not in Notice.objects.values_list("notice_id"):
        return API_result(400)

    ## check the notice is create by this club
    if club_id != Notice.objects.get(pk=notice_id).created_by:
        return API_result(400)

    ## check the notice is delete
    if Notice.objects.get(pk=notice_id).state == 2:
        return API_result(400,detail="Notice has deleted,can not change")
    ######################################################################################################

    notice = Notice.objects(pk=notice_id)
    title = request.POST.get('title')
    notice.update_one(set__title=title)

    notice_type = request.POST.get('notice_type')
    notice.update_one(set__notice_type=NoticeType(notice_type))

    if "image" in request.FILES:
        storage_path = "/data/static/images/notice/"+notice_id+"/"
        image_url_path = STATIC_URL+"images/notice/"+notice_id+"/"
        post_file_name = "image"
        remove_file_name = Notice.objects.get(pk=notice_id).image_url.split("/")[-1]
        new_image_url=f_change_image(request,post_file_name,storage_path,image_url_path,remove_file_name)
        notice.update_one(set__image_url=new_image_url)

    if "link" in request.POST:
        link = request.POST.get('link')
        notice.update_one(set__link=link)


    pre_token_data = token_check_result["dtoken"]
    token = f_get_token(pre_token_data["sub"], pre_token_data["name"], pre_token_data["iat"],pre_token_data["role"], TOKEN_EXPIRED_TIME)
    return API_result(1,token=token)




def delete_notice(request):
    ## verify token
    token = request.COOKIES['ARK_TOKEN']
    token_check_result = f_check_token(token)
    if token_check_result["code"] != "1":
        #return HttpResponse(json.dumps(token_check_result),content_type='application/json')
        return API_result(-1, content=token_check_result)

    ######################################################################################################
    ## check role is club
    club_id =token_check_result["dtoken"]["sub"]
    if token_check_result["dtoken"]["sub"] not in Club.objects.values_list("club_id"):
        return API_result(400)

    ## check notice has exist
    notice_id = request.POST.get("notice_id")
    if notice_id not in Notice.objects.values_list("notice_id"):
        return API_result(400)

    ## check the notice is create by this club
    if club_id != Notice.objects.get(pk=notice_id).created_by:
        return API_result(400)

    ## check the notice is delete
    if Notice.objects.get(pk=notice_id).state == 2:
        return API_result(400,detail="Notice has deleted,can not change")
    ######################################################################################################

    notice = Notice.objects(pk=notice_id)
    notice.update_one(set__state=2)

    pre_token_data = token_check_result["dtoken"]
    token = f_get_token(pre_token_data["sub"], pre_token_data["name"], pre_token_data["iat"],pre_token_data["role"], TOKEN_EXPIRED_TIME)
    return API_result(1, token=token)

def get_notice(request,mode):
    ## verify token
    token = request.COOKIES['ARK_TOKEN']
    token_check_result = f_check_token(token)
    if token_check_result["code"] != "1":
        #return HttpResponse(json.dumps(token_check_result),content_type='application/json')
        return API_result(-1, content=token_check_result)
    pre_token_data = token_check_result["dtoken"]

    if pre_token_data["role"]=="student":
        ###student
        if token_check_result["dtoken"]["sub"] in Student.objects.values_list("student_id"):
            if mode == "activity":
                activity_id = request.GET.get("activity_id")
                notice_obj = Notice.objects(activity_id=activity_id, state=1).order_by("-post_datetime")
            if mode == "club":
                club_num = request.GET.get("club_num")
                club = Club.objects.get(club_num=club_num)
                notice_obj = Notice.objects(created_by=club.club_id, state=1, notice_for="CLUB").order_by("-post_datetime")

    if pre_token_data["role"]=="club":
        ###club:get all notice for this club
        if token_check_result["dtoken"]["sub"] in Club.objects.values_list("club_id"):
            club = Club.objects.get(club_id=token_check_result["dtoken"]["sub"])
            if mode == "all":
                notice_obj = Notice.objects(created_by=club.club_id, state=1).order_by("-post_datetime")
            if mode == "activity":
                activity_id = request.GET.get("activity_id")
                notice_obj = Notice.objects(created_by=club.club_id,activity_id=activity_id, state=1).order_by("-post_datetime")
            if mode == "club":
                club_num = request.GET.get("club_num")
                notice_obj = Notice.objects(created_by=club.club_id,  notice_for="CLUB", state=1).order_by("-post_datetime")

    if "notice_obj" not in locals():
       return API_result(400,detail="Mode error or Authentication failed")

    notice = notice_obj.to_json()
    notice = json.loads(notice)


    # set page
    page = f_set_page(request, notice)
    if page["code"] == "1":
        notice = page["page_content"]
        num_pages = page["num_pages"]
    else:
        #return HttpResponse(json.dumps(page),content_type='application/json')
        return API_result(-1, content=page)

    #transform timestamp to utc
    #transform club id to club num
    if isinstance(notice, list):
        for act in notice:
            act["post_datetime"] = str(datetime.fromtimestamp(act["post_datetime"], tz=timezone.utc))
            act["created_by"] = Club.objects.get(pk=act["created_by"]).club_num
    else:
        notice["post_datetime"] = str(datetime.fromtimestamp(notice["post_datetime"], tz=timezone.utc))
        notice["created_by"] = Club.objects.get(pk=notice["created_by"]).club_num

    if len(notice) == 0 :
        return API_result(2)

    result = API_result(1, content=notice, return_HTTP=False)
    result["num_pages"] = num_pages


    ## renew token
    token = f_get_token(pre_token_data["sub"], pre_token_data["name"], pre_token_data["iat"],pre_token_data["role"],
                        TOKEN_EXPIRED_TIME)
    response =API_result(-1, content=result)
    response.set_cookie("ARK_TOKEN", token, max_age=COOKIE_MAX_AGE * 60 * 60 * 24)
    return response
    pass

def sent_mail_test(requset):
    print("123")
    Email_subject = "NEW notice of ARK"
    # Email_content = "<img src='https://umall.one/static/logo.png'  width='500' >" \
    #                 "<br>title: test2"\
    #                 "<br> post_datetime: "+datetime.now(China_timezone).strftime("%m/%d/%Y, %H:%M:%S")+\
    #                 "<br><a href='https://umall.one/openapp/'>打開app查看詳情</a>"
    Email_content = "test"
    result = send_email.send_mail(Email_subject, Email_content, 'tonyche351@gmail.com', "")
    print("result:",result)
    return API_result(1)








def test_user(request):
    t = OfficialUser()
    t.email = 'testsadasdas@um.mo'
    t.name = 'b'
    t.pw = 'a'
    t.last_login=time.time()
    t.creat_at=time.time()
    t.account_state=AccountStatus.SIGNUP
    t.save()
    return HttpResponse("success")

def test2_user(request):
    t=OfficialUser.objects(name='b')

    return HttpResponse("{} {} {}".format(t[0].email,str(2),str(len(t))))

def test_activity(request):
    t=Activity()
    t.activity_id=str(uuid.uuid4())
    t.title="Test Activity 1"
    t.type=ActivityType.OFFICIAL
    t.link="https://boxz.dev"
    t.created_by="testsadasdas@um.mo"
    t.cover_image_url="https://websso.um.edu.mo/adfs/portal/logo/logo.png"
    t.relate_image_url=['https://websso.um.edu.mo/adfs/portal/logo/logo.png',
                        'https://websso.um.edu.mo/adfs/portal/logo/logo.png',
                        'https://websso.um.edu.mo/adfs/portal/logo/logo.png']
    t.timestamp=time.time()
    t.save()
    return HttpResponse("success")

def test2_activity(request):
    t=Activity.objects(title="Test Activity 1")

    return HttpResponse("{} {} {}".format(str(len(t)),
                                          str(t.first().title),
                                          str(type(t.first().relate_image_url))))

def test_club(request):
    t=Club()
    t.club_id=str(uuid.uuid4())
    t.name="Test Club 1"
    t.tag=ClubTag.SOCIETY
    t.intro="Fuck u"
    t.contact={
        'type':'facebook',
        'info':'test page'
    }
    t.save()
    return HttpResponse("success")

def test2_club(request):
    t=Club.objects(name="Test Club 1")

    return HttpResponse("{} {} {} {}".format(str(len(t)),
                                             str(t.first().name),
                                             str(type(t.first().contact)),
                                             str(t.first().contact['info'])))
# def get_activity(request):
#     activity_list=list(Activity.objects())
#     for i in range(len(activity_list)):
#         activity_list[i]=activity_list[i].info()
#     res=Message(1,'success',activity_list).build()
#     return HttpResponse(res,content_type="application/json")

