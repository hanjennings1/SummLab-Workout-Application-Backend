# Summative Lab: Relational Databases- Flask SQLAlchemy Workout Application Backend
**Completed Sept 24, 2026**


A Flask REST API for a workout tracking application used by personal trainers. Trainers can create, view, and delete workouts and exercises, and add exercises to workouts with sets, reps, or a duration. Exercises are reusable, so the same exercise can appear in many workouts, each with its own details.

Built with Flask, Flask-SQLAlchemy, Flask-Migrate, and Marshmallow, with validation at three levels: database table constraints, model validations, and schema validations.

## Installation

Requires Python 3.8.13+ and Pipenv.

1. Clone the repository and move into it:

   ```bash
   git clone https://github.com/hanjennings1/SummLab-Workout-Application-Backend.git
   cd SummLab-Workout-Application-Backend
   ```

2. Install dependencies (including pytest for the test suite) and activate the virtual environment:

   ```bash
   pipenv install --dev
   pipenv shell
   ```

3. Move into the `server` directory. All remaining commands are run from here:

   ```bash
   cd server
   ```

4. Create the database tables by applying the migrations:

   ```bash
   flask db upgrade head
   ```

5. Seed the database with example data (6 exercises, 3 workouts, and 8 workout exercises):

   ```bash
   python seed.py
   ```

   The seed file clears existing data first, so it can be rerun at any time to reset the database.

## Running the Application

From the `server` directory:

```bash
python app.py
```

The API runs at `http://127.0.0.1:5555`. Alternatively, use `flask run --port 5555` (without `--port`, `flask run` defaults to port 5000).

## Running the Tests

From the `server` directory:

```bash
pytest -v
```

The tests use a temporary in-memory database, so they never affect the seeded data.

## Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/workouts` | List all workouts |
| GET | `/workouts/<id>` | Show a workout with its exercises, including sets, reps, and duration |
| POST | `/workouts` | Create a workout |
| DELETE | `/workouts/<id>` | Delete a workout and its associated workout exercises |
| GET | `/exercises` | List all exercises |
| GET | `/exercises/<id>` | Show an exercise with its associated workouts |
| POST | `/exercises` | Create an exercise |
| DELETE | `/exercises/<id>` | Delete an exercise and its associated workout exercises |
| POST | `/workouts/<workout_id>/exercises/<exercise_id>/workout_exercises` | Add an exercise to a workout with sets, reps, or duration |

### Workouts

**`GET /workouts`** returns a list of all workouts, without nested exercises. Status: `200`.

**`GET /workouts/<id>`** returns one workout with its workout exercises, each including the nested exercise. Status: `200`, or `404` if the workout doesn't exist.

```json
{
  "date": "2026-09-21",
  "duration_minutes": 45,
  "id": 1,
  "notes": "Upper body strength focus. Client pushed to failure on last set.",
  "workout_exercises": [
    {
      "duration_seconds": null,
      "exercise": { "category": "strength", "equipment_needed": false, "id": 1, "name": "Push-up" },
      "exercise_id": 1,
      "id": 1,
      "reps": 15,
      "sets": 3,
      "workout_id": 1
    },
    {
      "duration_seconds": 60,
      "exercise": { "category": "strength", "equipment_needed": false, "id": 3, "name": "Plank" },
      "exercise_id": 3,
      "id": 2,
      "reps": null,
      "sets": null,
      "workout_id": 1
    }
  ]
}
```

**`POST /workouts`** creates a workout. `date` (format `YYYY-MM-DD`) and `duration_minutes` are required; `notes` is optional. Status: `201`, or `400` if the data is invalid.

```json
{ "date": "2026-09-25", "duration_minutes": 40, "notes": "Conditioning session" }
```

**`DELETE /workouts/<id>`** deletes a workout. Its workout exercises are deleted too; the exercises themselves remain. Status: `204`, or `404` if the workout doesn't exist.

### Exercises

**`GET /exercises`** returns a list of all exercises, without nested workouts. Status: `200`.

