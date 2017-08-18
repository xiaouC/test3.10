-- ./win/Fight/fight_debug.lua

local __fight_debug_output = class( 'fight_debug_output' )
function __fight_debug_output:ctor( output_file_name )
    self.debug_file_name = CCFileUtils:sharedFileUtils():getWritablePath() .. output_file_name
    self.debug_msg_file = io.open( self.debug_file_name, 'w+' )
end

function __fight_debug_output:write( text )
    self.debug_msg_file:write( text )
    self.debug_msg_file:write( '\n\n' )
    self.debug_msg_file:flush()
end

local fight_output = nil
local verify_fight_output = nil

function write_fight_output( text )
    if not fight_output then fight_output = __fight_debug_output.new( 'fight_output' ) end
    fight_output:write( text )
end

function write_verify_fight_output( text )
    if not verify_fight_output then verify_fight_output = __fight_debug_output.new( 'verify_fight_output' ) end
    verify_fight_output:write( text )
end

