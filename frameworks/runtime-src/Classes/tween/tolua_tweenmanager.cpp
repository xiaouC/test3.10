/*
** Lua binding: TweenManager
** Generated automatically by tolua++-1.0.92 on 05/03/17 14:53:26.
*/

//extern "C" {
#include "tolua_fix.h"
//}

#include <map>
#include <string>
#include "cocos2d.h"
#include "CCLuaEngine.h"
//#include "SimpleAudioEngine.h"
//#include "cocos-ext.h"

using namespace cocos2d;
//using namespace cocos2d::extension;
//using namespace CocosDenshion;


/* Exported function */
TOLUA_API int  tolua_TweenManager_open (lua_State* tolua_S);

#include "TweenManager.h"

/* function to register type */
static void tolua_reg_types (lua_State* tolua_S)
{
 tolua_usertype(tolua_S,"TweenManager");
 
}

/* method: sharedTweenManager of class  TweenManager */
#ifndef TOLUA_DISABLE_tolua_TweenManager_TweenManager_sharedTweenManager00
static int tolua_TweenManager_TweenManager_sharedTweenManager00(lua_State* tolua_S)
{
#ifndef TOLUA_RELEASE
 tolua_Error tolua_err;
 if (
     !tolua_isusertable(tolua_S,1,"TweenManager",0,&tolua_err) ||
     !tolua_isnoobj(tolua_S,2,&tolua_err)
 )
  goto tolua_lerror;
 else
#endif
 {
  {
   TweenManager* tolua_ret = (TweenManager*)  TweenManager::sharedTweenManager();
    tolua_pushusertype(tolua_S,(void*)tolua_ret,"TweenManager");
  }
 }
 return 1;
#ifndef TOLUA_RELEASE
 tolua_lerror:
 tolua_error(tolua_S,"#ferror in function 'sharedTweenManager'.",&tolua_err);
 return 0;
#endif
}
#endif //#ifndef TOLUA_DISABLE

/* method: tweenFromTo of class  TweenManager */
#ifndef TOLUA_DISABLE_tolua_TweenManager_TweenManager_tweenFromTo00
static int tolua_TweenManager_TweenManager_tweenFromTo00(lua_State* tolua_S)
{
#ifndef TOLUA_RELEASE
 tolua_Error tolua_err;
 if (
     !tolua_isusertype(tolua_S,1,"TweenManager",0,&tolua_err) ||
     !tolua_isnumber(tolua_S,2,0,&tolua_err) ||
     !tolua_isnumber(tolua_S,3,0,&tolua_err) ||
     !tolua_isnumber(tolua_S,4,0,&tolua_err) ||
     !tolua_isnumber(tolua_S,5,0,&tolua_err) ||
     !tolua_isnumber(tolua_S,6,0,&tolua_err) ||
     !tolua_isnumber(tolua_S,7,0,&tolua_err) ||
     !tolua_isnumber(tolua_S,8,0,&tolua_err) ||
     (tolua_isvaluenil(tolua_S,9,&tolua_err) || !toluafix_isfunction(tolua_S,9,"LUA_FUNCTION",0,&tolua_err)) ||
     (tolua_isvaluenil(tolua_S,10,&tolua_err) || !toluafix_isfunction(tolua_S,10,"LUA_FUNCTION",0,&tolua_err)) ||
     !tolua_isnoobj(tolua_S,11,&tolua_err)
 )
  goto tolua_lerror;
 else
#endif
 {
  TweenManager* self = (TweenManager*)  tolua_tousertype(tolua_S,1,0);
  TWEEN_INTERPOLATION_TYPE type = ((TWEEN_INTERPOLATION_TYPE) (int)  tolua_tonumber(tolua_S,2,0));
  float delay = ((float)  tolua_tonumber(tolua_S,3,0));
  float duration = ((float)  tolua_tonumber(tolua_S,4,0));
  float interval = ((float)  tolua_tonumber(tolua_S,5,0));
  float from = ((float)  tolua_tonumber(tolua_S,6,0));
  float to = ((float)  tolua_tonumber(tolua_S,7,0));
  int loopCount = ((int)  tolua_tonumber(tolua_S,8,0));
  LUA_FUNCTION nSeterHandler = (  toluafix_ref_function(tolua_S,9,0));
  LUA_FUNCTION nEndHandler = (  toluafix_ref_function(tolua_S,10,0));
#ifndef TOLUA_RELEASE
  if (!self) tolua_error(tolua_S,"invalid 'self' in function 'tweenFromTo'", NULL);
#endif
  {
   int tolua_ret = (int)  self->tweenFromTo(type,delay,duration,interval,from,to,loopCount,nSeterHandler,nEndHandler);
   tolua_pushnumber(tolua_S,(lua_Number)tolua_ret);
  }
 }
 return 1;
#ifndef TOLUA_RELEASE
 tolua_lerror:
 tolua_error(tolua_S,"#ferror in function 'tweenFromTo'.",&tolua_err);
 return 0;
#endif
}
#endif //#ifndef TOLUA_DISABLE

