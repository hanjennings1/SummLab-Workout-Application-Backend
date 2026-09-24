from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
db = SQLAlchemy()

# EXERCISE MODEL
class Exercise(db.Model):
    __tablename__ = 'exercises'  # table name used by foreign keys

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)                 # e.g., "Push-up"
    category = db.Column(db.String)             # e.g., "strength", "cardio"
    equipment_needed = db.Column(db.Boolean)    # True if equipment is required

    # An exercise has many WorkoutExercises; deleting an exercise deletes its links:
    workout_exercises = db.relationship(
        'WorkoutExercise', back_populates='exercise', cascade='all, delete-orphan'
    )
    # An exercise has many workouts through WorkoutExercises:
    workouts = association_proxy('workout_exercises', 'workout')

    def __repr__(self):
        # Readable output when printing or debugging
        return f'<Exercise {self.id}: {self.name} ({self.category})>'


# WORKOUT MODEL
class Workout(db.Model):
    __tablename__ = 'workouts'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)                  # expects a Python date object, not a string
    duration_minutes = db.Column(db.Integer)   # total workout length
    notes = db.Column(db.Text)                 # Text allows longer, free-form content

    # A workout has many WorkoutExercises; deleting a workout deletes its links:
    workout_exercises = db.relationship(
        'WorkoutExercise', back_populates='workout', cascade='all, delete-orphan'
    )
    # A workout has many exercises through WorkoutExercises:
    exercises = association_proxy('workout_exercises', 'exercise')

    def __repr__(self):
        # Readable output when printing or debugging
        return f'<Workout {self.id}: {self.date} ({self.duration_minutes} min)>'


# WORKOUT-EXERCISES MODEL (JOIN TABLE)
class WorkoutExercise(db.Model):
    __tablename__ = 'workout_exercises'

    id = db.Column(db.Integer, primary_key=True)
    # Foreign keys reference table names ('workouts'), not class names:
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.id'))
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'))
    reps = db.Column(db.Integer)               # per set; empty for timed exercises
    sets = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)   # for timed exercises (e.g., plank)

    # Each WorkoutExercise belongs to one workout and one exercise:
    workout = db.relationship('Workout', back_populates='workout_exercises')
    exercise = db.relationship('Exercise', back_populates='workout_exercises')

    def __repr__(self):
        # Readable output when printing or debugging:
        return (f'<WorkoutExercise {self.id}: workout {self.workout_id}, '
                f'exercise {self.exercise_id}>')