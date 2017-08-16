#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <CCCommon.h>
#include "tolua++.h"
#include "CCLuaEngine.h"
#include "tolua_fix.h"
#include "google/protobuf/message_lite.h"

#ifndef WIN32
#include <sys/socket.h>
#include <arpa/inet.h>
#endif

#include "../NetMessage/NetMsgProcess.h"
#include "../NetMessage/NetWorkThread.h"
#include "../NetMessage/NetMsg.h"

static CNetSender* g_pNetSender = NULL;
CNetSender* CNetSender::SharedNetSender() {
    if (g_pNetSender == NULL) {
        std::string strSemName = std::string("net_sender") + getProjectNickname();
        g_pNetSender = new CNetSender(strSemName.c_str());
    }

    return g_pNetSender;
}

CNetSender::CNetSender(const char* sem_name)
{
    m_pSemSendMsg = NULL;
#if USE_NAMED_SEMAPHORE
    CCAssert(sem_name!=NULL, "don't support unnamed semaphore");
    m_pSemSendMsg = sem_open(sem_name, O_CREAT, 0644, 0);
    if (m_pSemSendMsg == SEM_FAILED) {
        CCLog("CCTextureCache async thread semaphore init error: %s\n", strerror(errno));
        CCAssert(false, "open named sem failed");
        m_pSemSendMsg = NULL;
        return;
    }
#else
    int iRet = sem_init(&m_sem, 0, 0);
    if (iRet<0) {
        CCLog("CCTextureCache async thread semaphore init error: %s\n", strerror(errno));
        CCAssert(false, "init sem failed");
        return;
    }
    m_pSemSendMsg = &m_sem;
#endif

    m_pNetWorkThread = new CNetWorkThread(this);
}

CNetSender::~CNetSender() {
	delete m_pNetWorkThread;
	sem_destroy(m_pSemSendMsg);

    std::list<CNetMsg*>::iterator iter = m_listSendMsg.begin();
    std::list<CNetMsg*>::iterator iter_end = m_listSendMsg.end();
    for (; iter != iter_end; ++iter)
        delete (*iter);
    m_listSendMsg.clear();

    std::list<CNetMsg*>::iterator iter_w = m_listWaitRecvMsg.begin();
    std::list<CNetMsg*>::iterator iter_w_end = m_listWaitRecvMsg.end();
    for (; iter_w != iter_w_end; ++iter_w)
        delete (*iter_w);
    m_listWaitRecvMsg.clear();

    g_pNetSender = NULL;
}

void CNetSender::SendNetMessage(CNetMsg* pNetMsg) {
    std::lock_guard<std::mutex> lock(m_SendNetMsgLock);

	m_listSendMsg.push_back(pNetMsg);

	sem_post(m_pSemSendMsg);
}

CNetMsg* CNetSender::GetSendMessage() {
    std::lock_guard<std::mutex> lock(m_SendNetMsgLock);

    if (!m_listSendMsg.empty()) {
        std::list<CNetMsg*>::iterator iter = m_listSendMsg.begin();

        CNetMsg* pSendMsg = (*iter);

        m_listSendMsg.erase(iter);

        return pSendMsg;
    }

	return NULL;
}

bool CNetSender::Connect(const char* szIPAddr, unsigned int uiPort) {
	return m_pNetWorkThread->Connect(szIPAddr, uiPort);
}

void CNetSender::CloseSocket() {
    std::lock_guard<std::mutex> lock(m_SendNetMsgLock);

    std::list<CNetMsg*>::iterator iter = m_listSendMsg.begin();
    std::list<CNetMsg*>::iterator iter_end = m_listSendMsg.end();
    for (; iter != iter_end; ++iter)
        delete (*iter);
    m_listSendMsg.clear();

    std::list<CNetMsg*>::iterator iter_w = m_listWaitRecvMsg.begin();
    std::list<CNetMsg*>::iterator iter_w_end = m_listWaitRecvMsg.end();
    for (; iter_w != iter_w_end; ++iter_w)
        delete (*iter_w);
    m_listWaitRecvMsg.clear();

    // 关闭 socket
	m_pNetWorkThread->CloseSocket(status);
}

