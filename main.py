from fastapi import FastAPI, HTTPException
from typing import List
from pydantic import BaseModel
from passlib.context import CryptContext
import jwt

class Payload(BaseModel):
    numbers: List[int]

class BinarySearchPayload(BaseModel):
    numbers: List[int]
    target: int

class UserCredentials(BaseModel): 
    username: str
    password: str

# Mock db
users_db = {} 

app = FastAPI()

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Token verify method
def get_current_user(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None or username not in users_db:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return username
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

# Register user
@app.post("/register")
def register(user: UserCredentials):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = pwd_context.hash(user.password)
    users_db[user.username] = {"password": hashed_password}
    return {"message": "User registered successfully"}

# Login user
@app.post("/login")
def login(user: UserCredentials):
    db_user = users_db.get(user.username)
    if not db_user or not pwd_context.verify(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token}

# Bubble Sort
@app.post("/bubble-sort")
def bubble_sort(payload: Payload, token: str):
    get_current_user(token)  # Verify token
    numbers = payload.numbers
    n = len(numbers)
    for i in range(n):
        for j in range(0, n-i-1):
            if numbers[j] > numbers[j+1]:
                numbers[j], numbers[j+1] = numbers[j+1], numbers[j]
    return {"numbers": numbers} 

# Filtro de Pares
@app.post("/filter-even")
def filter_even(payload: Payload, token: str):
    get_current_user(token)  # Verify token
    numbers = payload.numbers
    even_numbers = [number for number in numbers if number % 2 == 0]
    return {"even_numbers": even_numbers}


# Suma de Elementos
@app.post("/sum-elements")
def sum_elements(payload: Payload, token: str):
    get_current_user(token)  # Verify token
    numbers = payload.numbers
    return {"sum": sum(numbers)}


# Máximo Valor
@app.post("/max-value")
def max_value(payload: Payload, token: str):
    get_current_user(token)  # Verify token
    numbers = payload.numbers
    return {"max": max(numbers)}


# Búsqueda Binaria
@app.post("/binary-search")
def binary_search(payload: BinarySearchPayload, token: str):
    get_current_user(token)  # Verify token
    numbers = payload.numbers
    target = payload.target

    left, right = 0, len(numbers) - 1
    while left <= right:
        mid = (left + right) // 2
        if numbers[mid] == target:
            return {"found": True, "index": mid}
        elif numbers[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return {"found": False, "index": -1}
