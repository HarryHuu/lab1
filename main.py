from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from typing import List, Optional
from pathlib import Path
import json

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
# Part 1: Root

@app.get("/")
def read_root():
    return {"message": "Welcome to this fantastic app!"}

# read
USERS_PATH = BASE_DIR / "users.json"
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# load/save users ---
def load_users() -> List[dict]:
    with USERS_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    # lab's users.json is { "users": [...] }
    return data["users"]

def save_users(users: List[dict]) -> None:
    with USERS_PATH.open("w", encoding="utf-8") as f:
        json.dump({"users": users}, f, ensure_ascii=False, indent=2)

class User(BaseModel):
    name: str = Field(..., min_length=1)
    phone: int
    fave_color: str

@app.get("/users")
def get_users_lab_style():
    with open(USERS_PATH, "r", encoding="utf-8") as file:
        file_contents = "".join(file.readlines())
        data = json.loads(file_contents)
    return data




# Jinja2
@app.get("/users/html", response_class=HTMLResponse)
def users_html(request: Request):
    return templates.TemplateResponse(
        "users.html",
        {"request": request, "users": load_users()}
    )


@app.get("/users2", response_model=List[User])
def list_users():
    return load_users()

@app.get("/users/{name}", response_model=User)
def get_user(name: str):
    for u in load_users():
        if u["name"].lower() == name.lower():
            return u
    raise HTTPException(status_code=404, detail=f"User '{name}' not found")

@app.post("/users", response_model=User, status_code=201)
def create_user(user: User):
    users = load_users()
    if any(u["name"].lower() == user.name.lower() for u in users):
        raise HTTPException(status_code=409, detail="User with that name already exists")
    users.append(user.model_dump())
    save_users(users)
    return user

@app.put("/users/{name}", response_model=User)
def update_user(name: str, user: User):
    users = load_users()
    for i, u in enumerate(users):
        if u["name"].lower() == name.lower():
            users[i] = user.model_dump()
            save_users(users)
            return users[i]
    raise HTTPException(status_code=404, detail=f"User '{name}' not found")

@app.delete("/users/{name}", status_code=204)
def delete_user(name: str):
    users = load_users()
    new_users = [u for u in users if u["name"].lower() != name.lower()]
    if len(new_users) == len(users):
        raise HTTPException(status_code=404, detail=f"User '{name}' not found")
    save_users(new_users)
    return None


#DIY part


MOVIES_PATH = BASE_DIR / "movie_data.json"

def _read_movies_raw():
    with MOVIES_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)

def load_movies() -> List[dict]:
    raw = _read_movies_raw()
    if isinstance(raw, dict) and "results" in raw:
        return raw["results"]
    return raw  

def save_movies(movies: List[dict]) -> None:
    raw = _read_movies_raw()
    if isinstance(raw, dict) and "results" in raw:
        raw["results"] = movies
        with MOVIES_PATH.open("w", encoding="utf-8") as f:
            json.dump(raw, f, ensure_ascii=False, indent=2)
    else:
        with MOVIES_PATH.open("w", encoding="utf-8") as f:
            json.dump(movies, f, ensure_ascii=False, indent=2)

class Movie(BaseModel):
    id: int
    title: str
    overview: str
    release_date: str
    vote_average: float
    vote_count: int
    popularity: float
    genre_ids: List[int]
    original_title: Optional[str] = None
    original_language: Optional[str] = None
    adult: Optional[bool] = False
    video: Optional[bool] = False
    media_type: Optional[str] = None
    backdrop_path: Optional[str] = None
    poster_path: Optional[str] = None

@app.get("/movies", response_model=List[Movie])
def movies_list():
    return load_movies()

@app.get("/movies/{movie_id}", response_model=Movie)
def movies_get(movie_id: int):
    for m in load_movies():
        if m.get("id") == movie_id:
            return m
    raise HTTPException(status_code=404, detail=f"Movie with id {movie_id} not found")

@app.post("/movies", response_model=Movie, status_code=201)
def movies_create(movie: Movie):
    movies = load_movies()
    if any(m.get("id") == movie.id for m in movies):
        raise HTTPException(status_code=409, detail="Movie with this ID already exists")
    movies.append(movie.model_dump())
    save_movies(movies)
    return movie

@app.put("/movies/{movie_id}", response_model=Movie)
def movies_update(movie_id: int, movie: Movie):
    movies = load_movies()
    for i, m in enumerate(movies):
        if m.get("id") == movie_id:
            movies[i] = movie.model_dump()
            save_movies(movies)
            return movies[i]
    raise HTTPException(status_code=404, detail=f"Movie with id {movie_id} not found")

@app.delete("/movies/{movie_id}", status_code=204)
def movies_delete(movie_id: int):
    movies = load_movies()
    new_movies = [m for m in movies if m.get("id") != movie_id]
    if len(new_movies) == len(movies):
        raise HTTPException(status_code=404, detail=f"Movie with id {movie_id} not found")
    save_movies(new_movies)
    return None
