from typing import List, Optional
from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select, insert, update, delete, func
from sqlalchemy.engine import Engine, Connection
from database import cars_table, engine


app = FastAPI()

def get_db():
    with engine.begin() as conn:
        yield conn


class CarCreate(BaseModel):
    name: str
    model: str
    year: int
    price: float

class CarResponse(CarCreate):
    id: int


@app.get("/cars/", response_model=List[CarResponse], status_code=status.HTTP_200_OK)
async def get_cars(
    id: Optional[int] = None,
    name: Optional[str] = None,
    model: Optional[str] = None,
    year: Optional[int] = None,
    db: Connection = Depends(get_db)
) -> List[CarResponse]:
    if id is not None:
        selected_car = db.execute(select(cars_table).where(cars_table.c.id == id)).mappings().first()
        if selected_car is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
        return [CarResponse(**selected_car)]
    
    if name is not None:
        selected_car = db.execute(select(cars_table).where(func.lower(cars_table.c.name) == func.lower(name))).mappings().first()
        if selected_car is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
        return [CarResponse(**selected_car)]
    
    if model is not None:
        selected_car = db.execute(select(cars_table).where(func.lower(cars_table.c.model) == func.lower(model))).mappings().first()
        if selected_car is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
        return [CarResponse(**selected_car)]
    
    if year is not None:
        selected_cars = db.execute(select(cars_table).where(cars_table.c.year == year)).mappings().fetchall()
        if not selected_cars:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No cars found for the given year")
        return [CarResponse(**car) for car in selected_cars]
    
    selected_cars = db.execute(select(cars_table)).mappings().fetchall()
    return [CarResponse(**car) for car in selected_cars]


@app.post("/cars/", response_model=CarResponse, status_code=status.HTTP_201_CREATED)
async def create_car(car: CarCreate, db: Connection = Depends(get_db)) -> CarResponse:
    db.execute(insert(cars_table).values(**car.dict()))
    new_car = db.execute(select(cars_table).where(
    cars_table.c.name == car.name, cars_table.c.model == car.model
)).mappings().first()

    if new_car is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve the new car")
    return CarResponse(**new_car)


@app.put("/cars/{car_id}", response_model=CarResponse, status_code=status.HTTP_200_OK)
async def update_car(car_id: int, car: CarCreate, db: Connection = Depends(get_db)) -> CarResponse:
    car_to_update = db.execute(select(cars_table).where(cars_table.c.id == car_id)).mappings().first()
    if car_to_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")

    db.execute(update(cars_table).where(cars_table.c.id == car_id).values(**car.dict()))
    updated_car = db.execute(select(cars_table).where(cars_table.c.id == car_id)).mappings().first()
    return CarResponse(**updated_car)


@app.delete("/cars/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_car(car_id: int, db: Connection = Depends(get_db)):
    car_to_delete = db.execute(select(cars_table).where(cars_table.c.id == car_id)).mappings().first()
    if car_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
    db.execute(delete(cars_table).where(cars_table.c.id == car_id))
    return

