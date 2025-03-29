from abc import ABC, abstractmethod
from typing import Any
import pandas as pd
from pymongo import MongoClient
from bson import json_util
import sqlite3
import os


class Storage(ABC):
    """
    Abstract class representing a storage.
    """

    @abstractmethod
    def connect(self, credentials: Any) -> Any:
        """
        Establishes connection with a storage.
        """
        pass

    @abstractmethod
    def close(self, conn: Any) -> None:
        """
        Closes the existing connection with a storage.
        """
        pass

    @abstractmethod
    def write(self, conn: Any, data: pd.DataFrame, location: str) -> None:
        """
        Exports data to the storage in the specified location.
        """
        pass

    @abstractmethod
    def read(self, conn: Any, location: str) -> pd.DataFrame:
        """
        Imports data from the storage located in the specified place.
        """
        pass


class StorageJSON(Storage):
    """
    JSON storage class.
    """

    def connect(self, credentials: Any) -> Any:
        if not os.path.exists(credentials):
            os.mkdir(credentials)
        return credentials

    def close(self, conn: Any) -> None:
        return None

    def write(self, conn: Any, data: pd.DataFrame, location: str) -> None:
        data['date'] = data['date'].dt.strftime('%Y-%m-%d')
        with open(conn + location + '.json', 'w', encoding='UTF-8') as f:
            f.write(data.to_json(orient='records'))

    def read(self, conn: Any, location: str) -> pd.DataFrame:
        with open(conn + location + '.json', 'r', encoding='UTF-8') as f:
            json_str = f.read()
        data = pd.DataFrame(json_util.loads(json_str))
        return data


class StorageMongo(Storage):
    """
    MongoDB storage class.
    """

    def connect(self, credentials: Any) -> Any:
        username = credentials['username']
        password = credentials['password']
        url = credentials['url']
        mongo_uri = f"mongodb+srv://{username}:{password}{url}"

        return MongoClient(mongo_uri)

    def close(self, conn: Any) -> None:
        conn.close()

    def write(self, conn: Any, data: pd.DataFrame, location: str) -> None:
        data['date'] = data['date'].dt.strftime('%Y-%m-%d')
        db = conn["moex"]
        if location in db.list_collection_names():
            collection = db[location]
            collection.drop()
        collection = db[location]
        collection.insert_many(json_util.loads(data.to_json(orient='records')))
    
    def read(self, conn: Any, location: str) -> pd.DataFrame:
        db = conn['moex']
        if location not in db.list_collection_names():
            raise ValueError(f'No collection with name {location} was found!')
        collection = db[location]
        data = pd.DataFrame(list(collection.find()))
        data = data.drop('_id', axis=1)
        return data
    
class StorageSQLite(Storage):
    """
    SQLite storage class
    """
    def connect(self, credentials: Any) -> sqlite3.Connection:
        return sqlite3.connect('moex.db')
    
    def close(self, conn: Any):
        conn.close()
    
    def write(self, conn: sqlite3.Connection, data: pd.DataFrame, location: str) -> None:
        data['date'] = data['date'].dt.strftime('%Y-%m-%d')
        
        # If table exists, drop it
        cursor = conn.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS {location}")
        conn.commit()
        
        # Write new data
        data.to_sql(location, conn, index=False, if_exists='replace')
        conn.commit()

    def read(self, conn: sqlite3.Connection, location: str) -> pd.DataFrame:
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?", 
            (location,)
        )
        if not cursor.fetchone():
            raise ValueError(f'No table with name {location} was found!')
        
        # Read data and convert date column back to datetime
        df = pd.read_sql(f"SELECT * FROM {location}", conn)
        df['date'] = pd.to_datetime(df['date'])
        return df
    
