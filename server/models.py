from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
db = SQLAlchemy()

# ======= EXERCISE MODEL =======
class Exercise(db.Model):
    __tablename__ = 'exercises'  # table name used by foreign keys
    CATEGORIES = ('strength', 'cardio', 'flexibility', 'balance')  # allowed category values

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)    # required field; no duplicates
    category = db.Column(db.String)                 # e.g., "strength", "cardio"
    equipment_needed = db.Column(db.Boolean)        # True if equipment is required

    # An exercise has many WorkoutExercises; deleting an exercise deletes its links:
    workout_exercises = db.relationship(
        'WorkoutExercise', back_populates='exercise', cascade='all, delete-orphan'
    )
    # An exercise has many workouts through WorkoutExercises:
    workouts = association_proxy('workout_exercises', 'workout')

    # VALIDATIONS--
    # name validation
    @validates('name')
    def validate_name(self, key, value):
        # Reject empty or whitespace-only names (nullable=False still allows "")
        if not value or not value.strip():
            raise ValueError('Exercise name cannot be blank.')
        return value.strip()
    
    # category validation
    @validates('category')
    def validate_category(self, key, value):
        # Normalize case so "Strength" and "strength" are treated the same
        normalized = value.strip().lower() if value else value
        if normalized not in self.CATEGORIES:
            raise ValueError(f"Category must be one of: {', '.join(self.CATEGORIES)}.")
        return normalized

    def __repr__(self):
        # Readable output when printing or debugging
        return f'<Exercise {self.id}: {self.name} ({self.category})>'



# ======= WORKOUT MODEL =======
class Workout(db.Model):
    __tablename__ = 'workouts'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)  # required; expects a Python date object, not a string
    duration_minutes = db.Column(db.Integer)   # total workout length
    notes = db.Column(db.Text)                 # Text allows longer, free-form content

    # A workout has many WorkoutExercises; deleting a workout deletes its links:
    workout_exercises = db.relationship(
        'WorkoutExercise', back_populates='workout', cascade='all, delete-orphan'
    )
    # A workout has many exercises through WorkoutExercises:
    exercises = association_proxy('workout_exercises', 'exercise')

    # VALIDATIONS--
    # duration in minutes
    @validates('duration_minutes')
    def validate_duration_minutes(self, key, value):
        # A workout must last a positive number of minutes
        if value is None or value <= 0:
            raise ValueError('Duration must be a positive number of minutes.')
        return value
    
    def __repr__(self):
        # Readable output when printing or debugging
        return f'<Workout {self.id}: {self.date} ({self.duration_minutes} min)>'


# WORKOUT-EXERCISES MODEL (JOIN TABLE)
class WorkoutExercise(db.Model):
    __tablename__ = 'workout_exercises'

    # Database-level rules: values must be positive when provided
    __table_args__ = (
        db.CheckConstraint('reps > 0', name='ck_reps_positive'),
        db.CheckConstraint('sets > 0', name='ck_sets_positive'),
        db.CheckConstraint('duration_seconds > 0', name='ck_duration_positive'),
    )

    id = db.Column(db.Integer, primary_key=True)
    # Foreign keys reference table names ('workouts'), not class names:
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
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