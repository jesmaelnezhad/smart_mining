import copy
from threading import Lock


class ThreadSafeDictionary:
    """
    A key value dictionary that can be used by multiple threads concurrently.
    """

    def __init__(self):
        self.objects = dict()
        self.objects_mutex = Lock()

    def snapshot(self):
        self.objects_mutex.acquire()
        try:
            result = dict()
            for k,v in self.objects.items():
                result[k] = copy.deepcopy(self.objects[k])
            return result
        finally:
            self.objects_mutex.release()

    def has(self, key):
        self.objects_mutex.acquire()
        try:
            return key in self.objects.keys()
        finally:
            self.objects_mutex.release()

    def set(self, key, obj):
        self.objects_mutex.acquire()
        try:
            self.objects[key] = obj
        finally:
            self.objects_mutex.release()

    def unset(self, key):
        self.objects_mutex.acquire()
        try:
            if key in self.objects.keys():
                del self.objects[key]
                return True
            return False
        finally:
            self.objects_mutex.release()

    def get(self, key):
        self.objects_mutex.acquire()
        try:
            if key in self.objects.keys():
                obj = copy.deepcopy(self.objects[key])
                return True, obj
            return False, None
        finally:
            self.objects_mutex.release()

    def call_method_from_object(self, key, func, args):
        self.objects_mutex.acquire()
        try:
            if key in self.objects.keys():
                func(self.objects[key], **args)
                return True
            return False
        finally:
            self.objects_mutex.release()
