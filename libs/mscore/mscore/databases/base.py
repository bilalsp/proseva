# from abc import ABC, abstractmethod


# class BaseDatabaseManager(ABC):
#     def __init__(self, db_url):
#         return NotImplemented

#     @abstractmethod
#     def insert_data(self, table_name, data):
#         pass

#     @abstractmethod
#     def update_data(self, table_name, data, condition):
#         pass

#     @abstractmethod
#     def delete_data(self, table_name, condition):
#         pass


# class BaseDatabaseManagerMeta(type):
#     def __new__(cls, name, bases, attrs):
#         new_cls = super().__new__(cls, name, bases, attrs)

#         if name != 'BaseDatabaseManager':
#             BaseDatabaseManagerMeta.register_manager(new_cls)

#         return new_cls

#     @classmethod
#     def register_manager(cls, manager_class):
#         scheme = manager_class.get_scheme()
#         cls.SUPPORTED_MANAGERS[scheme] = manager_class

# class BaseDatabaseManager(metaclass=BaseDatabaseManagerMeta):
#     SUPPORTED_MANAGERS = {}

#     @classmethod
#     def create_manager(cls, db_url):
#         parsed_url = urlparse(db_url)
#         scheme = parsed_url.scheme.lower()

#         if scheme in cls.SUPPORTED_MANAGERS:
#             manager_class = cls.SUPPORTED_MANAGERS[scheme]
#             return manager_class({'url': db_url, 'database': parsed_url.path[1:]})
#         else:
#             raise ValueError(f"Unsupported database scheme in URL: {scheme}")

#     @classmethod
#     def get_scheme(cls):
#         raise NotImplementedError("get_scheme method must be implemented in subclass")
