from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.index import modelo

app = FastAPI(tittle='Autenticación para todos', description='Hackathon BBVA',version='1.0.0')

origins = [
    '*',
    "http://localhost",
    "http://localhost:8080",
    "https://localhost",
    "https://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(modelo)