from fastapi import APIRouter, Depends, HTTPException, Form, Path, Query
from datetime import datetime
from bson import ObjectId
from database import get_db
from models import PostBase

router = APIRouter(prefix="/post", tags=["Post"])

@router.post("/create-json")
def create_one_post_json(post: PostBase, db=Depends(get_db)):
    try:
        new_post = {
            "title": post.title,
            "content": post.content,
            "created": datetime.utcnow()
        }
        result = db["post"].insert_one(new_post)
        created_post = db["post"].find_one({"_id": result.inserted_id})
        return {
            "id": str(created_post["_id"]),
            "title": created_post["title"],
            "content": created_post["content"],
            "created": created_post["created"].isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando post: {e}")

@router.post("/create-form")
def create_one_post_form(
    title: str = Form(..., min_length=1, max_length=20),
    content: str = Form(..., min_length=1, max_length=255),
    db=Depends(get_db)
):
    try:
        new_post = {
            "title": title,
            "content": content,
            "created": datetime.utcnow()
        }
        result = db["post"].insert_one(new_post)
        created_post = db["post"].find_one({"_id": result.inserted_id})
        return {
            "id": str(created_post["_id"]),
            "title": created_post["title"],
            "content": created_post["content"],
            "created": created_post["created"].isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando post: {e}")

@router.get("/")
def get_all_posts(db=Depends(get_db)):
    try:
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo posts: {e}")

@router.get("/buscar")
def buscar_posts(
    titulo: str | None = Query(None, min_length=1, max_length=255),
    db=Depends(get_db)
):
    try:
        filtro = {"title": {"$regex": titulo, "$options": "i"}}
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error buscando posts: {e}")

@router.get("/{post_id}")
def get_one_post(
    post_id: str = Path(..., min_length=24, max_length=24, regex="^[0-9a-fA-F]{24}$"),
    db=Depends(get_db)
):
    try:
        post = db["post"].find_one({"_id": ObjectId(post_id)})
        if not post:
            raise HTTPException(status_code=404, detail="Post no encontrado")
        return {
            "id": str(post["_id"]),
            "title": post["title"],
            "content": post["content"],
            "created": post["created"].isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo post: {e}")

@router.patch("/edit/{post_id}")
def edit_one_post(post_id: str, post: PostBase, db=Depends(get_db)):
    try:
        existing_post = db["post"].find_one({"_id": ObjectId(post_id)})
        if not existing_post:
            raise HTTPException(status_code=404, detail="Post no encontrado")

        updated_data = {"title": post.title, "content": post.content}
        db["post"].update_one({"_id": ObjectId(post_id)}, {"$set": updated_data})

        updated_post = db["post"].find_one({"_id": ObjectId(post_id)})
        return {
            "id": str(updated_post["_id"]),
            "title": updated_post["title"],
            "content": updated_post["content"],
            "created": updated_post["created"].isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error editando post: {e}")

@router.delete("/delete/{post_id}")
def delete_one_post(post_id: str, db=Depends(get_db)):
    try:
        post = db["post"].find_one({"_id": ObjectId(post_id)})
        if not post:
            raise HTTPException(status_code=404, detail="Post no encontrado")
        db["post"].delete_one({"_id": ObjectId(post_id)})
        return {"message": "Post eliminado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error eliminando post: {e}")