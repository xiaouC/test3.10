# coding:utf-8
import settings
from UserString import UserString
from string import Template


class IndexString(UserString):
    SERVER_INFO = {
        "sessionID": settings.SESSION["ID"],
    }

    def render(self, **info):
        if not info:
            info = self.SERVER_INFO
        return Template(self.data).substitute(**info)


# 前缀RANK对应ordered set，INDEX对应hash map，SET对应set，INT为string，LIST为LIST

# player
INDEX_NAME = IndexString('index_p_name{$regionID}')
