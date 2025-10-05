from fastapi import FastAPI, Response, Cookie
from fastapi.middleware.cors import CORSMiddleware
from post import router as post_router

app = FastAPI(title="API 20v con FastAPI y MongoDB")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "API FastAPI funcionando correctamente"}

@app.get("/set-cookie")
def set_cookie(response: Response):
    response.set_cookie(key="user_id", value="123456", httponly=True)
    return {"message": "Cookie creada!"}

@app.get("/get-cookie")
def get_cookie(user_id: str | None = Cookie(None)):
    return {"cookie_user_id": user_id}

@app.get("/del-cookie")
def clear_cookie(response: Response):
    response.delete_cookie("user_id")
    return {"message": "Cookie eliminada"}

app.include_router(post_router)
