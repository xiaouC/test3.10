-- ./utils/shaders.lua

local vertex_shader_1 = [[
attribute vec4 a_position;
attribute vec4 a_color;
attribute vec2 a_texCoord;

#ifdef GL_ES
    varying lowp vec4 v_fragmentColor;
    varying mediump vec2 v_texCoord;
#else
    varying vec4 v_fragmentColor;
    varying vec2 v_texCoord;
#endif

void main() {
    gl_Position = CC_MVPMatrix * a_position;
    v_fragmentColor = a_color;
    v_texCoord = a_texCoord;
}
]]

local vertex_shader_2 = [[
attribute vec4 a_position;
attribute vec4 a_color;
attribute vec2 a_texCoord;
attribute vec2 a_texCoord1;

#ifdef GL_ES
    varying lowp vec4 v_fragmentColor;
    varying mediump vec2 v_texCoord;
    varying mediump vec2 v_texCoord_1;
#else
    varying vec4 v_fragmentColor;
    varying vec2 v_texCoord;
    varying vec2 v_texCoord_1;
#endif

void main() {
    gl_Position = CC_MVPMatrix * a_position;
    v_fragmentColor = a_color;
    v_texCoord = a_texCoord;
    v_texCoord_1 = a_texCoord1;
}
]]

local rgb_to_hsv = [[
vec3 rgb_to_hsv(float r, float g, float b) {
    float c_max = max(r, max(g, b));
    float c_min = min(r, min(g, b));

    float delta = c_max - c_min;
    if (delta == 0.0) {
        return vec3(0.0, 0.0, c_max);
    }

    vec3 hsv;
    hsv.z = c_max;
    hsv.y = (c_max - c_min) / c_max;

    if (r == c_max) {
        hsv.x = (g - b) / delta;
    } else {
        if (g == c_max) {
            hsv.x = 2.0 + (b - r) / delta;
        } else {
            hsv.x = 4.0 + (r - g) / delta;
        }
    }

    hsv.x = hsv.x * 60.0;
    if (hsv.x  < 0.0) {
        hsv.x = hsv.x + 360.0;
    }

    return hsv;
}
]]

local hsv_to_rgb = [[
vec3 hsv_to_rgb(float h, float s, float v) {
    float c = v * s;
    float x = c * (1.0 - abs(mod(h/60.0, 2.0) - 1.0));
    float m = v - c;

    if (h >= 0.0 && h < 60.0) {
        return vec3(c + m, x + m, m);
    }

    if (h >= 60.0 && h < 120.0) {
        return vec3(x + m, c + m, m);
    }

    if (h >= 120.0 && h < 180.0) {
        return vec3(m, c + m, x + m);
    }

    if (h >= 180.0 && h < 240.0) {
        return vec3(m, x + m, c + m);
    }

    if (h >= 240.0 && h < 300.0) {
        return vec3(x + m, m, c + m);
    }

    return vec3(c + m, m, x + m);
}
]]

