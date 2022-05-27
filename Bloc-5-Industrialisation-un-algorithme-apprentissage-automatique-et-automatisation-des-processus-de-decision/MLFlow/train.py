import mlflow
from mlflow.models.signature import infer_signature
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import  OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import cross_val_score, GridSearchCV

if __name__ == "__main__":



    # Set your variables for your environment
    EXPERIMENT_NAME="car_price_estimator"

    mlflow.set_tracking_uri("https://my-get-around.herokuapp.com/")

    # Instanciate your experiment
    client = mlflow.tracking.MlflowClient()

    # Set experiment's info 
    mlflow.set_experiment(EXPERIMENT_NAME)

    # Get our experiment info
    experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)
    run = client.create_run(experiment.experiment_id) # Creates a new run for a given experiment

    # Call mlflow autolog
    mlflow.sklearn.autolog()


    # Read data
    data_pricing =  pd.read_csv("get_around_pricing_project.csv")

    # Remove useless column
    data_pricing = data_pricing.iloc[: , 1:]

    # Split dataset into X features and Target variable
    X = data_pricing.drop(['rental_price_per_day'], axis=1)
    y = data_pricing['rental_price_per_day']

    # Split our training set and our test set 
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size =0.2, random_state = 42)

    # Splitting my numerical and categorical features
    numeric_features = ["mileage", "engine_power"]
    categorical_features = ["model_key", "fuel", "paint_color", "car_type", "private_parking_available", "has_gps", "has_air_conditioning", "automatic_car", "has_getaround_connect", "has_speed_regulator", "winter_tires"]

    # Create pipeline for numeric features
    numeric_transformer = Pipeline(steps=[
        ('scaler', StandardScaler())
    ])

    # Create pipeline for categorical features
    categorical_transformer = Pipeline(steps=[
        ('encoder', OneHotEncoder(drop='first')) # first column will be dropped to avoid creating correlations between features
        ])

    # Use ColumnTranformer to make a preprocessor object that describes all the treatments to be done
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])

    # Instantiating a linear regression model

    model = Pipeline(steps=[
    ("Preprocessing", preprocessor),
    ("Regressor",LinearRegression())
    ])



    with mlflow.start_run(run_id = run.info.run_id):

        # Fitting the model
        model.fit(X_train, y_train)

        predictions = model.predict(X_train)

        # Log model separately to have more flexibility on setup 
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="car_price_estimator",
            registered_model_name="car_price_estimator_LR",
            signature=infer_signature(X_train, predictions)
        )