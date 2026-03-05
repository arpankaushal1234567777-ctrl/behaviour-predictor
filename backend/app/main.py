from fastapi.middleware.cors import CORSMiddleware
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
import numpy as np
from .ml_model import train_model, predict_productivity
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import date
import numpy as np
from sklearn.linear_model import LogisticRegression
from .database import engine, SessionLocal
from .models import Base, User, DailyLog
from .auth import hash_password, verify_password
from model_utils import save_model, load_model
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
import numpy as np
from pydantic import BaseModel

class PredictRequest(BaseModel):
    sleep_hours: float
    study_hours: float
    screen_time: float
    exercise_minutes: float

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


# -------------------------
# Database Dependency
# -------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------
# Home Route
# -------------------------
@app.get("/")
def home():
    return {"message": "Behaviour Prediction API Running"}


# -------------------------
# Register
# -------------------------
@app.post("/register")
def register(email: str, password: str, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(User.email == email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=email,
        password_hash=hash_password(password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}


# -------------------------
# Login
# -------------------------
@app.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    return {"message": "Login successful"}


# -------------------------
# Add Daily Log
# -------------------------
@app.post("/add-daily-log")
def add_daily_log(
    email: str,
    sleep_hours: float,
    study_hours: float,
    screen_time: float,
    exercise_minutes: float,
    mood: int,
    productivity_score: float,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    new_log = DailyLog(
        date=date.today(),
        sleep_hours=sleep_hours,
        study_hours=study_hours,
        screen_time=screen_time,
        exercise_minutes=exercise_minutes,
        mood=mood,
        productivity_score=productivity_score,
        owner=user
    )

    db.add(new_log)
    db.commit()
    db.refresh(new_log)

    return {"message": "Daily log added successfully"}


# -------------------------
# Train Model
# -------------------------
@app.post("/train")
def train_model():

    db = SessionLocal()
    logs = db.query(DailyLog).all()
    db.close()

    if len(logs) < 10:
        return {"error": "Not enough data to train model"}

    X = []
    y = []

    for i, log in enumerate(logs):
        previous_score = logs[i-1].productivity_score if i > 0 else 50
        sleep_study_ratio = log.sleep_hours / (log.study_hours + 1)

        features = [
            log.sleep_hours,
            log.study_hours,
            log.screen_time,
            log.exercise_minutes,
            sleep_study_ratio,
            previous_score
        ]

        X.append(features)
        y.append(log.productivity_score)

    X = np.array(X)
    y = np.array(y)

    # Proper train-test split
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=6,
        random_state=42
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    accuracy = r2_score(y_test, predictions)

    # Save model
    with open("model.pkl", "wb") as f:
        import pickle
        pickle.dump(model, f)

    return {
        "message": "Model trained successfully",
        "r2_score": float(accuracy),
        "training_samples": len(X_train),
        "testing_samples": len(X_test)
    }# -------------------------
# Prediction Schema
# -------------------------
class PredictSchema(BaseModel):
    sleep_hours: float
    study_hours: float
    screen_time: float
    exercise_minutes: float
    mood: int


# -------------------------
# Predict
# -------------------------
@app.post("/predict")
def predict(data: PredictRequest):

    import pickle
    import numpy as np

    with open("model.pkl", "rb") as f:
        model = pickle.load(f)

    sleep = data.sleep_hours
    study = data.study_hours
    screen = data.screen_time
    exercise = data.exercise_minutes

    sleep_study_ratio = sleep / (study + 1)

    # Temporary previous score (later we’ll fetch real one from DB)
    previous_score = 50

    features = np.array([[
        sleep,
        study,
        screen,
        exercise,
        sleep_study_ratio,
        previous_score
    ]])

    prediction = model.predict(features)[0]

    insight = ""

    if prediction < 50:
        insight = "Low productivity expected. Improve sleep and reduce screen time."
    elif prediction < 75:
        insight = "Moderate productivity. Try increasing focused study hours."
    else:
        insight = "High productivity pattern. Maintain this balance."

    return {
        "predicted_productivity": float(prediction),
        "insight": insight
    }