#!/usr/bin/env python3
"""Resets the database and seeds it with example exercises, workouts, and links."""

from datetime import date

from app import app
from models import db, Exercise, Workout, WorkoutExercise

with app.app_context():
    print('Clearing existing data...')
    # Delete join records first, since they reference workouts and exercises
    WorkoutExercise.query.delete()
    Workout.query.delete()
    Exercise.query.delete()
    db.session.commit()

    print('Creating exercises...')
    push_up = Exercise(name='Push-up', category='strength', equipment_needed=False)
    squat = Exercise(name='Barbell Squat', category='strength', equipment_needed=True)
    plank = Exercise(name='Plank', category='strength', equipment_needed=False)
    run = Exercise(name='Treadmill Run', category='cardio', equipment_needed=True)
    stretch = Exercise(name='Hamstring Stretch', category='flexibility', equipment_needed=False)
    balance = Exercise(name='Single-Leg Stand', category='balance', equipment_needed=False)

    db.session.add_all([push_up, squat, plank, run, stretch, balance])
    db.session.commit()

    print('Creating workouts...')
    upper_body = Workout(
        date=date(2026, 9, 21),
        duration_minutes=45,
        notes='Upper body strength focus. Client pushed to failure on last set.'
    )
    leg_day = Workout(
        date=date(2026, 9, 22),
        duration_minutes=60,
        notes='Leg day with a cardio finisher.'
    )
    recovery = Workout(
        date=date(2026, 9, 23),
        duration_minutes=30,
        notes='Light recovery session: mobility and balance work.'
    )

    db.session.add_all([upper_body, leg_day, recovery])
    db.session.commit()

    print('Adding exercises to workouts...')
    workout_exercises = [
        # Upper body: rep-based and timed exercises
        WorkoutExercise(workout=upper_body, exercise=push_up, sets=3, reps=15),
        WorkoutExercise(workout=upper_body, exercise=plank, duration_seconds=60),

        # Leg day
        WorkoutExercise(workout=leg_day, exercise=squat, sets=4, reps=8),
        WorkoutExercise(workout=leg_day, exercise=run, duration_seconds=900),
        WorkoutExercise(workout=leg_day, exercise=stretch, duration_seconds=60),

        # Recovery: reuses plank and stretch from other workouts
        WorkoutExercise(workout=recovery, exercise=stretch, duration_seconds=90),
        WorkoutExercise(workout=recovery, exercise=balance, duration_seconds=45),
        WorkoutExercise(workout=recovery, exercise=plank, duration_seconds=45),
    ]

    db.session.add_all(workout_exercises)
    db.session.commit()

    print('Seeding complete!')