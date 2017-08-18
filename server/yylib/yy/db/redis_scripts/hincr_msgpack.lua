local key = KEYS[1]
local field = ARGV[1]
local name = ARGV[2]
local s = redis.call('hget', key, field)
local v
if s then
    v = cmsgpack.unpack(s)
end
if v==nil then
    v = {}
end
v[name] = (v[name] or 0) + ARGV[3]
return redis.call('hset', key, field, cmsgpack.pack(v))
