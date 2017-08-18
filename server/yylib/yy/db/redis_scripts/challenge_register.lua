-- 竞技场注册新人 keys=(key,), ARGV=(entityID,)
local result = redis.call('ZREVRANGE', KEYS[1], 0, 0, 'WITHSCORES')
redis.log(redis.LOG_NOTICE, 'zrevrange result: ' .. tostring(result[1]) .. ' ' .. tostring(result[2]))
local score = result[2] or 0
assert(redis.call('ZADD', KEYS[1], score+1, ARGV[1]) == 1, 'key already exists[2]')
return redis.call('ZRANK', KEYS[1], ARGV[1]) + 1
