from flask import Flask, make_response, request
from flask_migrate import Migrate
from marshmallow import ValidationError

from models import db, Exercise, Workout, WorkoutExercise
from schemas import ExerciseSchema, WorkoutSchema, WorkoutExerciseSchema


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

db.init_app(app)


# Schema instances: single-record views include nested data; lists stay concise
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True, exclude=('workout_exercises',))
exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True, exclude=('workouts',))
workout_exercise_schema = WorkoutExerciseSchema()


# ---------- WORKOUT ROUTES ----------

@app.route('/workouts', methods=['GET'])
def get_workouts():
    workouts = Workout.query.all()
    return make_response(workouts_schema.dump(workouts), 200)

@app.route('/workouts/<int:id>', methods=['GET'])
def get_workout(id):
    workout = db.session.get(Workout, id)
    if not workout:
        return make_response({'error': 'Workout not found'}, 404)
    return make_response(workout_schema.dump(workout), 200)

@app.route('/workouts', methods=['POST'])
def create_workout():
    try:
        data = workout_schema.load(request.get_json())
        workout = Workout(**data)
        db.session.add(workout)
        db.session.commit()
    except ValidationError as e:     # schema validations (Marshmallow)
        return make_response({'error': e.messages}, 400)
    except ValueError as e:          # model validations (@validates)
        return make_response({'error': str(e)}, 400)
    return make_response(workout_schema.dump(workout), 201)

@app.route('/workouts/<int:id>', methods=['DELETE'])
def delete_workout(id):
    workout = db.session.get(Workout, id)
    if not workout:
        return make_response({'error': 'Workout not found'}, 404)
    db.session.delete(workout)  # cascade also deletes its WorkoutExercises
    db.session.commit()
    return make_response('', 204)


# ---------- EXERCISE ROUTES ----------

@app.route('/exercises', methods=['GET'])
def get_exercises():
    return make_response({'message': 'List all exercises'}, 200)

@app.route('/exercises/<int:id>', methods=['GET'])
def get_exercise(id):
    return make_response({'message': f'Show exercise {id} with its workouts'}, 200)

@app.route('/exercises', methods=['POST'])
def create_exercise():
    return make_response({'message': 'Create an exercise'}, 200)

@app.route('/exercises/<int:id>', methods=['DELETE'])
def delete_exercise(id):
    return make_response({'message': f'Delete exercise {id}'}, 200)


# ---------- WORKOUT EXERCISE ROUTES ----------

@app.route(
    '/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises',
    methods=['POST']
)
def add_exercise_to_workout(workout_id, exercise_id):
    return make_response(
        {'message': f'Add exercise {exercise_id} to workout {workout_id}'}, 200
    )


if __name__ == '__main__':
    app.run(port=5555, debug=True)