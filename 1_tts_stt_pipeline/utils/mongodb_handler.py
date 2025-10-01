from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import PyMongoError, ConnectionFailure

class MongoDBHandler:
    client: MongoClient
    db: Database
    collection: Collection
    temp_db: Database
    temp_collection: Collection
    
    def __init__(self, config, instance):
        """Initialize a MongoDB Instance to handle communication between script and Database.

        Args:
            config (dict): Config for the project environment, containing connection strings
            instance (str): What MongoDB instance should be made
        """
        
        print("Initializing MongoDB Handler")
        try:
            match instance:
                case "piper":
                    self.client = MongoClient(config['db_host'], config['db_port'])
                    self.db = self.client[config['db_name']]
                    self.collection = self.db[config['db_collection']]
                case "recapp":
                    self.client = MongoClient(config['db_host'], config['db_port'])
                    self.db = self.client[config['recapp_db_name']]
                    self.collection = self.db[config['req_collection']]
                case "whisper":
                    self.client = MongoClient(config['db_host'], config['db_port'])
                    self.db = self.client[config['transcript_db']]
                    self.collection = self.db[config['transcript_collection']]
                case "vosk":
                    self.client = MongoClient(config['db_host'], config['db_port'])
                    self.db = self.client[config['transcript_db']]
                    self.collection = self.db[config['transcript_collection']]
                case "metrics":
                    self.client = MongoClient(config['db_host'], config['db_port'])
                    self.db = self.client[config['transcript_db']]
                    self.collection = self.db[config['transcript_collection']]
                case _:
                    self.client = MongoClient(config['db_host'], config['db_port'])
        except ConnectionFailure:
            print(f"Error while connecting to MongoDB Instance")
        # Catch any other exceptions
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            self.client = None
            self.db = None
            self.collection = None

    def getSingleItemByID(self, searchString: str):
        """Find single Item in collection based on search string.

        Args:
            searchString (str): Filter Criteria to query Collection

        Returns:
            dict: Database Object
        """
        try:
            res = self.collection.find_one(searchString)
            print("Found matching item in Collection.")
            return res
        except PyMongoError as e:
            print (f"Error finding item: {e}")
            return None
        except Exception as e:  
            # Catch any other exceptions
            print(f"An unexpected error occurred: {e}")
            return None
        
    def getAllItems(self):
        """Returns all items in collection

        Returns:
            list: A list of dictionaries containing all items in collection
        """
        try:
            res = self.collection.find()
            return res
        except PyMongoError as e:
            print (f"Error finding item: {e}")
            return None
        except Exception as e:  
            # Catch any other exceptions
            print(f"An unexpected error occurred: {e}")
            return None
        
    def addNewItem(self, newItem: dict):
        """Add new item to Collection.

        Args:
            newItem (dict): New Object to Add

        Returns:
            str: ID of the inserted Item as string.
        """
        try:
            print("Adding new item")
            res = self.collection.insert_one(newItem)
            print(f"Added item with ID {res.inserted_id}")
            return str(res.inserted_id)
        except PyMongoError as e:
            print(f"Error adding item: {e}")
            return None
        # Catch any other exceptions
        except Exception as e:  
            print(f"An unexpected error occurred: {e}")
            return None
   
    def updateItem (self, searchString: dict, newValues: dict):
        """Update a Item in the collection.

        Args:
            searchString (str): Filter Criteria to query Collection
            newValues (dict): New values to set

        Returns:
            bool: Has an item been updated or not.
        """
        
        try:
            res = self.collection.update_one(searchString, newValues)
            if res.modified_count > 0:
                print(f"Update for '{searchString}' successful.")
                return True
            else:
                print("No item updated.")
                return False
        except PyMongoError as e:
            print (f"Error updating item: {e}")
            return None
        except Exception as e:  
            # Catch any other exceptions
            print(f"An unexpected error occurred: {e}")
            return None
                    
    def disconnectMongoDB(self):
        """Disconnects the current MongoDB Connection

        Returns:
            Nothing
        """
        self.client.close()
    
    def searchByQuery(self, query):
        """Search multiple items in collection matching the query

        Args:
            query (dict): Query to search collection

        Returns:
            cursor: A cursor containing all items in collection
        """
        try:
            res = self.collection.find(query)
            print("Found matching items in Collection.")
            return res
        except PyMongoError as e:
            print (f"Error finding item: {e}")
            return None
        except Exception as e:  
            # Catch any other exceptions
            print(f"An unexpected error occurred: {e}")
            return None
    
    def getAllItemsFromTemp(self):
        """Returns all items in temporary collection

        Returns:
            list: A list of dictionaries containing all items in temporary collection
        """
        try:
            res = self.temp_collection.find()
            return res
        except PyMongoError as e:
            print (f"Error finding item: {e}")
            return None
        except Exception as e:  
            # Catch any other exceptions
            print(f"An unexpected error occurred: {e}")
            return None
    
    # Getters
    def getClient(self):
        """
        Get the MongoDB database instance.

        Returns:
            Database: The MongoDB database instance.
        """
        return self.client
    
    def getDB(self):
        """
        Get the MongoDB database instance.

        Returns:
            Database: The MongoDB database instance.
        """
        return self.db
    
    def getCollection(self):
        """
        Get the MongoDB collection instance.

        Returns:
            Collection: The MongoDB collection instance.
        """
        return self.collection
    
    def getTempDB(self):
        """
        Get the temporary MongoDB database instance.

        Returns:
            Database: The temporary MongoDB database instance.
        """
        return self.temp_db
    
    def getTempCollection(self):
        """
        Get the temporary MongoDB collection instance.

        Returns:
            Collection: The temporary MongoDB collection instance.
        """
        return self.temp_collectioncollection
    
    # Setter
    def setClient (self, client: MongoClient):
        """Set a new MongoDB Client Instance

        Args:
            client (MongoClient): New MongoDB Client
        """
        if isinstance(client, MongoClient):
            self.client = client
            print("Client set successfully.")
        else:
            print("Error: Provided client is not a valid MongoClient instance.")
    
    def setDB (self, dbName: str):
        """Set a new MongoDB Database Instance

        Args:
            dbName (str): New Database Name
        """
        if isinstance(dbName, str) and dbName:
            self.db = self.client[dbName]
            print(f"MongoDB database '{dbName}' set successfully.")
        else:
            print("Error: Provided db_name is invalid.")
            
    def setCollection(self, collectionName: str):
        """Set a new MongoDB collection instance.

        Args:
            collectionName (str): Name of the Collection
        """
        if isinstance(collectionName, str) and collectionName:
            self.collection = self.db[collectionName]
            print(f"MongoDB collection '{collectionName}' set successfully.")
        else:
            print("Error: Provided collection_name is invalid.")
            
    def setTempDB (self, dbName: str):
        """Set a new temporary MongoDB Database Instance to enable data transfer

        Args:
            dbName (str): New Temporary Database Name
        """
        if isinstance(dbName, str) and dbName:
            self.temp_db = self.client[dbName]
            print(f"Temporary MongoDB database '{dbName}' set successfully.")
        else:
            print("Error: Provided db_name is invalid.")
            
    def setTempCollection(self, collectionName: str):
        """Set a new temporary MongoDB collection instance to enable data transfer.

        Args:
            collectionName (str): Name of the temporary Collection
        """
        if isinstance(collectionName, str) and collectionName:
            self.temp_collection = self.temp_db[collectionName]
            print(f"Temporary MongoDB collection '{collectionName}' set successfully.")
        else:
            print("Error: Provided collection_name is invalid.")