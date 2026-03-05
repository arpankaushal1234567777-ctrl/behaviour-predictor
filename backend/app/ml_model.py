import pandas as pd
from sklearn.linear_model import LinearRegression
import pickle
from .models import DailyLog
from .database import SessionLocal

MODEL_PATH = "app/productivity_model.pkl"


def train_model():

    db = SessionLocal()
    logs = db.query(DailyLog).all()
    db.close()

    if len(logs) < 3:
        return {"error": "Not enough data to train model"}

    data = []

    for log in logs:
        data.append([
            log.sleep_hours,
            log.study_hours,
            log.screen_time,
            log.exercise_minutes,
            log.mood,
            log.productivity_score
        ])

    df = pd.DataFrame(data, columns=[
        "sleep",
        "study",
        "screen",
        "exercise",
        "mood",
        "productivity"
    ])

    X = df[["sleep", "study", "screen", "exercise", "mood"]]
    y = df["productivity"]

    model = LinearRegression()
    model.fit(X, y)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

    return {"message": "Model trained successfully"}

def predict_productivity(sleep, study, screen, exercise, mood):

    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)

    input_data = [[sleep, study, screen, exercise, mood]]

    prediction = model.predict(input_data)[0]

    prediction = max(0, min(100, prediction))

    return float(prediction)