/* method: removeTween of class  TweenManager */
#ifndef TOLUA_DISABLE_tolua_TweenManager_TweenManager_removeTween00
static int tolua_TweenManager_TweenManager_removeTween00(lua_State* tolua_S)
{
#ifndef TOLUA_RELEASE
 tolua_Error tolua_err;
 if (
     !tolua_isusertype(tolua_S,1,"TweenManager",0,&tolua_err) ||
     !tolua_isnumber(tolua_S,2,0,&tolua_err) ||
     !tolua_isnoobj(tolua_S,3,&tolua_err)
 )
  goto tolua_lerror;
 else
#endif
 {
  TweenManager* self = (TweenManager*)  tolua_tousertype(tolua_S,1,0);
  int nTweenHandle = ((int)  tolua_tonumber(tolua_S,2,0));
#ifndef TOLUA_RELEASE
  if (!self) tolua_error(tolua_S,"invalid 'self' in function 'removeTween'", NULL);
#endif
  {
   self->removeTween(nTweenHandle);
  }
 }
 return 0;
#ifndef TOLUA_RELEASE
 tolua_lerror:
 tolua_error(tolua_S,"#ferror in function 'removeTween'.",&tolua_err);
 return 0;
#endif
}
#endif //#ifndef TOLUA_DISABLE

/* method: removeAllTween of class  TweenManager */
#ifndef TOLUA_DISABLE_tolua_TweenManager_TweenManager_removeAllTween00
static int tolua_TweenManager_TweenManager_removeAllTween00(lua_State* tolua_S)
{
#ifndef TOLUA_RELEASE
 tolua_Error tolua_err;
 if (
     !tolua_isusertype(tolua_S,1,"TweenManager",0,&tolua_err) ||
     !tolua_isnoobj(tolua_S,2,&tolua_err)
 )
  goto tolua_lerror;
 else
#endif
 {
  TweenManager* self = (TweenManager*)  tolua_tousertype(tolua_S,1,0);
#ifndef TOLUA_RELEASE
  if (!self) tolua_error(tolua_S,"invalid 'self' in function 'removeAllTween'", NULL);
#endif
  {
   self->removeAllTween();
  }
 }
 return 0;
#ifndef TOLUA_RELEASE
 tolua_lerror:
 tolua_error(tolua_S,"#ferror in function 'removeAllTween'.",&tolua_err);
 return 0;
#endif
}
#endif //#ifndef TOLUA_DISABLE

