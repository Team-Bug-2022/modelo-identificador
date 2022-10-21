from fastapi import APIRouter, File, UploadFile

modelo = APIRouter()

@modelo.get("/")
def read_something():
    return {"msg":"Hola mundo"}