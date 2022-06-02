import mlflow 
import uvicorn
import json
import pandas as pd 
from pydantic import BaseModel
from typing import Literal, List, Union
from fastapi import FastAPI, File, UploadFile
import boto3
import pickle


description = """

# API documentation for Project Get Around

"""

mlflow.set_tracking_uri("https://mlflow-getaround.herokuapp.com/")


tag_metadata = [
    {
        "name": "Machine Learning",
        "description": "Endpoints that uses our Machine Learning model for predicting car rental price per day"
    }
]

app = FastAPI(
    title="My GetAround API",
    description=description,
    version="0.1",
    contact={
        "name": "GetAround",
        "url": "https://mlflow-getaround.herokuapp.com/",
    },
    openapi_tags=tag_metadata
)

class PredictionFeatures(BaseModel):
    model_key: str = "Citroën"
    mileage: int = 140411
    engine_power: int = 100
    fuel: str = "diesel"
    paint_color: str = "black"
    car_type: str = "convertible"
    private_parking_available: bool = True
    has_gps: bool = True
    has_air_conditioning: bool = False
    automatic_car: bool = False
    has_getaround_connect: bool = True
    has_speed_regulator: bool = True
    winter_tires: bool = True


@app.get("/")
async def index():

    message = "Hello this is my own API. If you want to learn more, check out documentation of the api at `/docs`"

    return message

@app.post("/predict", tags=["Machine Learning"])
async def predict(predictionFeatures: PredictionFeatures):
    """
    Prediction of rental price per day for a car
    """
    # Read data 
    car_price = pd.DataFrame(dict(predictionFeatures), index=[0])
    # # Log model from mlflow 
    logged_model = 'runs:/f7d5061de4e74c6fa52c91d76f522bfa/car_price_estimator'

    # Load model as a PyFuncModel.
    loaded_model = mlflow.pyfunc.load_model(logged_model)
    prediction = loaded_model.predict(car_price)

    # Format response
    response = {"prediction": prediction.tolist()[0]}
    return response

if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000, debug=True, reload=True) # Here you define your web server to run the `app` variable (which contains FastAPI instance), with a specific host IP (0.0.0.0) and port (4000)