local custom_shaders = {
    ['color_texture_label'] = {
        vertex_shader = vertex_shader_2,
        frag_shader = [[
            #ifdef GL_ES
            precision lowp float;
            #endif

            varying vec4 v_fragmentColor;
            varying vec2 v_texCoord;
            varying vec2 v_texCoord_1;

            uniform vec4 u_textColor;

            void main() {
                // RGB from uniform, A from texture & uniform
                vec4 color_0 = v_fragmentColor * vec4(u_textColor.rgb, u_textColor.a * texture2D(CC_Texture0, v_texCoord).a);

                // color texture
                vec4 color_1 = texture2D(CC_Texture1, v_texCoord_1);

                gl_FragColor = color_0 * vec4( color_1.r, color_1.g, color_1.b, 1.0 );
            }
        ]],
    },
    ['color_texture_system_font_label'] = {
        vertex_shader = [[
            attribute vec4 a_position;
            attribute vec4 a_color;
            attribute vec2 a_texCoord;
            attribute vec2 a_texCoord1;
            
            #ifdef GL_ES
                varying lowp vec4 v_fragmentColor;
                varying mediump vec2 v_texCoord;
                varying mediump vec2 v_texCoord_1;
            #else
                varying vec4 v_fragmentColor;
                varying vec2 v_texCoord;
                varying vec2 v_texCoord_1;
            #endif
            
            void main() {
                gl_Position = CC_PMatrix * a_position;
                v_fragmentColor = a_color;
                v_texCoord = a_texCoord;
                v_texCoord_1 = a_texCoord1;
            }
        ]],
        frag_shader = [[
            #ifdef GL_ES
            precision lowp float;
            #endif

            varying vec4 v_fragmentColor;
            varying vec2 v_texCoord;
            varying vec2 v_texCoord_1;

            uniform vec4 u_textColor;

            void main() {
                vec4 color_0 =  v_fragmentColor * texture2D(CC_Texture0, v_texCoord);
                vec4 color_1 = texture2D(CC_Texture1, v_texCoord_1);

                if (color_0.a > 0.0 && color_0.a < 1.0) {
                    //color_0.rgb = v_fragmentColor.rgb;
                    color_0.r = 1.0;
                    color_0.g = 1.0;
                    color_0.b = 1.0;
                }

                gl_FragColor = color_0 * vec4( color_1.r, color_1.g, color_1.b, 1.0 );
            }
        ]],
    },
    ['color_texture_sprite'] = {
        vertex_shader = [[
        attribute vec4 a_position;
        attribute vec2 a_texCoord;
        attribute vec2 a_texCoord1;
        attribute vec4 a_color;

        #ifdef GL_ES
            varying lowp vec4 v_fragmentColor;
            varying mediump vec2 v_texCoord;
            varying mediump vec2 v_texCoord_1;
        #else
            varying vec4 v_fragmentColor;
            varying vec2 v_texCoord;
            varying vec2 v_texCoord_1;
        #endif

        void main() {
            gl_Position = CC_PMatrix * a_position;
            v_fragmentColor = a_color;
            v_texCoord = a_texCoord;
            v_texCoord_1 = a_texCoord1;
        }
        ]],
        frag_shader = [[
            #ifdef GL_ES
            precision lowp float;
            #endif

            varying vec4 v_fragmentColor;
            varying vec2 v_texCoord;
            varying vec2 v_texCoord_1;

            void main() {
                vec4 color_0 = v_fragmentColor * texture2D(CC_Texture0, v_texCoord);
                vec4 color_1 = texture2D(CC_Texture1, v_texCoord_1);

                gl_FragColor = color_0 * vec4(color_1.r, color_1.g, color_1.b, 1.0);

                // float a = 0.5;
                // gl_FragColor.rgb = color_0.rgb * (1 - a) + color_1.rgb * a;
                // gl_FragColor.a = color_0.a;

                // 颜色叠加
                float f = 0.3 * color_0.r + 0.6 * color_0.g + 0.1 * color_0.b;

                if (f <= 0.5) {
                    gl_FragColor.rgb = 2.0 * f * color_1.rgb;
                }
                else {
                    gl_FragColor.rgb = 1.0 - 2.0 * ( 1.0 - f ) * ( 1.0 - color_1.rgb );
                }

                gl_FragColor.rgb = gl_FragColor.rgb * color_0.a;
                gl_FragColor.a = color_0.a;
            }
        ]],
    },
    ['tablecloth'] = {
        vertex_shader = [[
            attribute vec4 a_position;
            attribute vec2 a_texCoord;
            attribute vec4 a_color;

            #ifdef GL_ES
                varying lowp vec4 v_fragmentColor;
                varying mediump vec2 v_texCoord;
            #else
                varying vec4 v_fragmentColor;
                varying vec2 v_texCoord;
            #endif

            void main() {
                gl_Position = CC_PMatrix * a_position;
                v_fragmentColor = a_color;
                v_texCoord = a_texCoord;
            }
        ]],
        frag_shader = [[
            #ifdef GL_ES
                precision lowp float;
            #endif

            varying vec4 v_fragmentColor;
            varying vec2 v_texCoord;

            uniform vec4 u_custom;  // x: h 色相，y: s 饱和度，z: b 明度，w: 对比度
            ]]
                .. rgb_to_hsv .. hsv_to_rgb ..
            [[
            void main() {
                vec4 color = v_fragmentColor * texture2D(CC_Texture0, v_texCoord);

                // 色相
                if (u_custom.x != 0.0) {
                    vec3 hsv = rgb_to_hsv(color.r, color.g, color.b);

                    hsv.x += u_custom.x;
                    hsv.x = mod(hsv.x, 360.0);

                    color.rgb = hsv_to_rgb(hsv.x, hsv.y, hsv.z);
                }

                // 饱和度
                if (u_custom.y != 0.0) {
                    float c_max = max(color.r, max(color.g, color.b));
                    float c_min = min(color.r, min(color.g, color.b));
                    float delta = c_max - c_min;
                    if (delta != 0.0) {
                        float v = c_max + c_min;
                        float l = v * 0.5;
                        float s = l < 0.5 ? (delta / v) : ((delta) / (2.0 - v));

                        if (u_custom.y >= 0.0) {
                            float alpha = (u_custom.y + s) >= 1.0 ? s : (1.0 - u_custom.y);
                            alpha = 1.0 / alpha - 1.0;

                            color.rgb = color.rgb + (color.rgb - l) * alpha;
                        } else {
                            float alpha = u_custom.y;
                            color.rgb = l + (color.rgb - l) * (1.0 + alpha);
                        }
                    }
                }

                // 明度
                if (u_custom.z != 0.0) {
                    color.rgb = u_custom.z > 0.0 ? (color.rgb * (1.0 - u_custom.z) + u_custom.z): (color.rgb + color.rgb * u_custom.z);
                }

                // 对比度
                // color.rgb = ((color.rgb - 0.5) * max(u_custom.w + 1.0, 0.0)) + 0.5;

                gl_FragColor = vec4(color.rgb, color.a);
            }
        ]],
    },
}

-- 在初始化的时候调用
function initCustomShaders()
    cc.TextureCache:initColorTexture(8, 8, 'common/color.png')

    for k, v in pairs(custom_shaders) do
        local p = cc.GLProgram:createWithByteArrays(v.vertex_shader, v.frag_shader)
        cc.GLProgramCache:getInstance():addGLProgram(p, k)
    end
end

-- 从后台回到前台的时候调用
function enterForegroundReloadShaders()
    cc.TextureCache:initColorTexture(8, 8, 'common/color.png')

    for k, v in pairs(custom_shaders) do
        local p = cc.GLProgramCache:getInstance():getGLProgram(k)
        if p then
            p:reset()
            p:initWithByteArrays(v.vertex_shader, v.frag_shader)
            p:link();
            p:updateUniforms();
        end
    end
end

-- 在更新完成后调用
function updateReloadShaders()
    cc.TextureCache:initColorTexture(8, 8, 'common/color.png')

    for k, v in pairs(custom_shaders) do
        local p = cc.GLProgramCache:getInstance():getGLProgram(k)
        if not p then
            p = cc.GLProgram:createWithByteArrays(v.vertex_shader, v.frag_shader)
            cc.GLProgramCache:getInstance():addGLProgram(p, k)
        else
            p:reset()
            p:initWithByteArrays(v.vertex_shader,v.frag_shader)
            p:link();
            p:updateUniforms();
        end
    end
end
