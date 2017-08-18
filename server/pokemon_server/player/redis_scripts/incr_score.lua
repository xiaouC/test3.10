local val = tonumber(ARGV[2])
local meb = ARGV[1]
local key = KEYS[1]
local s = tonumber(redis.call('ZSCORE', key, meb))
if not s then
    s = 1000
end
if val > 0 then
    val = s + val
elseif val < 0 then
    val = s + val
    if val < 0 then
        val = 0
    end
else
    return val
end
return redis.call('ZADD', key, val, meb)
