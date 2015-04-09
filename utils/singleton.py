from utils import *
from utils.configs import Configs

class Singleton(object):
#     def __new__(cls, *args, **kwargs):
#         if not hasattr(cls, '_instance'):
#             cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
#         return cls._instance

    __instance = None
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(Singleton, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self):
        if(self.__initialized): return
        self.__initialized = True
        print ("INIT")

class Sub_Singleton(Singleton):
    def __init__(self):
        print "sub singleton"

if __name__ == "__main__":
    a = Singleton()
    b = Singleton()
#     c = Sub_Singleton()
#     d = Sub_Singleton()

# import threading
# 
# class Singleton(object):
#     objs = {}
#     objs_locker = threading.Lock()
#     def __new__(cls, *args, **kv):
#         if cls in cls.objs:
#             return cls.objs[cls]['obj']
#         cls.objs_locker.acquire()
#         try:
#             if cls in cls.objs:  # # double check locking
#                 return cls.objs[cls]['obj']
#             obj = object.__new__(cls)
#             cls.objs[cls] = {'obj': obj, 'init': False}
#             setattr(cls, '__init__', cls.decorate_init(cls.__init__))
#         finally:
#             cls.objs_locker.release()
#     @classmethod
#     def decorate_init(cls, fn):
#         def init_wrap(*args):
#             if not cls.objs[cls]['init']:
#                 fn(*args)
#                 cls.objs[cls]['init'] = True
#             return
#         return init_wrap
