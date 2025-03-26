# from mscore.databases.base import BaseDatabaseManager

# __all__ = [
#     "BaseDatabaseManager",
# ]


# https://chat.openai.com/c/5e8f5aa4-0f18-4f4f-baad-1429b644e44c

# class DatabaseManagerFactory:
#     SUPPORTED_SCHEMES = {
#         'sql': SQLDatabaseManager,
#         'age': ApacheAgeDatabaseManager,
#         'neo4j': Neo4jDatabaseManager,
#     }

#     @classmethod
#     def create_manager(cls, db_url):
#         parsed_url = urlparse(db_url)
#         scheme = parsed_url.scheme.lower()

#         if scheme in cls.SUPPORTED_SCHEMES:
#             manager_class = cls.SUPPORTED_SCHEMES[scheme]
#             return manager_class({'url': db_url, 'database': parsed_url.path[1:]})
#         else:
#             raise ValueError(f"Unsupported database scheme in URL: {scheme}")