**`GET /exercises/<id>`** returns one exercise with a list of the workouts it appears in. Status: `200`, or `404` if the exercise doesn't exist.

**`POST /exercises`** creates an exercise. `name` and `category` are required; `equipment_needed` defaults to `false`. Status: `201`, `400` if the data is invalid, or `409` if an exercise with that name already exists.

```json
{ "name": "Lunge", "category": "strength", "equipment_needed": false }
```

**`DELETE /exercises/<id>`** deletes an exercise. Its workout exercises are deleted too; the workouts themselves remain. Status: `204`, or `404` if the exercise doesn't exist.

### Workout Exercises

**`POST /workouts/<workout_id>/exercises/<exercise_id>/workout_exercises`** adds an exercise to a workout. The ids come from the URL; the body must include either both `reps` and `sets` (for rep-based exercises) or `duration_seconds` (for timed exercises). Status: `201`, `400` if the data is invalid, or `404` if the workout or exercise doesn't exist.

```json
{ "sets": 3, "reps": 12 }
```

```json
{ "duration_seconds": 60 }
```

### Error Responses

All errors use an `error` key. Schema validation errors list problems by field:

```json
{ "error": { "date": ["Not a valid date."], "duration_minutes": ["Must be greater than or equal to 1 and less than or equal to 600."] } }
```

Model validation and constraint errors return a message:

```json
{ "error": "Category must be one of: strength, cardio, flexibility, balance." }
```

## Data Model

- **Exercise**: `id`, `name`, `category`, `equipment_needed`
- **Workout**: `id`, `date`, `duration_minutes`, `notes`
- **WorkoutExercise** (join table): `id`, `workout_id`, `exercise_id`, `reps`, `sets`, `duration_seconds`

A workout has many exercises through workout exercises, and an exercise has many workouts through workout exercises. Each workout exercise belongs to one workout and one exercise.

## Validations

**Table constraints (database)**
- Exercise `name` is required and unique
- Workout `date` is required
- Workout exercise `workout_id` and `exercise_id` are required
- Workout exercise `reps`, `sets`, and `duration_seconds` must be positive when provided

**Model validations**
- Exercise `name` can't be blank or whitespace only (surrounding spaces are trimmed)
- Exercise `category` must be one of `strength`, `cardio`, `flexibility`, or `balance` (case-insensitive; stored in lowercase)
- Workout `duration_minutes` must be greater than 0

**Schema validations**
- Exercise `name` must be 2 to 100 characters
- Workout `duration_minutes` must be between 1 and 600
- Workout exercise `reps`, `sets`, and `duration_seconds` must be at least 1
- A workout exercise must include both `reps` and `sets`, or `duration_seconds`

## Project Structure

```
server/
├── app.py          # Flask app configuration and API routes
├── models.py       # SQLAlchemy models, relationships, constraints, and model validations
├── schemas.py      # Marshmallow schemas and schema validations
├── seed.py         # Resets and seeds the database with example data
├── test_app.py     # Tests for model validations and endpoint status codes
└── migrations/     # Database migrations (Flask-Migrate)
```


## Considerations / Known Limitations

- **No update or unlink endpoints.** Per the project spec, workouts, exercises, and workout exercises can't be edited after creation, and an exercise can't be removed from a workout on its own. To change a record, delete it and create it again.
- **Deleting an exercise removes it from past workouts.** The cascade delete keeps the database consistent, but it also removes that exercise from any workout history that used it.
- **The same exercise can be added to a workout more than once.** There's no unique constraint on the workout/exercise pair, which allows repeated entries (such as an exercise done twice in one session) but also permits accidental duplicates.
- **Exercise name uniqueness is case-sensitive.** Surrounding spaces are trimmed, but "Push-up" and "push-up" count as different names.
- **Categories are fixed in code.** Adding a category means editing `Exercise.CATEGORIES` in `models.py`.
- **No authentication or pagination.** Any client can create or delete records, and list endpoints return every record at once.
- **Development setup only.** The app uses SQLite and runs with debug mode on, which suits local development but not production.