void CNetSender::NewNetMsgAndSend(unsigned short msgID, google::protobuf::MessageLite* pMsg, int nCallBackHandler) {
	std::string strMsgContent;
	pMsg->SerializeToString(&strMsgContent);

	NewNetMsgAndSend(msgID, strMsgContent.c_str(), strMsgContent.length(), nCallBackHandler);
}

void CNetSender::NewNetMsgAndSend(unsigned short msgID, const char* pszMsgData, int nLength, int nCallBackHandler) {
	unsigned int uiMsgLength = nLength + 12;	// 12 是消息头长度

    unsigned int uiMsgID = packMsgID(msgID, GetNextSequenceID(msgID));

	CNetMsg* pNetMsg = new CNetMsg;
	pNetMsg->m_uiMsgLength = uiMsgLength;
	pNetMsg->m_uiMsgID = uiMsgID;
    pNetMsg->m_nCallBackHandler = nCallBackHandler;

	pNetMsg->m_szMsgData = new char[pNetMsg->m_uiMsgLength];
	memset(pNetMsg->m_szMsgData, 0, uiMsgLength);

	// 写消息头
	unsigned int uiTemp = htonl(pNetMsg->m_uiMsgLength);
	memcpy(pNetMsg->m_szMsgData, &uiTemp, 4);

	uiTemp = htonl(pNetMsg->m_uiMsgID);
	memcpy(pNetMsg->m_szMsgData + 4, &uiTemp, 4);

	uiTemp = htonl(pNetMsg->m_uiCode);
	memcpy(pNetMsg->m_szMsgData + 8, &uiTemp, 4);

	// 写消息的实际内容
	if (pszMsgData != NULL)
		memcpy(pNetMsg->m_szMsgData + 12, pszMsgData, nLength);

	SendNetMessage(pNetMsg);
}

unsigned short CNetSender::GetNextSequenceID(unsigned short msgID) {
    std::map<unsigned short,unsigned short>::iterator iter = m_mapSequenceID.find(msgID);
    if (iter != m_mapSequenceID.end())
        return ++iter->second;

    m_mapSequenceID[msgID] = 1;

    return 1;
}

void CNetSender::appendWaitRecvMsg(CNetMsg* pNetMsg) {
    std::lock_guard<std::mutex> lock(m_SendNetMsgLock);

    m_listWaitRecvMsg.push_back(pNetMsg);
}

CNetMsg* CNetSender::getWaitRecvMsg(unsigned int uiMsgID) {
    std::lock_guard<std::mutex> lock(m_SendNetMsgLock);

    // 从等待列表里面查找
    std::list<CNetMsg*>::iterator iter = m_listWaitRecvMsg.begin();
    std::list<CNetMsg*>::iterator iter_end = m_listWaitRecvMsg.end();
    for (; iter != iter_end; ++iter) {
        CNetMsg* pNetMsg = (*iter);
        if (pNetMsg->m_uiMsgID == uiMsgID) {
            if (pNetMsg->m_szMsgData != NULL) {
                delete[] pNetMsg->m_szMsgData;
                pNetMsg->m_szMsgData = NULL;
            }

            m_listWaitRecvMsg.erase(iter);

            return pNetMsg;
        }
    }

    // 等待列表中没有的话，就创建一个新的返回
    CNetMsg* pNetMsg = new CNetMsg;
    pNetMsg->m_uiMsgID = uiMsgID;
    return pNetMsg;
}

CNetMsg* CNetSender::parseNetMsg(char* szRevcBuf, unsigned int nLength) {
	unsigned int uiTemp;
	memcpy(&uiTemp, szRevcBuf + 4, 4);

    CNetMsg* pNetMsg = getWaitRecvMsg(ntohl(uiTemp));
    pNetMsg->m_uiMsgLength = nLength;

	pNetMsg->m_szMsgData = new char[nLength];
	memcpy(pNetMsg->m_szMsgData, szRevcBuf, nLength);

	memcpy(&uiTemp, pNetMsg->m_szMsgData + 8, 4);
	pNetMsg->m_uiCode = ntohl(uiTemp);

	return pNetMsg;
}

static CNetReceiver* g_pNetReceiver = NULL;
CNetReceiver::CNetReceiver()
: m_nMsgErrorDefaultHandler(0)
{
}

CNetReceiver::~CNetReceiver() {
	while (!m_quRecvMsg.empty()) {
		CNetMsg* pNetMsg = m_quRecvMsg.front();
		m_quRecvMsg.pop();

		delete pNetMsg;
	}
	g_pNetReceiver = NULL;
}

