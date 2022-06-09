import pymongo
from acss_core.config import PIPE_EVENT_DB_USER, PIPE_EVENT_DB_PW, PIPE_EVENT_DB_URL


class EventDatabase:
    def __init__(self, url=f"mongodb://{PIPE_EVENT_DB_USER}:{PIPE_EVENT_DB_PW}@{PIPE_EVENT_DB_URL}:27017/"):
        self.client = pymongo.MongoClient(url)
        print(self.client)
        self.db = self.client.service_data
        print(f"wait until mongo db (${url}) is running")
        if self.client.is_mongos:
            print("mongo db started.")

    def insert(self, msg):
        # to dict
        return self.db.service_data.insert_one(msg)

    def find_by_id(self, id):
        res = self.db.service_data.find_one({"id": id}, {'_id': False})
        return res

    def find_by_timestamp(self, from_date, to_date):
        res = self.db.service_data.find({"timestamp": {"$gte": from_date, "$lt": to_date}})
        return [r for r in res]
