local s = redis.call('hget', KEYS[1], ARGV[1])
local v
if s then
    v = cmsgpack.unpack(s)
end
if v==nil then
    v = {}
end
v[ARGV[2]] = ARGV[3]
return redis.call('hset', KEYS[1], ARGV[1], cmsgpack.pack(v))
