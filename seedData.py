from pymongo import MongoClient
from scrapeJobs import scrape_jobs

# Another idea, add some logic that checks if the job is already in the db, if so skip else insert it.
# initial jobs
initial_jobs = scrape_jobs()

# connection
try:
    client = MongoClient(host='localhost', port=27017)
    client.server_info()
    db = client['projectPrototype']
    collection = db['protoCollection']
except Exception as e:
    print(e)
    print(f"{e} Can't connect to db")


def seed_database():
    try:
        if collection.count_documents({}) == 0:
            result = collection.insert_many(initial_jobs)
            print(f"Jobs inserted: {result.inserted_ids}")
        else:
            print("protoCollection already has data, skipping seeding.")
    except Exception as ex:
        print(f"An error occurred: {ex}")


if __name__ == "__main__":
    seed_database()
