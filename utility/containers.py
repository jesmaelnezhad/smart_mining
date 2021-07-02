import copy
import json
from threading import Lock


OWNER_KEY = "owner"
OBJECT_ID_KEY = "object_id"


class PersistentObject:

    def __init__(self, owner, object_id):
        self.__setitem__(OWNER_KEY, owner)
        self.__setitem__(OBJECT_ID_KEY, object_id)

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__.get(key)

    def __delitem__(self, key):
        del self.__dict__[key]

    def get_owner(self):
        return self[OWNER_KEY]

    def get_object_id(self):
        return self[OBJECT_ID_KEY]

    def json(self):
        return json.dumps(self.__dict__)

    def __str__(self):
        return self.json().__str__()

    def save_in_db(self, db):
        db.key_value_put(self.get_owner(), self.get_object_id(), self.__str__())

    def load_from_db(self, db):
        json_str = db.key_value_get(self.get_owner(), self.get_object_id())
        self.__dict__ = json.loads(json_str)
        self.recast_attr_types_after_load()

    def delete_from_db(self, db):
        return db.key_value_delete(self.get_owner(), self.get_object_id())

    def recast_attr_types_after_load(self):
        pass


class ThreadSafeDictionary:
    """
    A key value dictionary that can be used by multiple threads concurrently.
    """

    def __init__(self):
        self.objects = dict()
        self.objects_mutex = Lock()

    def snapshot(self, should_clear=False):
        self.objects_mutex.acquire()
        try:
            result = dict()
            for k, v in self.objects.items():
                result[k] = copy.deepcopy(self.objects[k])
            if should_clear:
                self.objects.clear()
            return result
        finally:
            self.objects_mutex.release()

    def bulk_insert(self, data_dictionary):
        self.objects_mutex.acquire()
        try:
            for k, v in data_dictionary.items():
                self.objects[k] = v
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

    def call_method_from_object(self, func, args, key=None):
        """
        Calls the given function with the given arguments on the object pointed by the given key.
        If key is None, it calls the given function and args on all objects.
        :param key:
        :param func:
        :param args:
        :return: True if the given func is called at least once, and False otherwise.
        """
        self.objects_mutex.acquire()
        try:
            called_at_least_once = False
            if key is None:
                for object_key in self.objects.keys():
                    func(self.objects[object_key], **args)
                    called_at_least_once = True
            elif key in self.objects.keys():
                func(self.objects[key], **args)
                called_at_least_once = True
            return called_at_least_once
        finally:
            self.objects_mutex.release()

    def clear_by_predicate(self, predicate_function, args):
        """
        Removes any object (say o) which makes predicate_function(o, **args) return False
        :param predicate_function:
        :param args:
        :return:
        """
        self.objects_mutex.acquire()
        try:
            to_keep = dict()
            for k, v in self.objects.items():
                if predicate_function(v, **args):
                    to_keep[k] = v
            self.objects.clear()
            self.objects = to_keep
        finally:
            self.objects_mutex.release()


class PersistentThreadSafeDictionary(ThreadSafeDictionary):
    def __init__(self, orders_db_handler):
        super(PersistentThreadSafeDictionary, self).__init__()
        self.orders_db = orders_db_handler

    def set(self, key, obj):
        if not isinstance(obj, PersistentObject):
            raise Exception("Non-persistent object type is passed to persistent dictionary.")
        super(PersistentThreadSafeDictionary, self).set(key, obj)

    def bulk_insert(self, data_dictionary):
        for k, v in data_dictionary.items():
            if not isinstance(v, PersistentObject):
                raise Exception("Non-persistent object {0} type is passed to persistent dictionary.".format(v))
        super(PersistentThreadSafeDictionary, self).bulk_insert(data_dictionary)

    def save_objects(self):
        super(PersistentThreadSafeDictionary, self).call_method_from_object(PersistentObject.save_in_db,
                                                                            {'db': self.orders_db}, key=None)

    def load_objects(self):
        super(PersistentThreadSafeDictionary, self).call_method_from_object(PersistentObject.load_from_db,
                                                                            {'db': self.orders_db}, key=None)
