#coding:utf-8
from libc.string cimport strstr
from libc.stdint cimport uint32_t

def get_cookie_value(bytes s, bytes key):
    if s is None:
        return

    cdef const char* c_s = s
    cdef const char* c_key = key

    cdef const char* begin = strstr(c_s, c_key)
    if begin == NULL:
        return

    begin += len(key)
    if begin[0]!='=':
        return

    begin += 1

    cdef const char* end = strstr(begin, ";")
    
    if end == NULL:
        return c_s[begin-c_s:]
    else:
        return c_s[begin-c_s : end-c_s]

def constant_time_compare(val1, val2):
    """
    Returns True if the two strings are equal, False otherwise.

    The time taken is independent of the number of characters that match.
    """
    if len(val1) != len(val2):
        return False
    cdef char* c_val1 = val1
    cdef char* c_val2 = val2
    cdef uint32_t result = 0
    cdef int size = len(val1)
    cdef int i
    for i in range(size):
        result |= c_val1[i] ^ c_val2[i]
    return result == 0