CNetReceiver* CNetReceiver::SharedNetReceiver() {
    if (g_pNetReceiver==NULL)
        g_pNetReceiver = new CNetReceiver();

    return g_pNetReceiver;
}

void CNetReceiver::ProcessMsg() {
    std::lock_guard<std::mutex> lock(m_RecvNetMsgLock);

	while (!m_quRecvMsg.empty()) {
		CNetMsg* pNetMsg = m_quRecvMsg.front();
		m_quRecvMsg.pop();

        NetMsgCallback(pNetMsg);
		delete pNetMsg;
	}
}

void CNetReceiver::NetMsgCallback(CNetMsg* pNetMsg) {
    unsigned int uiCode = pNetMsg->GetMsgCode();
    if (uiCode == 0) {
        unsigned short sRealMsgID, sSquID;
        unpackMsgID(pNetMsg->GetMsgID(), sRealMsgID, sSquID);
        std::map<unsigned short, int>::iterator iter = m_mapNetMsgFunc.find(sRealMsgID);
        if (iter != m_mapNetMsgFunc.end()) {
            CCLuaEngine::defaultEngine()->getLuaStack()->pushCCObject(pNetMsg, "CNetMsg");
            CCLuaEngine::defaultEngine()->getLuaStack()->executeFunctionByHandler(iter->second, 1);
        }

        // 发送消息者自己的回调
        if (pNetMsg->m_nCallBackHandler > 0) {
            CCLuaEngine::defaultEngine()->getLuaStack()->pushCCObject(pNetMsg, "CNetMsg");
            CCLuaEngine::defaultEngine()->getLuaStack()->executeFunctionByHandler(pNetMsg->m_nCallBackHandler, 1);
        }
    } else {
        int nErrHandler = m_nMsgErrorDefaultHandler;
        std::map<int, int>::iterator iter = m_mapMsgErrorFuncPtr.find(uiCode);
        if (iter != m_mapMsgErrorFuncPtr.end())
            nErrHandler = iter->second;

        if (nErrHandler > 0) {
            CCLuaEngine::defaultEngine()->getLuaStack()->pushCCObject(pNetMsg, "CNetMsg");
            CCLuaEngine::defaultEngine()->getLuaStack()->executeFunctionByHandler(nErrHandler, 1);
        }
    }
}

void CNetReceiver::SetMsgErrorDefaultFuncPtr(int nLuaHandle) {
    std::lock_guard<std::mutex> lock(m_RecvNetMsgLock);

	if (m_nMsgErrorDefaultHandler > 0)
		CCLuaEngine::defaultEngine()->getLuaStack()->removeScriptHandler(m_nMsgErrorDefaultHandler);

	m_nMsgErrorDefaultHandler = nLuaHandle;
}

void CNetReceiver::RegisterMsgErrorFuncPtr(int nMsgCode, int nLuaHandle) {
    std::lock_guard<std::mutex> lock(m_RecvNetMsgLock);

	std::map<int, int>::iterator iter = m_mapMsgErrorFuncPtr.find(nMsgCode);
	if (iter != m_mapMsgErrorFuncPtr.end()) {
		if (iter->second > 0)
			CCLuaEngine::defaultEngine()->getLuaStack()->removeScriptHandler(iter->second);

		iter->second = nLuaHandle;

		return;
	}

	m_mapMsgErrorFuncPtr[nMsgCode] = nLuaHandle;
}

void CNetReceiver::RegisterMsgProcessFuncPtr(unsigned short nMsgID, int nLuaHandler) {
    std::lock_guard<std::mutex> lock(m_RecvNetMsgLock);

    std::map<unsigned short, int>::iterator iter = m_mapNetMsgFunc.find(nMsgID);
    if (iter != m_mapNetMsgFunc.end())
        CCLuaEngine::defaultEngine()->getLuaStack()->removeScriptHandler(iter->second);

    m_mapNetMsgFunc[nMsgID] = nLuaHandler;
}

void CNetReceiver::AppendMsg(CNetMsg* pNetMsg) {
    std::lock_guard<std::mutex> lock(m_RecvNetMsgLock);

    unsigned short sRealMsgID, sSquID;
    unpackMsgID(pNetMsg->GetMsgID(), sRealMsgID, sSquID);
    unsigned int uiCode = pNetMsg->GetMsgCode();

	m_quRecvMsg.push(pNetMsg);
}

