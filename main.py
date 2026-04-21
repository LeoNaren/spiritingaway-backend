from fastapi import FastAPI, HTTPException, Header
import firebase_admin
from firebase_admin import credentials, auth

#Initialize firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Spiritng Away Backend is live"}

@app.get("/me")
def get_me(authorization: str = Header(...)):
    try:
        token = authorization.replace("Bearer ", "")
        decoded_token = auth.verify_id_token(token)
        return {"uid": decoded_token["uid"], "email": decoded_token.get("email")}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid or expired token")