/* Open function */
TOLUA_API int tolua_TweenManager_open (lua_State* tolua_S)
{
 tolua_open(tolua_S);
 tolua_reg_types(tolua_S);
 tolua_module(tolua_S,NULL,0);
 tolua_beginmodule(tolua_S,NULL);
  tolua_constant(tolua_S,"LINEAR_IN",LINEAR_IN);
  tolua_constant(tolua_S,"LINEAR_OUT",LINEAR_OUT);
  tolua_constant(tolua_S,"LINEAR_INOUT",LINEAR_INOUT);
  tolua_constant(tolua_S,"BOUNCE_IN",BOUNCE_IN);
  tolua_constant(tolua_S,"BOUNCE_OUT",BOUNCE_OUT);
  tolua_constant(tolua_S,"BOUNCE_INOUT",BOUNCE_INOUT);
  tolua_constant(tolua_S,"EXPO_IN",EXPO_IN);
  tolua_constant(tolua_S,"EXPO_OUT",EXPO_OUT);
  tolua_constant(tolua_S,"EXPO_INOUT",EXPO_INOUT);
  tolua_constant(tolua_S,"ELASTIC_IN",ELASTIC_IN);
  tolua_constant(tolua_S,"ELASTIC_OUT",ELASTIC_OUT);
  tolua_constant(tolua_S,"ELASTIC_INOUT",ELASTIC_INOUT);
  tolua_constant(tolua_S,"QUART_IN",QUART_IN);
  tolua_constant(tolua_S,"QUART_OUT",QUART_OUT);
  tolua_constant(tolua_S,"QUART_INOUT",QUART_INOUT);
  tolua_constant(tolua_S,"QUINT_IN",QUINT_IN);
  tolua_constant(tolua_S,"QUINT_OUT",QUINT_OUT);
  tolua_constant(tolua_S,"QUINT_INOUT",QUINT_INOUT);
  tolua_constant(tolua_S,"QUAD_IN",QUAD_IN);
  tolua_constant(tolua_S,"QUAD_OUT",QUAD_OUT);
  tolua_constant(tolua_S,"QUAD_INOUT",QUAD_INOUT);
  tolua_constant(tolua_S,"BACK_IN",BACK_IN);
  tolua_constant(tolua_S,"BACK_OUT",BACK_OUT);
  tolua_constant(tolua_S,"BACK_INOUT",BACK_INOUT);
  tolua_constant(tolua_S,"CUBIC_IN",CUBIC_IN);
  tolua_constant(tolua_S,"CUBIC_OUT",CUBIC_OUT);
  tolua_constant(tolua_S,"CUBIC_INOUT",CUBIC_INOUT);
  tolua_constant(tolua_S,"STRONG_IN",STRONG_IN);
  tolua_constant(tolua_S,"STRONG_OUT",STRONG_OUT);
  tolua_constant(tolua_S,"STRONG_INOUT",STRONG_INOUT);
  tolua_constant(tolua_S,"CIRC_IN",CIRC_IN);
  tolua_constant(tolua_S,"CIRC_OUT",CIRC_OUT);
  tolua_constant(tolua_S,"CIRC_INOUT",CIRC_INOUT);
  tolua_constant(tolua_S,"SINE_IN",SINE_IN);
  tolua_constant(tolua_S,"SINE_OUT",SINE_OUT);
  tolua_constant(tolua_S,"SINE_INOUT",SINE_INOUT);
  tolua_cclass(tolua_S,"TweenManager","TweenManager","",NULL);
  tolua_beginmodule(tolua_S,"TweenManager");
   tolua_function(tolua_S,"sharedTweenManager",tolua_TweenManager_TweenManager_sharedTweenManager00);
   tolua_function(tolua_S,"tweenFromTo",tolua_TweenManager_TweenManager_tweenFromTo00);
   tolua_function(tolua_S,"removeTween",tolua_TweenManager_TweenManager_removeTween00);
   tolua_function(tolua_S,"removeAllTween",tolua_TweenManager_TweenManager_removeAllTween00);
  tolua_endmodule(tolua_S);
 tolua_endmodule(tolua_S);
 return 1;
}


#if defined(LUA_VERSION_NUM) && LUA_VERSION_NUM >= 501
 TOLUA_API int luaopen_TweenManager (lua_State* tolua_S) {
 return tolua_TweenManager_open(tolua_S);
};
#endif

