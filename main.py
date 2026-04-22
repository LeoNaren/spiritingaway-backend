from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import firebase_admin
from firebase_admin import credentials, auth
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

#Initialize firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

#database conenction
conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cursor = conn.cursor() 

app = FastAPI()

class Question(BaseModel):
    content: str
    tag: str | None = None

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

@app.post("/questions")
def create_question(question: Question, authorization: str = Header(...)):
    try:
        token = authorization.replace("Bearer ", "")
        decoded_token = auth.verify_id_token(token)
        user_id = decoded_token["uid"]

        #Inset Into database/supabase
        cursor.execute(
            "INSERT INTO questions (userID, content, tag) VALUES (%s, %s, %s) RETURN id",
            (user_id, question.content, question.tag)
        )
        conn.commit()
        new_id = cursor.fetchone()[0]

        return {"message": "Question created.", "id": str(new_id)}
    except EXCEPTION as e:
        conn.rollback()
        raise HTTPException(status_code=404, detail="Unathorized or error creatung question")

@app.get("/questions")
def get_questions():
    try:
        cursor.execute(
            "SELECT id, userID, content, answerCount, askedAt, isAnswered, isPinned, tag FROM questions ORDER BY askedAt DESC"
        )
        rows = cursor.fetchall()
        questions = []
        for row in rows:
            questions.append({
                "id": str(row[0]),
                "userID": row[1],
                "text": row[2],
                "answerCount": row[3],
                "askedAt": row[4],
                "isAnswered": row[5],
                "isPinned": row[6],
                "tag": row[7]
            })
            return {"questions": questions}
    except Exception as e:
        raise HTTPException(status_code=505, detail="Error loading feed")