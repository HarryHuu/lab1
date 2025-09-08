from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from typing import List
from pathlib import Path
import json

app = FastAPI()

# --- paths & templates ---
BASE_DIR = Path(__file__).resolve().parent
USERS_PATH = BASE_DIR / "users.json"
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# --- helpers to load/save users ---
def load_users() -> List[dict]:
    with USERS_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data["users"]

def save_users(users: List[dict]) -> None:
    with USERS_PATH.open("w", encoding="utf-8") as f:
        json.dump({"users": users}, f, ensure_ascii=False, indent=2)

# --- Pydantic model for validation ---
class User(BaseModel):
    name: str = Field(..., min_length=1)
    phone: int
    fave_color: str

# --------------------
# Lab endpoints (keep)
# --------------------
@app.get("/")
def read_root():
    return {"message": "Welcome to this fantastic app!"}

@app.get("/users")
def get_users_lab_style():
    # Lab’s original way (reads as string then json.loads)
    with open(USERS_PATH, "r", encoding="utf-8") as file:
        file_contents = "".join(file.readlines())
        data = json.loads(file_contents)
    return data

# --------------------
# DIY JSON CRUD
# --------------------
# List (clean version)
@app.get("/users2", response_model=List[User])
def list_users():
    return load_users()

# Get one by name
@app.get("/users/{name}", response_model=User)
def get_user(name: str):
    for u in load_users():
        if u["name"].lower() == name.lower():
            return u
    raise HTTPException(status_code=404, detail=f"User '{name}' not found")

# Create
@app.post("/users", response_model=User, status_code=201)
def create_user(user: User):
    users = load_users()
    if any(u["name"].lower() == user.name.lower() for u in users):
        raise HTTPException(status_code=409, detail="User with that name already exists")
    users.append(user.model_dump())
    save_users(users)
    return user

# Update (replace by name)
@app.put("/users/{name}", response_model=User)
def update_user(name: str, user: User):
    users = load_users()
    for i, u in enumerate(users):
        if u["name"].lower() == name.lower():
            users[i] = user.model_dump()
            save_users(users)
            return users[i]
    raise HTTPException(status_code=404, detail=f"User '{name}' not found")

# Delete
@app.delete("/users/{name}", status_code=204)
def delete_user(name: str):
    users = load_users()
    new_users = [u for u in users if u["name"].lower() != name.lower()]
    if len(new_users) == len(users):
        raise HTTPException(status_code=404, detail=f"User '{name}' not found")
    save_users(new_users)
    return None

# --------------------
# Optional: HTML view
# --------------------
@app.get("/users/html", response_class=HTMLResponse)
def users_html(request: Request):
    return templates.TemplateResponse(
        "users.html",
        {"request": request, "users": load_users()}
    )
