import sqlite3
import random
from datetime import datetime, timedelta

# Connect to existing database
conn = sqlite3.connect("behaviour.db")
cursor = conn.cursor()

start_date = datetime(2025, 1, 1)

sleep_trend = 7
stress_trend = 3

for i in range(300):  # Generate 300 days
    date = start_date + timedelta(days=i)
    weekday = date.weekday()
    weekend = 1 if weekday >= 5 else 0

    # Sleep fluctuates slowly
    sleep_trend += random.uniform(-0.3, 0.3)
    sleep_hours = round(max(4, min(9, sleep_trend)), 1)

    # Study hours slightly higher on weekdays
    study_hours = round(random.uniform(2, 6) if weekend == 0 else random.uniform(0.5, 3), 1)

    # Screen time increases if sleep is low
    screen_time = round(random.uniform(3, 6) + (7 - sleep_hours) * 0.5, 1)

    # Exercise lower when stress high
    exercise_minutes = round(random.uniform(10, 60) if sleep_hours > 6 else random.uniform(0, 30), 1)

    # Mood inversely related to low sleep
    mood = int(max(1, min(5, 6 - (7 - sleep_hours))))

    # Productivity influenced by sleep, mood, study
    productivity_score = round(
        (sleep_hours * 0.3) +
        (mood * 0.5) +
        (study_hours * 0.2) -
        (screen_time * 0.1),
        1
    )

    cursor.execute("""
        INSERT INTO daily_logs 
        (date, sleep_hours, study_hours, screen_time, exercise_minutes, mood, productivity_score, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        date.strftime("%Y-%m-%d"),
        sleep_hours,
        study_hours,
        screen_time,
        exercise_minutes,
        mood,
        productivity_score,
        1
    ))

conn.commit()
conn.close()

print("✅ 300 synthetic entries inserted successfully.")