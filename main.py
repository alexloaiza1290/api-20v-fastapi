from fastapi import FastAPI, Depends, HTTPException
from pymongo import MongoClient
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from bson import ObjectId

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    client = MongoClient("mongodb+srv://jorgeav527:jorgimetro527@cluster0.mn8kdim.mongodb.net/")
    try:
        db = client["api-20v"]
        yield db
    finally:
        client.close()


class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=20)
    content: str = Field(..., min_length=1, max_length=255)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/post/create-json-data")
def create_one_post_json_data(post: PostBase, db=Depends(get_db)):
    new_post = {
        "title": post.title,
        "content": post.content,
        "created": datetime.now()
    }
    result = db["post"].insert_one(new_post)
    created_post = db["post"].find_one({"_id": result.inserted_id})
    return {
        "id": str(created_post["_id"]),
        "title": created_post["title"],
        "content": created_post["content"],
        "created": created_post["created"].isoformat()
    }

@app.get("/post")
def get_all_post(db=Depends(get_db)):
    posts = []
    post_list = db["post"].find()
    for post in post_list:
        posts.append({
        "id": str(post["_id"]),
        "title": post["title"],
        "content": post["content"],
        "created": post["created"].isoformat()
    })
    return posts

@app.get("/post/{post_id}")
def get_one_post(post_id: str, db=Depends(get_db)):
    post = db["post"].find_one({"_id": ObjectId(post_id)})
    return {
        "id": str(post["_id"]),
        "title": post["title"],
        "content": post["content"],
        "created": post["created"].isoformat()
    }

@app.put("/post/edit/{post_id}")
def edit_one_post(post_id: str, post: PostBase, db=Depends(get_db)):
    existing_post = db["post"].find_one({"_id": ObjectId(post_id)})
    if not existing_post:
        raise HTTPException(status_code=404, detail="el objeto no existe")

    updated_data = {
        "title": post.title,
        "content": post.content
    }
    db["post"].update_one({"_id": ObjectId(post_id)}, {"$set": updated_data})
    updated_post = db["post"].find_one({"_id": ObjectId(post_id)})
    return {
        "id": str(updated_post["_id"]),
        "title": updated_post["title"],
        "content": updated_post["content"],
        "created": updated_post["created"].isoformat()
    }

@app.delete("/post/delete/{post_id}")
def delete_one_post(post_id: str, db=Depends(get_db)):
    post = db["post"].find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="el objeto no existe")
    db["post"].delete_one({"_id": ObjectId(post_id)})
    return {"message": "Post deleted successfully"}