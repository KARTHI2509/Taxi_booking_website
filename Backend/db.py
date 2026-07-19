from pymongo import MongoClient
from dotenv import load_dotenv
import os
import sqlite3
import json
import re
import uuid

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "").strip()
DATABASE_NAME = os.getenv("DATABASE_NAME", "taxi_booking_db")

# Result helper classes to emulate PyMongo return values
class InsertOneResult:
    def __init__(self, inserted_id):
        self.inserted_id = inserted_id

class UpdateResult:
    def __init__(self, matched_count, modified_count):
        self.matched_count = matched_count
        self.modified_count = modified_count

class DeleteResult:
    def __init__(self, deleted_count):
        self.deleted_count = deleted_count

class SQLiteCollection:
    def __init__(self, db_path, collection_name):
        self.db_path = db_path
        self.collection_name = collection_name
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS document_store (
                    collection_name TEXT,
                    doc_id TEXT,
                    doc_json TEXT,
                    PRIMARY KEY (collection_name, doc_id)
                )
            """)
            conn.commit()

    def _get_all_docs(self):
        docs = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT doc_json FROM document_store WHERE collection_name = ?",
                (self.collection_name,)
            )
            rows = cursor.fetchall()
            for row in rows:
                docs.append(json.loads(row[0]))
        return docs

    def _save_doc(self, doc_id, doc):
        doc_json = json.dumps(doc)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO document_store (collection_name, doc_id, doc_json)
                VALUES (?, ?, ?)
                """,
                (self.collection_name, str(doc_id), doc_json)
            )
            conn.commit()

    def _delete_doc(self, doc_id):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "DELETE FROM document_store WHERE collection_name = ? AND doc_id = ?",
                (self.collection_name, str(doc_id))
            )
            conn.commit()

    def _matches(self, doc, query):
        if not query:
            return True
        
        for key, val in query.items():
            if key == "$or":
                # val is a list of sub-queries
                matched_any = False
                for sub_query in val:
                    if self._matches(doc, sub_query):
                        matched_any = True
                        break
                if not matched_any:
                    return False
            else:
                doc_val = doc.get(key)
                if isinstance(val, dict):
                    if "$regex" in val:
                        pattern = val["$regex"]
                        options = val.get("$options", "")
                        flags = re.IGNORECASE if "i" in options else 0
                        if doc_val is None:
                            return False
                        if not re.search(pattern, str(doc_val), flags):
                            return False
                    # Extend other operators if needed
                else:
                    if doc_val != val:
                        return False
        return True

    def find(self, query=None, projection=None):
        docs = self._get_all_docs()
        matched = []
        for doc in docs:
            if self._matches(doc, query):
                # Apply projection
                doc_copy = dict(doc)
                if projection:
                    for pk, pv in projection.items():
                        if pv == 0 and pk in doc_copy:
                            doc_copy.pop(pk, None)
                matched.append(doc_copy)
        return matched

    def find_one(self, query=None, projection=None, sort=None):
        docs = self._get_all_docs()
        matched = []
        for doc in docs:
            if self._matches(doc, query):
                matched.append(doc)
        
        if not matched:
            return None

        # Apply sort
        # sort parameter is usually a list of tuples, e.g. [("customer_id", -1)]
        if sort:
            for sort_key, direction in reversed(sort):
                reverse = True if direction == -1 else False
                # Sort handling default values gracefully
                matched.sort(key=lambda x: x.get(sort_key) if x.get(sort_key) is not None else 0, reverse=reverse)

        selected = matched[0]
        # Apply projection
        selected_copy = dict(selected)
        if projection:
            for pk, pv in projection.items():
                if pv == 0 and pk in selected_copy:
                    selected_copy.pop(pk, None)
        return selected_copy

    def insert_one(self, document):
        # Generate an ID if not present
        doc = dict(document)
        if "_id" not in doc:
            doc["_id"] = uuid.uuid4().hex
        
        # Determine logical ID field
        id_field = "_id"
        for potential_id in ["customer_id", "driver_id", "vehicle_id", "booking_id", "payment_id"]:
            if potential_id in doc:
                id_field = potential_id
                break

        doc_id = doc[id_field]
        self._save_doc(doc_id, doc)
        return InsertOneResult(doc_id)

    def update_one(self, query, update):
        # We need to find the first matching document, update it, and save it
        docs = self._get_all_docs()
        matched_doc = None
        for doc in docs:
            if self._matches(doc, query):
                matched_doc = doc
                break
        
        if not matched_doc:
            return UpdateResult(0, 0)
        
        # Apply update (e.g. {"$set": {...}})
        if "$set" in update:
            for k, v in update["$set"].items():
                matched_doc[k] = v

        # Determine doc_id
        id_field = "_id"
        for potential_id in ["customer_id", "driver_id", "vehicle_id", "booking_id", "payment_id"]:
            if potential_id in matched_doc:
                id_field = potential_id
                break

        doc_id = matched_doc[id_field]
        self._save_doc(doc_id, matched_doc)
        return UpdateResult(1, 1)

    def delete_one(self, query):
        docs = self._get_all_docs()
        deleted_count = 0
        for doc in docs:
            if self._matches(doc, query):
                id_field = "_id"
                for potential_id in ["customer_id", "driver_id", "vehicle_id", "booking_id", "payment_id"]:
                    if potential_id in doc:
                        id_field = potential_id
                        break
                self._delete_doc(doc[id_field])
                deleted_count = 1
                break
        return DeleteResult(deleted_count)

    def delete_many(self, query):
        docs = self._get_all_docs()
        deleted_count = 0
        for doc in docs:
            if self._matches(doc, query):
                id_field = "_id"
                for potential_id in ["customer_id", "driver_id", "vehicle_id", "booking_id", "payment_id"]:
                    if potential_id in doc:
                        id_field = potential_id
                        break
                self._delete_doc(doc[id_field])
                deleted_count += 1
        return DeleteResult(deleted_count)

    def count_documents(self, query):
        docs = self._get_all_docs()
        count = 0
        for doc in docs:
            if self._matches(doc, query):
                count += 1
        return count

# Initialize database connections based on MONGO_URI env variable
use_mongo = False
if MONGO_URI:
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        # Verify connection
        client.server_info()
        db = client[DATABASE_NAME]
        use_mongo = True
        print("Connected to MongoDB Atlas successfully.")
    except Exception as e:
        print(f"MongoDB connection failed: {e}. Falling back to SQLite local database.")

if use_mongo:
    customers_collection = db["customers"]
    drivers_collection = db["drivers"]
    vehicles_collection = db["vehicles"]
    bookings_collection = db["bookings"]
    payments_collection = db["payments"]
else:
    # Use SQLite emulation
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "local_db.sqlite3")
    customers_collection = SQLiteCollection(db_path, "customers")
    drivers_collection = SQLiteCollection(db_path, "drivers")
    vehicles_collection = SQLiteCollection(db_path, "vehicles")
    bookings_collection = SQLiteCollection(db_path, "bookings")
    payments_collection = SQLiteCollection(db_path, "payments")
    print(f"Using SQLite database at {db_path}")
