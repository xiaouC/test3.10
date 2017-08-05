-- ./utils/conditional_expression.lua
require 'utils.signal'

local ce_signal_prefix = '__ce__'

-- 
local conditional_expression_obj = nil
function __ce_get_attr_value__(attr_name)
    if conditional_expression_obj then
        return conditional_expression_obj.attr_list[attr_name] or 0
    end

    return 0
end

-- 
local function __get_value__(text)
    local new_text = string.gsub(text, '{(%a+)}', '__ce_get_attr_value__("%1")')
    local fn = loadstring('return (' .. new_text .. ')')
    return (fn ~= nil) and fn() or 0
end

local function __check_value__(operator, src_value, dest_value)
    local all_operators = {
        ['>'] = function() return src_value > dest_value end,
        ['<'] = function() return src_value < dest_value end,
        ['=='] = function() return src_value == dest_value end,
        ['>='] = function() return src_value >= dest_value end,
        ['<='] = function() return src_value <= dest_value end,
        ['~='] = function() return src_value ~= dest_value end,
    }

    return all_operators[operator]()
end

----------------------------------------------------------------------------------------------------
local expression = {
    relation = 'and',   -- 'and' / 'or'     -- 多个子表达式间的逻辑关系
    result_list = {
        {
            attr_name = 'w',
            value = '{z} + 5',
        },
    },
    content_list = {        -- 子表达式列表
        {
            operator = '~=',    -- 左值与右值之间的比较操作符: [ '>', '<', '==', '>=', '<=', '~=' ]
            src_value = '{x} + 1',
            dest_value == '{y} * 2 + 1',
        },
    },
}

----------------------------------------------------------------------------------------------------
local conditional_expression = class('conditional_expression')
function conditional_expression:ctor()
    conditional_expression_obj = self

    self.attr_list = {}

    self.all_unlisten_attrs_func = {}
end

function conditional_expression:unlisten_all()
    for attr_name, v in pairs(self.all_unlisten_attrs_func) do
        for _, func in ipairs(v) do
            signal.unlisten(ce_signal_prefix .. attr_name, func)
        end
    end
    self.all_unlisten_attrs_func = {}
end

function conditional_expression:listenExpression(expression)
    -- 获取影响表达式的所有的属性，分别监听
    local all_expression_attrs = {}
    local function __add_attr_name__(attr_name, index)
        if not all_expression_attrs[attr_name] then
            all_expression_attrs[attr_name] = {}
        end

        if not table.hasValue(all_expression_attrs[attr_name], index) then
            table.insert(all_expression_attrs[attr_name], index)
        end
    end

    for index, v in ipairs(expression.content_list or {}) do
        for attr_name in string.gmatch(v.src_value, '{(%a+)}') do
            __add_attr_name__(attr_name, index)
        end
        for attr_name in string.gmatch(v.dest_value, '{(%a+)}') do
            __add_attr_name__(attr_name, index)
        end
    end

    -- 对应每个 content_list 的结果
    local expression_results = {}
    local function __get_expression_result__()
        if expression.relation == 'or' then
            for _, result in ipairs(expression_results) do
                if result then return true end
            end
            return false
        else
            for _, result in ipairs(expression_results) do
                if not result then return false end
            end
            return true
        end
    end

    local function __expression_callback__(index, result)
        expression_results[index] = result

        if __get_expression_result__() then
            local new_attr_values = {}
            for _, v in ipairs(expression.result_list or {}) do
                new_attr_values[v.attr_name] = __get_value__(v.value)
            end
            self:updateAttributeList(new_attr_values)
        end
    end

    -- 初始化 expression_results
    for index, v in ipairs(expression.content_list) do
        local src_value = __get_value__(v.src_value)
        local dest_value = __get_value__(v.dest_value)

        local result = __check_value__(v.operator, src_value, dest_value)
        expression_results[index] = result
    end

    -- 监听
    for attr_name, content_index_list in pairs(all_expression_attrs) do
        local unlisten_func = signal.listen(ce_signal_prefix .. attr_name, function()
            for _, index in ipairs(content_index_list) do
                local v = expression.content_list[index]

                local src_value = __get_value__(v.src_value)
                local dest_value = __get_value__(v.dest_value)

                local result = __check_value__(v.operator, src_value, dest_value)
                __expression_callback__(index, result)
            end
        end)

        -- 记下，用于取消监听
        if not self.all_unlisten_attrs_func[attr_name] then
            self.all_unlisten_attrs_func[attr_name] = {}
        end
        table.insert(self.all_unlisten_attrs_func[attr_name], unlisten_func)
    end
end

function conditional_expression:listenAttribute(attr_name, callback, priority)
    local unlisten_func = signal.listen(ce_signal_prefix .. attr_name, callback, priority)

    -- 记下，用于取消监听
    if not self.all_unlisten_attrs_func[attr_name] then
        self.all_unlisten_attrs_func[attr_name] = {}
    end
    table.insert(self.all_unlisten_attrs_func[attr_name], unlisten_func)
end

function conditional_expression:updateAttributeList(attr_list)
    local fire_attrs = {}

    for attr_name, value in pairs(attr_list or {}) do
        if self.attr_list[attr_name] ~= value then
            self.attr_list[attr_name] = value
            table.insert(fire_attrs, attr_name)
        end
    end

    for _, attr_name in ipairs(fire_attrs) do
        signal.fire(ce_signal_prefix .. attr_name, attr_list[attr_name])
    end
end

function conditional_expression:updateAttribute(attr_name, value)
    if self.attr_list[attr_name] ~= value then
        self.attr_list[attr_name] = value
        signal.fire(ce_signal_prefix .. attr_name, value)
    end
end

-- 
return conditional_expression
