-- (k1 k2 rank_key) (field e1 e2)
local k1 = KEYS[1]
local k2 = KEYS[2]
local rank_key = KEYS[3]
local field = ARGV[1]
local e1 = ARGV[2]
local e2 = ARGV[3]

local v1 = redis.call('HGET', k1, field)
local v2 = redis.call('HGET', k2, field)
redis.call('HSET', k1, field, v2)
redis.call('HSET', k2, field, v1)
redis.call('ZADD', rank_key, v2, e1)
redis.call('ZADD', rank_key, v1, e2)
return {v2, v1}
