#pragma once
#include <map>
#include "base/CCRef.h"

USING_NS_CC;

enum TWEEN_INTERPOLATION_TYPE
{
    LINEAR_IN,	//!< 
    LINEAR_OUT,
    LINEAR_INOUT,

    BOUNCE_IN,	//!< 
    BOUNCE_OUT,
    BOUNCE_INOUT,

    EXPO_IN,	//!< 
    EXPO_OUT,
    EXPO_INOUT,

    ELASTIC_IN,	//!< 
    ELASTIC_OUT,
    ELASTIC_INOUT,

    QUART_IN,	//!< 
    QUART_OUT,
    QUART_INOUT,

    QUINT_IN,	//!< 
    QUINT_OUT,
    QUINT_INOUT,

    QUAD_IN,	//!< 
    QUAD_OUT,
    QUAD_INOUT,

    BACK_IN,	//!< 
    BACK_OUT,
    BACK_INOUT,

    CUBIC_IN,	//!< 
    CUBIC_OUT,
    CUBIC_INOUT,

    STRONG_IN,	//!< 
    STRONG_OUT,
    STRONG_INOUT,

    CIRC_IN,	//!<  
    CIRC_OUT,
    CIRC_INOUT,

    SINE_IN,	//!< 
    SINE_OUT,
    SINE_INOUT,
};

typedef float ( *InterpolationFunc )( float t, float b, float c, float d );

class TweenManager : public Ref
{
public:
    TweenManager();
	virtual ~TweenManager();

	static TweenManager* sharedTweenManager();

	void update( float dt );

public:
    int tweenFromTo( TWEEN_INTERPOLATION_TYPE type, float delay, float duration, float interval, float from, float to, int loopCount,
            int nSeterHandler, int nEndHandler );
    void removeTween( int nTweenHandle );
    void removeAllTween();

protected:
    int m_nNextTweenHandle;
    int getNextTweenHandle() { return ++m_nNextTweenHandle; }

    std::map<TWEEN_INTERPOLATION_TYPE,InterpolationFunc> m_mapInterpolationFunc;

protected:
    struct TweenData
    {
        bool bIsPause;
        InterpolationFunc func;
        float delay;
        float duration;
        float interval;
        float from;
        float to;
        int nLoopCount;
        int nGeterHandler;
        int nSeterHandler;
        int nEndHandler;

        float tick;
        bool bDelete;
    };
    std::map<int,TweenData*> m_mapTweenList;
};

#include "interpolation.h"

