from marshmallow import Schema, fields


# ===== EXERCISE SCHEMA =====
class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    category = fields.Str(required=True)
    equipment_needed = fields.Bool(load_default=False)  # defaults to False if omitted

    # Associated workouts; excludes their exercise details to prevent infinite nesting
    workouts = fields.List(
        fields.Nested(lambda: WorkoutSchema(exclude=('workout_exercises',))),
        dump_only=True
    )

# ===== WORKOUT SCHEMA =====
class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)  # "YYYY-MM-DD" in JSON, a date object in Python
    duration_minutes = fields.Int(required=True)
    notes = fields.Str(allow_none=True)

    # Exercises in this workout, including reps/sets/duration from the join table
    workout_exercises = fields.List(
        fields.Nested(lambda: WorkoutExerciseSchema()),
        dump_only=True
    )

# ===== WORKOUT EXERCISE SCHEMA (JOIN TABLE) =====
class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(dump_only=True)   # set from the URL, not the request body
    exercise_id = fields.Int(dump_only=True)
    reps = fields.Int(allow_none=True)
    sets = fields.Int(allow_none=True)
    duration_seconds = fields.Int(allow_none=True)

    # The exercise's details; excludes its workouts to prevent infinite nesting
    exercise = fields.Nested(
        lambda: ExerciseSchema(exclude=('workouts',)),
        dump_only=True
    )