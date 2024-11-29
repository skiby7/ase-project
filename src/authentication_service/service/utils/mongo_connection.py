from pymongo import MongoClient
from pymongo.collection import Collection

mongo_client: MongoClient | None = None

username = "root"
port = "27017"
auth_source = "admin"
database = "my_database"

def startup_db_client(container_name = "db_authentication"):
    with open('/run/secrets/mongodb_password', 'r') as file:
        password = file.read().strip()
    global mongo_client
    uri = f"mongodb://{username}:{password}@{container_name}:{port}/{database}?authSource={auth_source}&tls=true&tlsAllowInvalidCertificates=true"
    mongo_client = MongoClient(uri)

def get_db_client():
    return mongo_client

def get_accounts_collection() -> Collection:
    db = mongo_client[database]
    return db["accounts"]

def delete_accounts_collection():
    res = get_accounts_collection().delete_many({})
    print(res)