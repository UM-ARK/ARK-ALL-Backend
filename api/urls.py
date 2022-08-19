from django.urls import path
import api.views as api


urlpatterns = [
    ##jwt
    path('renewal_token/', api.renewal_token),

    ##appInfo
    path('get_appInfo/',api.get_appinfo),
    #path('create_appinfo/',api.create_appinfo),

    ##club
    path('club_signin/', api.club_signin),
    path('club_signup/', api.register_new_club),
    path('get_club_info/<str:mode>/', api.get_club_info),
    path('edit_club_info/',api.edit_club_info),

    ##activity
    path('create_activity/', api.create_activity),
    path('delete_activity/', api.delete_activity),
    path('get_activity/<str:mode>/',api.get_activity),
    path('edit_activity/',api.edit_activity),

    ##student
    #path('student_signin/', api.student_signin),
    path('get_follow_club/', api.get_follow_club),
    path('student_add_follow_club/', api.student_add_follow_club),
    path('student_del_follow_club/', api.student_del_follow_club),

    path('get_follow_activity/', api.get_follow_activity),
    path('student_add_follow_activity/', api.student_add_follow_activity),
    path('student_del_follow_activity/', api.student_del_follow_activity),

    ## notice
    path('create_notice/', api.create_notice),
    path('edit_notice/', api.edit_notice),
    path('delete_notice/', api.delete_notice),
    path('get_notice/<str:mode>/', api.get_notice),



    ### The page for test
    path('register_club_page/',api.register_club_page),
    # path('club_signin_page/',api.club_signin_page),
    # path('renewal_token_page/',api.renewal_token_page),
    # path('update_club_info_page/',api.update_club_info_page),
    # #path('upload_club_photos_page/',api.upload_club_photos_page),
    # #path('delete_club_photos_page/',api.delete_club_photos_page),
    # path('create_activity_page/',api.create_activity_page),
    # path('update_activity_info_page/',api.update_activity_info_page),
    # path('delete_activity_page/', api.delete_activity_page),
    # path('student_signin_page/', api.student_signin_page),
    # path('student_add_follow_club_page/', api.student_add_follow_club_page),
    # path('student_del_follow_club_page/', api.student_del_follow_club_page),
    # path('get_follow_club_page/', api.get_follow_club_page),
    # path('student_add_follow_activity_page/', api.student_add_follow_activity_page),
    # path('student_del_follow_activity_page/', api.student_del_follow_activity_page),
    # path('get_follow_activity_page/', api.get_follow_activity_page),
    # path('get_club_info_page/', api.get_club_info_page),
    # path('get_club_info_page2/', api.get_club_info_page2),
    # path('sent_mail_test/', api.sent_mail_test),

]