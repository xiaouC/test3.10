local s = redis.hget(KEYS[1], ARGS[1])
local v
if s~=nil then
    v = msgpack.unpack(s)
end
if v==nil then
    v = {}
end
table.insert(v, ARGS[2])
redis.hset(KEYS[1], msgpack.pack(v))
