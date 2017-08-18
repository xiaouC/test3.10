-- ./utils/class.lua

-------------------------------------------------------------------------------------------------------------------------------------
-- clone
function clone( object )
    local lookup_table = {}

    local function _copy( object )
        if type( object ) ~= 'table' then
            return object
        elseif lookup_table[object] then
            return lookup_table[object]
        end

        local new_table = {}
        lookup_table[object] = new_table
        for key,value in pairs( object ) do
            new_table[_copy(key)] = _copy( value )
        end

        return setmetatable( new_table, getmetatable( object ) )
    end

    return _copy( object )
end

-- class
--[[--
** usage **
    local Shape = class( 'Shape' )

    -- base class
    function Shape:ctor( shapeName )
        self.shapeName = shapeName
        CCLuaLog( string.format( 'Shape:ctor(%s)', self.shapeName ) )
    end

    function Shape:draw()
        CCLuaLog( 'draw ' .. self.shapeName )
    end

    --
    local Circle = class( 'Circle', Shape )
    function Circle:ctor()
        Circle.super.ctor( self, 'circle' )         -- call super-class method
        self.radius = 100
    end

    function Circle:setRadius( radius )
        self.radius = radius
    end

    function Circle:draw()
        CCLuaLog( string.format( 'draw %s, radius = %0.2f', self.shapeName, self.radius ) )
    end

    --
    local Rectangle = class( 'Rectangle', Shape )

    function Rectangle:ctor()
        Rectangle.super.ctor( self, 'rectangle' )
    end

    local circle = Circle.new()             -- output: Shape:ctor(circle)
    circle:setRadius( 200 )
    circle:draw()                           -- output: draw circle, radius = 200.00

    local rectangle = Rectangle.new()       -- output: Shape:ctor(rectangle)
    rectangle:draw()                        -- output: draw rectangle

@param string classname
@param table/function super-class
@return table
]]

function class( classname, super )
    local superType = type( super )
    local cls

    if superType == 'function' or ( super and super.__ctype == 1 ) then
        cls = {}            -- inherited from native c++ object

        if superType == 'table' then
            -- copy fields from super
            for k,v in pairs( super ) do cls[k] = v end
            cls.__create = super.__create
            cls.super = super
        else
            cls.__create = super
            cls.ctor = function() end
        end

        cls.__cname = classname
        cls.__ctype = 1

        function cls.new( ... )
            local instance = cls.__create( ... )
            -- copy fields from class to native object
            for k,v in pairs( cls ) do instance[k] = v end
            instance.class = cls
            instance:ctor( ... )
            return instance
        end
    else
        -- inherited from lua object
        if super then
            cls = clone( super )
            cls.super = super
        else
            cls = { ctor = function() end }
        end

        cls.__cname = classname
        cls.__ctype = 2 -- lua
        cls.__index = cls

        function cls.new( ... )
            local instance = setmetatable( {}, cls )
            instance.class = cls
            instance:ctor( ... )
            return instance
        end
    end

    return cls
end


