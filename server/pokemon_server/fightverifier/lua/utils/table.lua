--./utils/table.lua
-- 取最小值
function table.min(t)
    local minv
    local mini
    for i,v in pairs(t) do
        if not minv or v<minv then
            minv = v
            mini = i
        end
    end
    return mini, minv
end

function table.clear(t)
    for k in pairs(t) do
        t[k] = nil
    end
end

-- table.update(t, t1, t2...) 把 t1 t2 等的key复制到t中
function table.update (t,...)
    for i = 1,select('#',...) do
        for k,v in pairs(select(i,...)) do
            t[k] = v
        end
    end
    return t
end

-- 浅拷贝
function table.copy(tab)
    return table.update({}, tab)
end

-- 判断是否空表
function table.isEmpty(tab)
    --[[
    for _,_ in pairs(tab) do
        return false
    end
    return true
    --]]
    return next(tab) == nil
end

-- key变value，value变key
function table.k2v(tab)   --直接转换，慎用
    local ret = {}
    for k,v in pairs(tab) do
        ret[v] = k
    end
    return ret
end

-- 主动触发protobuf的magic method
function table.expand(tab)
    pcall(function()
        return tab.id
    end)
    return tab
end

function table.unproto(tab)
    tab = table.expand(tab)
    return setmetatable(tab, {})
end

function table.hasKey(proto,key)
    local tab = table.expand(proto)
    return rawget(tab,key) ~= nil
end

-- 定义全局空表
table.empty = setmetatable({}, {
    __newindex = function(...)
    end,
    __eq = function(tab1,empty)
        return type(tab1) == "table" and table.isEmpty(tab1) or false
    end
})

function toString(tab)
    if type(tab) == "string" then
        return tab
    elseif type(tab) == "number" then
        return tostring(tab)
    elseif type(tab) == "table" then
        local con = {}
        for k,v in pairs(tab) do
            local fs = "[%d]=%s"
            if type(k) ~= "number" then 
                fs = "[\"%s\"]=%s"
            end
            table.insert(con,string.format(fs,toString(k),toString(v)))
        end
        return "{"..table.concat(con,",").."}"
    else
        return tostring(tab)
    end
end

function table.orderIter(tab,cmp)
    --cmp方法比较时用 .key .value 获取table的key ,value
    --默认按key值大小排序
    local i = 0
    local ta = {}
    local cmp = cmp or function(a,b)
        return a.key < b.key
    end
    table.foreach(tab,function(k,v) return table.insert(ta,{key=k,value=v})end)
    table.sort(ta,cmp)
    return function()
        i = i + 1
        if i > #ta then return end
        return ta[i].key,ta[i].value
    end
end

function table.specialSort(tab,cmp)
    local ta = {}
    table.foreach(tab,function(k,v) 
        v.id = k
        table.insert(ta,v) 
        return 
    end)
    table.sort(ta,cmp)
    return ta
end

function table.filter(list, func)
    local selected = {}
    for _,i in ipairs(list) do
        if func(i) then
            table.insert(selected, i)
        end
    end
    return selected
end

function table.find(list, func)
    for _, item in ipairs(list) do
        if func(item) then
            return item
        end
    end
end

function table.index(list, func)
    for idx, item in ipairs(list) do
        if func(item) then
            return idx
        end
    end
end

-- pop最后一个值，table.insert的逆操作
function table.pop(tbl)
    if #tbl>0 then
        local o = tbl[#tbl]
        tbl[#tbl] = nil
        return o
    else
        return nil
    end
end

function table.len(ta)
    local len = 0
    for _,_ in pairs(ta) do
        len = len + 1
    end
    return len
end

function table.zip(t1, t2)
    local r = {}
    for idx, v1 in ipairs(t1) do
        local v2 = t2[idx]
        r[v1] = v2
    end
    return r
end

function table.hasValue(tb, value)
	for _, v in pairs(tb) do
		if v == value then
			return _, true
		end
	end
end

function table.hasKeyWord(tb, value)
	for key, v in pairs(tb) do
		if key == value then
			return v, true
		end
	end

	return false
end
