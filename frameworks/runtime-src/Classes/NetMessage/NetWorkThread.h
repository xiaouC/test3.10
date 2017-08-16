#pragma once
#include "../Common/TLCommon.h"
#include "semaphore.h"
#include <mutex>
#include "pthread.h"

class CNetSender;

class CNetWorkThread {
public:
	CNetWorkThread(CNetSender* pNetSender);
	~CNetWorkThread();

	bool Connect(const char* szIPAddr, unsigned int uiPort);
	void CloseSocket();

	static void* RecvThread(void* pParam);
	static void* SendThread(void* pParam);

	SOCKET GetSocketID() { return m_socketID; }

    bool RecvThreadRunning() { return m_bRecvThreadExit; }
    bool SendThreadRunning() { return m_bSendThreadExit; }

protected:
    CNetSender* m_pNetSender;

	SOCKET m_socketID;
    std::mutex m_socketLock;

    std::string m_strIPAddr;
	unsigned int m_uiPort;

	//////////////////////////////////////////////////////////////////////////
	bool m_bIsExit;

	bool m_bRecvThreadExit;
	bool m_bSendThreadExit;

	pthread_t m_hRecvThreadID;
	pthread_t m_hSendThreadID;

    float m_fLastConnectTime;           // 上一次创建 socket 连接的时间
};
