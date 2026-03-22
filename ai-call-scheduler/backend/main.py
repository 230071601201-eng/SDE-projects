from fastapi import FastAPI
from model import calculate_priority

app = FastAPI()

calls = []

@app.post("/add_call")
def add_call(call: dict):
    priority = calculate_priority(call)
    call["priority"] = priority
    calls.append(call)
    return {"message": "Call added", "priority": priority}


@app.get("/get_calls")
def get_calls():
    sorted_calls = sorted(calls, key=lambda x: x["priority"], reverse=True)
    return sorted_calls

@app.get("/")
def home():
    return {"message": "AI Call Scheduler API is running"}