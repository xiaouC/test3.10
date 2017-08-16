#pragma once
#include "../Common/TLCommon.h"
#include "semaphore.h"
#include <list>
#include <queue>
#include <map>
#include <mutex>

namespace google {
    namespace protobuf {
        class MessageLite;
    }
}

class CNetMsg;
class CNetWorkThread;

class CNetSender {
	friend class CNetWorkThread;
public:
    static CNetSender* SharedNetSender();

	void CloseSocket();
	bool Connect(const char* szIPAddr, unsigned int uiPort);

	void NewNetMsgAndSend(unsigned short msgID, ::google::protobuf::MessageLite* pMsg, int nCallBackHandler = 0);
	void NewNetMsgAndSend(unsigned short msgID, const char* pszMsgData = NULL, int nLength = 0, int nCallBackHandler = 0);

protected:
	CNetMsg* GetSendMessage();
	CNetSender(const char* sem_name);
	~CNetSender();

	void SendNetMessage(CNetMsg* pNetMsg);

    void appendWaitRecvMsg(CNetMsg* pNetMsg);
    CNetMsg* getWaitRecvMsg(unsigned int uiMsgID);
    CNetMsg* parseNetMsg(char* szRevcBuf, unsigned int nLength);

	sem_t* GetSendMsgSem() { return m_pSemSendMsg; }

protected:
    std::mutex m_SendNetMsgLock;
	sem_t* m_pSemSendMsg;
#if USE_NAMED_SEMAPHORE
#else
    sem_t m_sem;
#endif
	std::list<CNetMsg*> m_listSendMsg;
    std::list<CNetMsg*> m_listWaitRecvMsg;

    unsigned short GetNextSequenceID(unsigned short msgID);
    std::map<unsigned short,unsigned short> m_mapSequenceID;

	CNetWorkThread* m_pNetWorkThread;
};

class CNetReceiver {
public:
	~CNetReceiver();
    static CNetReceiver* SharedNetReceiver();

    // 设置错误消息处理函数
	void SetMsgErrorDefaultFuncPtr(int nLuaHandle);
	void RegisterMsgErrorFuncPtr(int nMsgCode, int nLuaHandle);
	void RegisterMsgProcessFuncPtr(unsigned short nMsgID, int nLuaHandler);

    // 设置lua网络消息回调函数	
	void ProcessMsg();
	void AppendMsg(CNetMsg* pNetMsg);
	void SendErrorMsgToSelf(unsigned int uiMsgCode);
	void SendMsgToSelf(unsigned int msgID, google::protobuf::MessageLite* pMsg);
	void SendMsgToSelf(unsigned int msgID, const char* pszMsgData = NULL, int nLength = 0);

    void Reset();

protected:
	CNetReceiver();
	void NetMsgCallback(CNetMsg* pNetMsg);

    std::mutex m_RecvNetMsgLock;
	std::queue<CNetMsg*> m_quRecvMsg;

	//////////////////////////////////////////////////////////////////////////
    int m_nMsgErrorDefaultHandler;
	std::map<int, int> m_mapMsgErrorFuncPtr;
    std::map<unsigned short, int> m_mapNetMsgFunc;
};
