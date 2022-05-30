import mlflow 
import uvicorn
import json
import pandas as pd 
from pydantic import BaseModel
from typing import Literal, List, Union
from fastapi import FastAPI, File, UploadFile


description = """

# API documentation for Project Get Around

"""

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
        "url": "https://get-around-mlflow.herokuapp.com/",
    },
    openapi_tags=tag_metadata
)

class PredictionFeatures(BaseModel):
    model_key: str
    mileage: int
    engine_power: int
    fuel: str
    paint_color: str
    car_type: str
    private_parking_available: bool
    has_gps: bool
    has_air_conditioning: bool
    automatic_car: bool
    has_getaround_connect: bool
    has_speed_regulator: bool
    winter_tires: bool


@app.get("/")
async def index():

    message = "Hello this is my test API. If you want to learn more, check out documentation of the api at `/docs`"

    return message

@app.post("/predict", tags=["Machine Learning"])
async def predict(predictionFeatures: PredictionFeatures):
    """
    Prediction of rental price per day for a car
    """
    import pandas as pd 
    # Read data 
    car_price = pd.DataFrame(dict(predictionFeatures), index=[0])

    # # Log model from mlflow 
    logged_model = 'runs:/b20787929fb445e3ad0574ad722657d4/car_price_estimator'

    # Load model as a PyFuncModel.
    loaded_model = mlflow.pyfunc.load_model(logged_model)
    prediction = loaded_model.predict(car_price)

    # Format response
    response = {"prediction": prediction.tolist()[0]}
    return response



if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000, debug=True, reload=True) # Here you define your web server to run the `app` variable (which contains FastAPI instance), with a specific host IP (0.0.0.0) and port (4000)