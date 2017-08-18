if not redis.call('HEXISTS', KEYS[1], ARGV[1]) then
    redis.call('HSET', KEYS[1], ARGV[1], ARGV[3])
end
local result = redis.call('HINCRBY', KEYS[1], ARGV[1], -ARGV[2])
redis.log(redis.LOG_WARNING, 'incrby result ' .. tostring(result))
if result < 0 then
    -- recover
    redis.call('HINCRBY', KEYS[1], ARGV[1], ARGV[2])
    return 0
else
    return 1
end
