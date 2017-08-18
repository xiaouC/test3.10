# coding: utf-8
from manager import Query, async_execute, execute

class Proc(object):
    def __init__(self, name, argnames, dbtag='game'):
        self.name = name
        self.argnames = argnames
        self.dbtag = dbtag

    def get_query(self, *args, **kwargs):
        clean_args = []
        self.dbtag = kwargs.pop('dbtag', 'user')
        for i, a in enumerate(self.argnames):
            if i<len(args):
                clean_args.append(args[i])
            else:
                clean_args.append(kwargs.get(a))
        return Query(self.name, clean_args, True, self.dbtag, self.argnames)

    def execute(self, *args, **kwargs):
        print args, kwargs
        return execute(self.get_query(*args, **kwargs))

    def async_execute(self, *args, **kwargs):
        cb = kwargs.pop('callback', None)
        return async_execute(self.get_query(*args, **kwargs), cb)

#         存储过程名字也是函数名字          参数名列表    所在数据库[user, game]
procs = [
      Proc("sp_CreateUser",["username","password","sIMSI","sTID","password_changed"],"user")
    , Proc("sp_CreatePlayer",["Usename","Sex","UserId","School","ModelID"],"game")
    , Proc("sp_DeletePlayer",["rId"],"game")
    , Proc("sp_UpdateCheckName",["_RootNode","_Leaf"],"game")
    , Proc("sp_LoadPlayerBase",["userID"],"game")
    #----------------------------------------------------------------------
    , Proc('sp_LoadAll',                ['roleID'], 'game')
    , Proc('sp_LoadPlayer',             ['roleID'], 'game')
    , Proc('sp_LoadAttribute',          ['roleID'], 'game')
    , Proc('sp_LoadPackage',            ['roleID'], 'game')
    , Proc('sp_LoadEquip',              ['roleID'], 'game')
    , Proc('sp_LoadExpendable',         ['roleID'], 'game')
    , Proc('sp_LoadMaterial',           ['roleID'], 'game')
    , Proc('sp_LoadEquipsOnRole',       ['roleID','playerId'], 'game')
    , Proc('sp_LoadPet',                ["roleID"], "game")
    #----------------------------------------------------------------------
    , Proc('sp_LoadRoleLimitConst',     ['roleID'], 'game')
    , Proc('sp_UpdateRoleLimitConst',   ['_constValue','_type','pId','_time','_cytime'], 'game')
    #----------------------------------------------------------------------
    , Proc('sp_UpdateServerStatus',     ['worldID', 'OnlineCount'], 'user')
    , Proc('sp_loadBase',               ['tempInt'],'game')
    , Proc('sp_updateGameBase',         ['name', 'nvalue', 'cvalue', 'fvalue'],'game')
    , Proc('sp_ChangePackIndex',        ['roleID', 'srcIndex', 'dstIndex'],'game')
    , Proc('sp_UpdatePlayer',           ['name', 'nvalue', 'cvalue', 'fvalue', 'roleId'],'game')
    , Proc('sp_UpdatePack',             ['packIndex','gridIndex','itemID','type','count','locked','roleId'],'game')
    , Proc('sp_DeletePackAllGrids',     ['packIndex','roleId'],'game')
    , Proc('sp_UpdateLineup',           ["_id", "_roleid", "_lineupinfo", "_isprimary"], 'game')
    , Proc('sp_LoadLineups',            ["_roleid"], 'game')
    , Proc('sp_CreateLineup',           ["_roleid", "_lineupinfo", "_isprimary"], 'game')
    , Proc('sp_RemoveLineup',           ["_id"], 'game')
    , Proc('sp_UpdateEquip',            ['equipId','_position','_type','rId'],'game')  #
    , Proc('sp_UpdateEquipsOnRole',     ['equipId','_placetype','rId','pId'],'game')  #
    , Proc('sp_UpdateFlySword',         [])  #
    , Proc('sp_UpdateSkills',           [])  #
    , Proc('sp_UpdateAttribute',        [])  #
    , Proc('sp_UpdateEquipAttri',       ['eId','name','nvalue','cvalue','fvalue'],'game')  #
    , Proc('sp_UpdateMaterialAttri',    ['name','nvalue','cvalue','fvalue','mID'],'game')  #
    , Proc('sp_UpdateExpendableAttri',  ['_eId','name','nvalue','cvalue','fvalue'],'game') #
    , Proc('sp_CreateEquipMent',        ['_prototypeId','_worldId'],'game')  #
    , Proc('sp_CreateFlySword',         [])  #
    , Proc('sp_CreateMaterial',         ['_prototypeId','_type','_durable','_worldId'],'game')  #
    , Proc('sp_CreateExpendable',       ['_useTimes','_prototypeId','_worldId'],'game')  #
    , Proc('sp_AddPack',                ['_packIndex','_prototypeId','_rId'],'game')  #
    , Proc('sp_AddRoleSkill',           [])  #
    , Proc('sp_AddPetSkill',            [])  #
    #----------------------------------------------------------------------
    , Proc('sp_LoadTask',               ["_TaskId"],"game")  #
    , Proc('sp_LoadTask_his',           ["_TaskId"],"game")  #
    , Proc('sp_AddTask',                ["_RoleId","_TaskId","_TName","_status","_oriContent"],"game")  #
    , Proc('sp_AddTaskHis',             ["_RoleId","_TaskId"],"game")  #
    , Proc('sp_UpdateTask',             ["_roleId","_taskID","_taskStatus","_oriContent"],"game")  #
    #----------------------------------------------------------------------
    , Proc('sp_LoadGuide',              ['_roleId'],'game')  #
    , Proc('sp_AddGuide',               ['_roleId','_guideId'],'game')  #
    #----------------------------------------------------------------------
    , Proc('sp_LoadHome',               ['_roleId'],'game')    #读取家园数据
    #----------------------------------------------------------------------
    , Proc('sp_RemovePack',             ['_packId','_rId'],'game')  #
    , Proc('sp_RemoveRoleSkill',        [])  #
    , Proc('sp_RemovePetSkill',         [])  #
    , Proc('sp_UpdatePetSkill',         [])  #
    , Proc('sp_CreateAddiAttri',        [])  #
    , Proc('sp_UpdateAttrAddi',         [])  #
    , Proc('sp_UpdateAddiAttri',        [])  #
    , Proc('sp_UpdateStorage',          [])  #
    , Proc('sp_UpdatePetAttri',         [])  #
    , Proc('sp_AddPet',                 ["PetID", "RoleID"], "game")  #
    , Proc('sp_UpdatePet',              [])  #
    , Proc('sp_DeletePet',              [])  #
    , Proc('sp_RemovePet',              [])  #
    , Proc('sp_ChangePackPosition',     ['_s_packIndex','_d_packIndex','_rId'],'game')  #
    , Proc('sp_CreatePet',              [])  #
    , Proc('sp_UpdateUser',             [], 'user')  #
    , Proc('sp_AddCopyCount',           [])  #
    , Proc('sp_AddGroup',               [])  #
    , Proc('sp_RemoveGroup',            [])  #
    , Proc('sp_AddGroupMember',         [])  #
    , Proc('sp_RemoveGroupMember',      [])  #
    , Proc('sp_UpdateGroupMember',      [])  #
    , Proc('sp_ChangeGroupName',        [])  #
    , Proc('sp_AddRequestList',         [])  #
    , Proc('sp_RemoveRequest',          [])  #
    , Proc('sp_UpdateRequestOwner',     [])  #
    , Proc('sp_UpdateLineStatus',       [])  #
    , Proc('sp_RemoveRoleBuff',         [])  #
    , Proc('sp_RemovePetBuff',          [])  #
    , Proc('sp_SaveRoleBuff',           [])  #
    , Proc('sp_SavePetBuff',            [])  #
    , Proc('sp_UpdateMaterial',         [])  #
    , Proc('sp_updateAutoSetScheme',    [])  #
    , Proc('sp_updateRoleGuide',        [])  #
    , Proc('sp_UpdateRoleGold',         [])  #
    , Proc('sp_UpdateUserLotteryTimes', [])  #
    , Proc('sp_UpdateCAInfo',           [])  #
    , Proc('sp_UpdateCATally',          [])  #
    , Proc('sp_UpdateFlySwordProperty', [])  #
    , Proc('sp_UpdateArena',            [])  #
    , Proc('gm_dropline',               [])  #
    , Proc('gm_buy',                    [])  #
    , Proc('gm_ingame',                 [])  #
    , Proc('gm_task',                   [])  #
    , Proc('gm_leavegame',              [])  #
    , Proc('gm_mallinfo',               [])  #
    , Proc('gm_use',                    [])  #
    , Proc('gm_level',                  [])  #
    , Proc('gm_epLog',                  [])  #
    , Proc('sp_UpdateCharts',           [])  #
    , Proc('sp_UpdateAttunement',       [])  #
    , Proc('sp_AddMaterialMake',        [])  #
    , Proc('sp_LoadMaterialMake',       [])  #
    , Proc('sp_UpdateMaterialMake',     [])  #
    , Proc('sp_CreatePetEquip',         [])  #
    , Proc('sp_UpdatePetEquipPack',     [])  #
    , Proc('sp_LoadPetEquipPack',       [])  #
    , Proc('sp_UpdatePetEquipAttr',     [])  #
    , Proc('sp_soul_rank',              [])  #
    , Proc('sp_update_soul_rank',       [])  #
    , Proc('sp_CreateMail',             [])  #
    , Proc('sp_deleteRoleMail',         [])  #
    , Proc('sp_UpdateMailProperty',     [])  #
    , Proc('sp_AddPlayerFlySword',      [])  #
    , Proc('sp_InitExpendaleUsetimesLimit',      [])  #
    , Proc('sp_UpdateExpendableUsedTimesLimit',  [])  #
    #-----------------------------------------------------------------
    , Proc('gm_StatisticsTask',      [],'game')  #任务GM接口
    ## 获取温泉中玩家
    ,Proc("sp_GethotspringOL",["baselevel","sublevel","rowcount","datetime", "selfid"],"game")
    ## 获取其他凑数玩家
    ,Proc("sp_Gethotspringrands",["baselevel","sublevel","rowcount","datetime", "selfid"],"game")
    ## 重置鲁王争霸所有对手
    ,Proc("sp_getChallengeRivalResultAll",["userID", "exculdeId"],"game")
    ## 重置鲁王争霸单个对手
    ,Proc("sp_getChallengeRivalResultSingle",["userID","vStyle","vCount","exculdeId"],"game")
    ,Proc('sp_ChallengeRanking',      [], "game")  #

    ,Proc('swap_ranks', ['u1', 'u2', 'rank_field_id', 'trend_field_id'], 'game')
    ]

# 创建全局函数
for p in procs:
    globals()[p.name] = p

def onPlayerPropertyUpdate(role, name, value):
    if name=="tile":
        x, y = value
        sp_UpdatePlayer.async_execute(name='scenePosX', nvalue=x, roleId=role.roleID)
        sp_UpdatePlayer.async_execute(name='scenePosY', nvalue=y, roleId=role.roleID)
    else:
        args = { 'name': name, 'roleId': role.roleID }
        if name=="name" or name=="title" or name=="spouseName" or name=="shortcutKeys":
            if isinstance(value, (str, unicode)):
                args["cvalue"] = value
            else:
                args['cvalue'] = pickle.dumps(value)
        else:
            if isinstance(value, (int, float, str, unicode)):
                args['nvalue'] = value
            else:
                args['nvalue'] = pickle.dumps(value)
        sp_UpdatePlayer.async_execute(**args)

if __name__ == '__main__':
    import doctest
    doctest.testmod()

    from manager import start_dbmanager, execute
    start_dbmanager()
    ds = sp_LoginAccount.execute('111111', '111111', 5)
    uid = ds.rows[0][1]
    (ds_roles, ds_players) = sp_LoadServerPlayerCount.execute(uid)
