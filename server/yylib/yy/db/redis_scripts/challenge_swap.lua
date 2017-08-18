--竞技场交换排名
local s1 = redis.call('ZSCORE', KEYS[1], ARGV[1])
local s2 = redis.call('ZSCORE', KEYS[1], ARGV[2])
redis.call('ZADD', KEYS[1], s2, ARGV[1])
redis.call('ZADD', KEYS[1], s1, ARGV[2])
local r1 = redis.call('ZRANK', KEYS[1], ARGV[1]) + 1
local r2 = redis.call('ZRANK', KEYS[1], ARGV[2]) + 1
return {r1, r2}
