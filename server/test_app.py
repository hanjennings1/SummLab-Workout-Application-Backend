"""Tests for model validations and API endpoint status codes."""

import os
os.environ['DATABASE_URI'] = 'sqlite:///:memory:'  # must be set before importing app

import pytest
from app import app
from models import db, Exercise, Workout


@pytest.fixture
def client():
    # Fresh in-memory database for each test; never touches app.db
    with app.app_context():
        db.create_all()
        db.session.add(Exercise(name='Push-up', category='strength'))
        db.session.commit()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


# ---------- Model validations ----------

def test_exercise_rejects_invalid_category():
    with pytest.raises(ValueError):
        Exercise(name='Lunge', category='yoga')


def test_workout_rejects_nonpositive_duration():
    with pytest.raises(ValueError):
        Workout(duration_minutes=0)


# ---------- Endpoints ----------

def test_get_exercises_returns_list(client):
    response = client.get('/exercises')
    assert response.status_code == 200
    assert response.json[0]['name'] == 'Push-up'


def test_get_missing_workout_returns_404(client):
    response = client.get('/workouts/999')
    assert response.status_code == 404


def test_create_workout_returns_201(client):
    response = client.post('/workouts', json={'date': '2026-09-25', 'duration_minutes': 40})
    assert response.status_code == 201
    assert response.json['id'] is not None


def test_create_workout_with_invalid_data_returns_400(client):
    response = client.post('/workouts', json={'date': 'tomorrow', 'duration_minutes': 0})
    assert response.status_code == 400


def test_create_duplicate_exercise_returns_409(client):
    response = client.post('/exercises', json={'name': 'Push-up', 'category': 'strength'})
    assert response.status_code == 409