from mongoengine import *
from data.enum import AccountStatus, ActivityType, ClubTag, NoticeType

def club_num_increment():
    try:
        largest = Club.objects.all().order_by('-club_num').first()
        return largest.club_num + 1
    except Exception:
        return 0


class AppInfo(Document):
    id = StringField(primary_key=True)
    index_head_carousel = ListField()
    API_version = StringField()
    app_version = StringField()
    admin_register_new_club_token = StringField()


class OfficialUser(Document):
    email = EmailField(required=True, primary_key=True)
    pw = StringField(max_length=50, required=True)
    name = StringField(max_length=1024)
    profile_image = StringField(max_length=1024)
    last_login = IntField()
    creat_at = IntField()
    account_state = EnumField(AccountStatus, default=AccountStatus.NA)

    last_login = IntField()
    creat_at = IntField()

    account_state = EnumField(AccountStatus, default=AccountStatus.NA)
    def info(self):
        res = {
            'email': self.email,
            'name': self.name,
            'profile_image': self.profile_image,
            'last_login': self.last_login,
            'creat_at': self.creat_at,
            'account_state': self.account_state,
        }
        return res


class User(Document):
    student_id = StringField(max_length=50, required=True, primary_key=True)
    profile_image = StringField(max_length=1024)
    created_at = StringField(max_length=1024)
    fo_clud = ListField()
    fo_activity = ListField()
    cookie_last_update = StringField(max_length=1024)
    cookie_content = StringField(max_length=2048)

    def info(self):
        res = {
            'student_id': self.student_id,
            'profile_image': self.profile_image,
            'created_at': self.created_at,
            'fo_clud': self.fo_clud,
            'fo_activity': self.fo_activity,
            'cookie_last_update': self.cookie_last_update,
        }
        return res


class Activity(Document):
    activity_id = StringField(primary_key=True)
    title = StringField(max_length=50)
    type = EnumField(ActivityType, default=ActivityType.NA)
    #link = URLField()
    link=StringField(max_length=255)
    location = StringField(max_length=100)
    introduction = StringField(max_length=2048)
    #created_by = EmailField()
    created_by = StringField()
    cover_image_url = StringField()###
    relate_image_url = ListField()###
    timestamp = IntField()
    startdatetime = IntField()
    enddatetime = IntField()
    can_follow = BooleanField()
    state = IntField()  # 0:hide;1:publish;2:deleted;

    def info(self):
        res = {
            "id": self.activity_id,
            "title": self.title,
            "type": self.type.value,
            "link": self.link,
            "created_by": self.created_by,
            "cover_image_url": self.cover_image_url,
            "relate_image_url": self.relate_image_url,
            "timestamp": self.timestamp
        }

        return res


class Club(Document):
    club_id = StringField(primary_key=True)
    club_num = IntField()
    club_account = StringField(max_length=30)
    club_password = StringField(max_length=255)

    logo_url = StringField(max_length=255)
    name = StringField(max_length=50)
    tag = EnumField(ClubTag, default=ClubTag.NA)
    intro = StringField(max_length=2048)
    contact = ListField(DictField())

    club_photos_list = ListField(StringField(max_length=255))
    login_time = IntField()
    # contact=DictField()


class Student(Document):
    student_id = StringField(primary_key=True)
    name = StringField(max_length=100)
    nickname = StringField(max_length=100)
    Student_email = EmailField(domain_whitelist=None, allow_utf8_user=False, allow_ip_domain=False)
    #Student_email = StringField(max_length=200)
    icon_url = URLField()
    calendar_url = URLField()
    calendar_url_Expired_day = IntField()
    follow_club_list = ListField(StringField(max_length=255))
    follow_activity_list = ListField(StringField(max_length=255))
    login_time = IntField()


    def info(self):
        res = {
            "club_id": self.club_id,
            "club_num": self.club_num,
            "club_account": self.club_account,
            "logo_url": self.logo_url,
            "name": self.name,
            "tag": self.tag.value,
            "intro": self.intro,
            "contact": self.contact,
            "club_photos_list": self.club_photos_list,
        }

        return res


class Notice(Document):
    notice_id = StringField(primary_key=True)
    post_datetime = IntField()
    notice_for = StringField() #CLUB/ACTIVITY
    notice_type = EnumField(NoticeType, default=NoticeType.NA)
    title = StringField(max_length=255)
    image_url = StringField()
    link = StringField(max_length=255)
    state = IntField()# 0:hide;1:publish;2:deleted;
    created_by = StringField()
    activity_id = StringField()