void CNetReceiver::SendErrorMsgToSelf(unsigned int uiMsgCode) {
	AppendMsg(new CNetMsg(uiMsgCode));
}

void CNetReceiver::SendMsgToSelf(unsigned int msgID, google::protobuf::MessageLite* pMsg) {
	unsigned int uiMsgLength = 0;
	std::string strMsgContent;
	pMsg->SerializeToString(&strMsgContent);
	uiMsgLength = strMsgContent.length() + 12;	// 12 是消息头长度

	CNetMsg* pNetMsg = new CNetMsg;
	pNetMsg->m_uiMsgLength = uiMsgLength;
	pNetMsg->m_uiMsgID = msgID;

	pNetMsg->m_szMsgData = new char[pNetMsg->m_uiMsgLength];
	memset(pNetMsg->m_szMsgData, 0, uiMsgLength);
	//写消息头
	unsigned int uiTemp = htonl(pNetMsg->m_uiMsgLength);
	memcpy(pNetMsg->m_szMsgData, &uiTemp, 4);
	uiTemp = htonl(pNetMsg->m_uiMsgID);
	memcpy(pNetMsg->m_szMsgData + 4, &uiTemp, 4);
	uiTemp = htonl(pNetMsg->m_uiCode);
	memcpy(pNetMsg->m_szMsgData + 8, &uiTemp, 4);

	// 写消息的实际内容
	if (NULL != strMsgContent.c_str())
		memcpy(pNetMsg->m_szMsgData + 12, strMsgContent.c_str(), strMsgContent.length());

	AppendMsg(pNetMsg);
}

void CNetReceiver::SendMsgToSelf(unsigned int msgID, const char* pszMsgData, int nLength) {
	unsigned int uiMsgLength = nLength + 12;	// 12 是消息头长度

	CNetMsg* pNetMsg = new CNetMsg;
	pNetMsg->m_uiMsgLength = uiMsgLength;
	pNetMsg->m_uiMsgID = msgID;

	pNetMsg->m_szMsgData = new char[pNetMsg->m_uiMsgLength];
	memset(pNetMsg->m_szMsgData, 0, uiMsgLength);
	// 写消息头
	unsigned int uiTemp = htonl(pNetMsg->m_uiMsgLength);
	memcpy(pNetMsg->m_szMsgData, &uiTemp, 4);
	uiTemp = htonl(pNetMsg->m_uiMsgID);
	memcpy(pNetMsg->m_szMsgData + 4, &uiTemp, 4);
	uiTemp = htonl(pNetMsg->m_uiCode);
	memcpy(pNetMsg->m_szMsgData + 8, &uiTemp, 4);

	// 写消息的实际内容
	if (NULL != pszMsgData)
		memcpy(pNetMsg->m_szMsgData + 12, pszMsgData, nLength);

	AppendMsg(pNetMsg);
}

void CNetReceiver::Reset() {
    std::lock_guard<std::mutex> lock(m_RecvNetMsgLock);

    while (!m_quRecvMsg.empty()) {
		CNetMsg* pNetMsg = m_quRecvMsg.front();
		delete pNetMsg;

        m_quRecvMsg.pop();
    }

	if (m_nMsgErrorDefaultHandler > 0) {
		CCLuaEngine::defaultEngine()->getLuaStack()->removeScriptHandler(m_nMsgErrorDefaultHandler);

		m_nMsgErrorDefaultHandler = 0;
	}

	std::map<int,int>::iterator iter = m_mapMsgErrorFuncPtr.begin();
    for (; iter!=m_mapMsgErrorFuncPtr.end(); iter++) {
        if (iter->second > 0)
			CCLuaEngine::defaultEngine()->getLuaStack()->removeScriptHandler(iter->second);
    }
    m_mapMsgErrorFuncPtr.clear();

	std::map<unsigned short, int>::iterator iter_1 = m_mapNetMsgFunc.begin();
    for (; iter_1!=m_mapNetMsgFunc.end(); iter_1++) {
        if (iter_1->second > 0)
			CCLuaEngine::defaultEngine()->getLuaStack()->removeScriptHandler(iter_1->second);
    }
    m_mapNetMsgFunc.clear();
}

