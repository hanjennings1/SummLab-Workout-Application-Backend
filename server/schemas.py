"""Marshmallow schemas for serialization, deserialization, and schema validations."""

from marshmallow import Schema, fields, validate, validates_schema, ValidationError


# ===== EXERCISE SCHEMA =====
class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
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
    duration_minutes = fields.Int(
        required=True, validate=validate.Range(min=1, max=600)  # 1 minute to 10 hours
    )
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
    reps = fields.Int(allow_none=True, validate=validate.Range(min=1))
    sets = fields.Int(allow_none=True, validate=validate.Range(min=1))
    duration_seconds = fields.Int(allow_none=True, validate=validate.Range(min=1))

    # The exercise's details; excludes its workouts to prevent infinite nesting
    exercise = fields.Nested(
        lambda: ExerciseSchema(exclude=('workouts',)),
        dump_only=True
    )

    # validation for reps/duration in workout-exercise schema
    @validates_schema
    def validate_reps_or_duration(self, data, **kwargs):
        # Rep-based exercises need reps and sets; timed exercises need a duration
        has_reps = data.get('reps') is not None and data.get('sets') is not None
        has_duration = data.get('duration_seconds') is not None
        if not (has_reps or has_duration):
            raise ValidationError('Provide both reps and sets, or duration_seconds.')