import firebase_admin
from firebase_admin import credentials, firestore

def init_db():
    cred = credentials.Certificate("firebase-key.json")
    firebase_admin.initialize_app(cred)
    return firestore.client()

def has_caught(db, user_id, pokemon_id):
    doc_ref = db.collection("users").document(str(user_id)) \
                .collection("pokedex").document(str(pokemon_id))
    doc = doc_ref.get()
    return doc.exists

def add_catch(db, user_id, pokemon_id, pokemon_name):
    user_ref = db.collection("users").document(str(user_id))

    catch_ref = user_ref.collection("pokedex").document(str(pokemon_id))
    catch_ref.set({
        "pokemon_name": pokemon_name,
        "caught_at": firestore.SERVER_TIMESTAMP
    })

    user_ref.set({
        "catch_count": firestore.Increment(1)
    },merge=True)

def get_pokedex(db, user_id):
    catches = db.collection("users").document(str(user_id)).collection("pokedex").stream()

    return sorted([(int(doc.id), doc.to_dict()["pokemon_name"]) 
                   for doc in catches],
                        key=lambda entry: entry[0])

def get_leaderboard(db, limit=10):
    users = db.collection("users").order_by("catch_count", direction=firestore.Query.DESCENDING).limit(limit).stream()
    return [(doc.id, doc.to_dict().get("catch_count", 0)) for doc in users]
