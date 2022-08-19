from enum import Enum


class AccountStatus(Enum):
    NA = -1
    SIGNUP = 0
    CHANGE_PW = 1


# Todo
class Faculty(Enum):
    NA = 'N/A'
    FAH = 'FAH'
    FLL = 'FLL'
    FST='FST'


# Todo
class Major(Enum):
    NA = 'N/A'
    CIS = 'Computer Science'


class ActivityType(Enum):
    NA = 'N/A'
    ACTIVITY = 'ACTIVITY'
    OFFICIAL = 'OFFICIAL'
    WEBSITE = 'WEBSITE'


class ClubTag(Enum):
    NA = 'N/A'
    SA = 'SA'
    CLUB = 'CLUB'
    SOCIETY = 'SOCIETY'
    COLLEGE = 'COLLEGE'
    OFFICIAL = 'OFFICIAL'
    MEDIA = 'MEDIA'
    BUSINESS = 'BUSINESS'

class NoticeType(Enum):
    NA = 'N/A'
    TEXT = 'TEXT'
    WEBSITE = 'WEBSITE'
    IMAGE = 'IMAGE'
