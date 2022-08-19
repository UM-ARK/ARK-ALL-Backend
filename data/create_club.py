# How to use?
# enter the below command in terminal
# > python manage.py shell
# >>> exec(open('data/create_club.py').read())
# >>> main()
from pathlib import Path
from passlib.hash import pbkdf2_sha256
import os
import shutil
import random
import string
import uuid

from data.models import *
from data.enum import Faculty, Major, AccountStatus, ActivityType, ClubTag

#
all_chs = string.digits + string.ascii_letters


def gen_pass(n=8):
    result = ''
    for i in range(n):
        ch = random.choice(all_chs)
        result += ch
    return result


def create_club_all(account, name, tag, logo_path,introText, contact):
    new_club = Club()
    id = str(uuid.uuid4())
    new_club.club_id = id
    new_club.club_account = account
    o_pw = gen_pass()
    pw = pbkdf2_sha256.hash(o_pw)
    new_club.club_password = pw
    new_club.name = name
    new_club.tag = tag

    path = "data/static/images/club/" + id
    Path(path).mkdir(parents=True, exist_ok=True)
    shutil.copy2(logo_path, path + "/logo" + os.path.splitext(logo_path)[1])
    new_club.logo_url = path + "/logo" + os.path.splitext(logo_path)[1]

    new_club.intro = introText
    new_club.contact = contact
    new_club.save()
    # print()
    # print('Added club successfully.')
    # print("/------------------------------------------\\")
    # print('|ID: ', '{0: <36}'.format(id), "|")
    # print('|account: ', '{0: <31}'.format(account), "|")
    # print('|password: ', '{0: <30}'.format(pw), "|")
    # print("\------------------------------------------/")
    result = {
        'code': '1',
        'message': 'success',
        'id': id,
        'account': account,
        'password': o_pw
    }
    return result
    pass


def create_club(account, name, tag, logo_path):
    new_club = Club()
    id = str(uuid.uuid4())
    new_club.club_id = id
    new_club.club_account = account
    o_pw = gen_pass()
    pw = pbkdf2_sha256.hash(o_pw)
    new_club.club_password = pw
    new_club.name = name
    new_club.tag = tag

    path = "data/static/images/club/" + id
    Path(path).mkdir(parents=True, exist_ok=True)
    shutil.copy2(logo_path, path + "/logo" + os.path.splitext(logo_path)[1])
    new_club.logo_url = path + "/logo" + os.path.splitext(logo_path)[1]
    new_club.club_num= club_num_increment()
    new_club.save()
    result = {
        'code': '1',
        'message': 'success',
        'id': id,
        'account': account,
        'password': o_pw
    }
    return result
    pass


def main():
    print("Sign up for Club now")
    print("Please enter the corresponding information one by one when prompted")
    account = input("account:")
    print('=======================================')
    name = input("name:")
    print('=======================================')
    print("please only input: ", end="")
    for CTag in ClubTag:
        print(CTag.value, end=" / ")
    tag = input("\ntag:")
    print('=======================================')
    logo_path = input("logo path:")
    print('=======================================')
    result = create_club(account, name, tag, logo_path)

    # introText = input("introText:")
    # print('=======================================')
    # print("contact - if do not have the type of the contact just push enter button.")
    # contact = {}
    # contact['Wechat']=input("Wechat: ")
    # contact['Email'] =input("Email: ")
    # contact['Phone'] =input("Phone: ")
    # contact['IG'] =input("IG: ")
    # contact['Facebook'] =input("Facebook: ")
    # contact['Website'] = input("Website: ")
    # print('=======================================')
    # result = create_club_all(account, name, tag, logo_path, introText, contact)

    print()
    print('Added club successfully.')
    print("/------------------------------------------\\")
    print('|ID: ', '{0: <36}'.format(result["id"]), "|")
    print('|account: ', '{0: <31}'.format(result["account"]), "|")
    print('|password: ', '{0: <30}'.format(result["password"]), "|")
    print("\------------------------------------------/")