import time
from typing import List
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError

from database import Base, engine, get_db
import models

app = FastAPI()

class LaptopBase(BaseModel):
    marca: str
    modelo: str
    ram_gb: int


class LaptopCreate(LaptopBase):
    pass


class LaptopResponse(LaptopBase):
    id: int
    disponible: bool

    class Config:
        from_attributes = True

@app.on_event("startup")
def startup():
    retries = 10
    while retries > 0:
        try:
            
            Base.metadata.create_all(bind=engine)
            break
        except OperationalError:
            retries -= 1
            print(f"Esperando a MySQL... reintentos restantes: {retries}")
            time.sleep(3)

    db = next(get_db())
    try:
        if db.query(models.Laptop).count() == 0:
            laptops_iniciales = [
                models.Laptop(
                    marca="Dell",
                    modelo="Latitude 5440",
                    ram_gb=16,
                    disponible=True,
                ),
                models.Laptop(
                    marca="Lenovo",
                    modelo="ThinkPad E14",
                    ram_gb=8,
                    disponible=False,
                ),
                models.Laptop(
                    marca="HP",
                    modelo="ProBook 450",
                    ram_gb=16,
                    disponible=True,
                ),
            ]
            db.add_all(laptops_iniciales)
            db.commit()
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"mensaje": "API del laboratorio de cómputo"}


@app.get("/laptops", response_model=List[LaptopResponse])
def get_laptops(db: Session = Depends(get_db)):
    return db.query(models.Laptop).all()

@app.get("/laptops/disponibles", response_model=List[LaptopResponse])
def get_laptops_disponibles(db: Session = Depends(get_db)):
    return db.query(models.Laptop).filter(models.Laptop.disponible == True).all()


@app.get("/laptops/{laptop_id}", response_model=LaptopResponse)
def get_laptop(laptop_id: int, db: Session = Depends(get_db)):
    laptop = (
        db.query(models.Laptop).filter(models.Laptop.id == laptop_id).first()
    )
    if not laptop:
        raise HTTPException(status_code=404, detail="Laptop no encontrada")
    return laptop


@app.post("/laptops", response_model=LaptopResponse, status_code=200)
def create_laptop(laptop_in: LaptopCreate, db: Session = Depends(get_db)):
    nueva_laptop = models.Laptop(
        marca=laptop_in.marca,
        modelo=laptop_in.modelo,
        ram_gb=laptop_in.ram_gb,
        disponible=True,
    )
    db.add(nueva_laptop)
    db.commit()
    db.refresh(nueva_laptop)
    return nueva_laptop