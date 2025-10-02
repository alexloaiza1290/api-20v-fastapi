from fastapi import FastAPI, Depends, HTTPException, Path, Query, Form, Header, Response, Cookie
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
    client = MongoClient("mongodb+srv://jorgeav527:jorgimetro527@cluster0.mn8kdim.mongodb.net/",
    tls=True,
    tlsAllowInvalidCertificates=True)
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
    return {"Hello": "Alumnos"}

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

@app.post("/post/create-form-data")
def create_one_post_form_data(
        title: str = Form(..., min_length=1, max_length=20),
        content: str = Form(..., min_length=1, max_length=255),
        db=Depends(get_db)
    ):
    new_post = {
        "title": title,
        "content": content,
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

@app.get("/post/buscar")
def buscar_post(
    titulo: str | None = Query(None, min_length=1, max_length=255, title="titulo del post"),
    db=Depends(get_db)
    ):
    filtro = {"title": {"$regex": titulo, "$options": "i"} }

    posts = []
    post_list = db["post"].find(filtro)
    for post in post_list:
        posts.append({
        "id": str(post["_id"]),
        "title": post["title"],
        "content": post["content"],
        "created": post["created"].isoformat()
    })
    return posts

@app.get("/post/{post_id}")
def get_one_post(
        post_id: str = Path(
                title="Id del post", 
                min_length=24, 
                max_length=24,
                regex="^[0-9a-fA-F]{24}$"
            ), 
        db=Depends(get_db)
    ):
    post = db["post"].find_one({"_id": ObjectId(post_id)})
    return {
        "id": str(post["_id"]),
        "title": post["title"],
        "content": post["content"],
        "created": post["created"].isoformat()
    }

@app.patch("/post/edit/{post_id}")
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


@app.get("/posts/secure/")
def obtener_posts_secure(
        authorization: str = Header(..., alias="Authorization", description="Token en formato 'Bearer <token>'"),
        db=Depends(get_db)
    ):
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=400,
            detail="Formato de token inválido. Use 'Bearer <token>'"
        )
    
    token = authorization[7:]

    if token != "secreto123":
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
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

@app.get("/set-cookie")
def set_cookie(response: Response):
    response.set_cookie(key="user_id", value="123456")
    return {"message": "Cookie creada!"}

@app.get("/get-cookie")
def get_cookie(user_id: str | None = Cookie(None)):
    return { "value": user_id }

@app.get("/del-cookie/")
def clear_cookie(response: Response):
    response.delete_cookie("user_id")
    return {"message": "Cookie de posts eliminada"}