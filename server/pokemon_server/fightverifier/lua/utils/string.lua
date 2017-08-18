
-- 分割字符串
function string:split( sep , convertfunc)
    local sep, fields = sep or ':', {}
    local convert = convertfunc or tostring
    local pattern = string.format( '([^%s]+)', sep )
    self:gsub( pattern, function( c ) fields[#fields+1] = convert(c) end )
    return fields
end

function string.toArray(str)
    local ret = {}
    if string.len(str) < 1 then
        return ret
    end
    for i = 1,string.len(str) do
        table.insert(ret,string.sub(str,i,i))
    end
    return ret
end
