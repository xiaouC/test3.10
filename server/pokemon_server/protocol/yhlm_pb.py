# coding: utf-8
from pyprotobuf import ProtoEntity, Field
# file: notice.proto.proto
class NoticeResponse(ProtoEntity):
    notices         = Field('string',	1, repeated=True)

