import json
import os
import random
from typing import List, Dict, Any

# Correctly locate the project root to access top-level directories
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
EXERCISES_FILE = os.path.join(PROJECT_ROOT, "streamlit_workout_app", "exercises.json")
IMAGE_DIR = os.path.join(PROJECT_ROOT, "images")
PLACEHOLDER_IMAGE = os.path.join(IMAGE_DIR, "placeholder.png")


def load_all_exercises() -> List[Dict[str, Any]]:
    """Load all exercises from the JSON file with error handling."""
    try:
        if not os.path.exists(EXERCISES_FILE):
            print(f"Warning: {EXERCISES_FILE} not found. Using fallback exercises.")
            return get_fallback_exercises()

        with open(EXERCISES_FILE, 'r', encoding='utf-8') as f:
            exercises = json.load(f)

        # Validate exercise data structure
        validated_exercises = []
        for exercise in exercises:
            if validate_exercise(exercise):
                validated_exercises.append(exercise)
            else:
                print(f"Warning: Invalid exercise data for {exercise.get('name', 'unknown')}")

        return validated_exercises

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file: {e}")
        return get_fallback_exercises()
    except Exception as e:
        print(f"Error loading exercises: {e}")
        return get_fallback_exercises()


def validate_exercise(exercise: Dict[str, Any]) -> bool:
    """Validate that an exercise has required fields."""
    required_fields = ['name', 'description', 'instructions', 'muscles_worked', 'equipment', 'focus_area']

    for field in required_fields:
        if field not in exercise:
            return False

    # Validate data types
    if not isinstance(exercise['name'], str):
        return False
    if not isinstance(exercise['instructions'], list):
        return False
    if not isinstance(exercise['muscles_worked'], list):
        return False

    return True


def get_fallback_exercises() -> List[Dict[str, Any]]:
    """Return basic fallback exercises if JSON loading fails."""
    return [
        {
            "name": "Bodyweight Squat",
            "description": "Basic squat exercise targeting lower body",
            "instructions": [
                "Stand with feet shoulder-width apart",
                "Lower by bending knees and pushing hips back",
                "Return to standing position"
            ],
            "tips": ["Keep chest up", "Don't let knees cave inward"],
            "muscles_worked": ["Quadriceps", "Glutes", "Hamstrings"],
            "equipment": "bodyweight",
            "focus_area": "lower",
            "duration": 45
        },
        {
            "name": "Push-Up",
            "description": "Upper body exercise targeting chest and arms",
            "instructions": [
                "Start in plank position",
                "Lower chest to ground",
                "Push back up"
            ],
            "tips": ["Keep body straight", "Don't let hips sag"],
            "muscles_worked": ["Chest", "Shoulders", "Triceps"],
            "equipment": "bodyweight",
            "focus_area": "upper",
            "duration": 30
        },
        {
            "name": "Plank",
            "description": "Core stability exercise",
            "instructions": [
                "Hold plank position",
                "Keep body straight",
                "Breathe steadily"
            ],
            "tips": ["Don't let hips drop", "Keep core tight"],
            "muscles_worked": ["Core", "Shoulders"],
            "equipment": "bodyweight",
            "focus_area": "core",
            "duration": 60
        },
        {
            "name": "Jumping Jacks",
            "description": "Full body cardio exercise",
            "instructions": [
                "Start with feet together",
                "Jump while spreading legs",
                "Return to start position"
            ],
            "tips": ["Land softly", "Keep core engaged"],
            "muscles_worked": ["Calves", "Shoulders", "Core"],
            "equipment": "bodyweight",
            "focus_area": "full_body",
            "duration": 30
        }
    ]


def get_exercises(equipment: str = "all", focus_area: str = "all") -> List[Dict[str, Any]]:
    """Get filtered exercises based on equipment and focus area."""
    all_exercises = load_all_exercises()

    filtered_exercises = []
    for exercise in all_exercises:
        equipment_match = (equipment == "all" or exercise.get("equipment") == equipment)
        focus_match = (focus_area == "all" or exercise.get("focus_area") == focus_area)

        if equipment_match and focus_match:
            filtered_exercises.append(exercise)

    return filtered_exercises


def get_random_workout(equipment: str = "all", focus_area: str = "all") -> List[Dict[str, Any]]:
    """Generate a random workout with 4-6 exercises."""
    eligible_exercises = get_exercises(equipment, focus_area)

    if not eligible_exercises:
        # If no exercises match criteria, return all exercises
        eligible_exercises = load_all_exercises()

    # Ensure we have at least some exercises
    if len(eligible_exercises) < 4:
        return eligible_exercises

    # Return 4-6 exercises for optimal 10-minute workout
    workout_size = min(6, len(eligible_exercises))
    workout_size = max(4, workout_size)  # Ensure at least 4 exercises

    return random.sample(eligible_exercises, workout_size)


def ensure_image(exercise: Dict[str, Any]) -> str:
    """Ensure image exists for exercise, return path or placeholder."""
    # Create images directory if it doesn't exist
    if not os.path.exists(IMAGE_DIR):
        os.makedirs(IMAGE_DIR)

    # Try to find an image for this exercise
    exercise_name = exercise.get('name', '').lower().replace(' ', '_')
    possible_extensions = ['.png', '.jpg', '.jpeg', '.gif']

    for ext in possible_extensions:
        image_path = os.path.join(IMAGE_DIR, f"{exercise_name}{ext}")
        if os.path.exists(image_path):
            return image_path

    # Return placeholder if no specific image found
    return PLACEHOLDER_IMAGE


def get_equipment_types() -> List[str]:
    """Get all unique equipment types from loaded exercises."""
    all_exercises = load_all_exercises()
    equipment_types = set()

    for exercise in all_exercises:
        equipment = exercise.get('equipment', '')
        if equipment:
            equipment_types.add(equipment)

    return sorted(list(equipment_types))


def get_focus_areas() -> List[str]:
    """Get all unique focus areas from loaded exercises."""
    all_exercises = load_all_exercises()
    focus_areas = set()

    for exercise in all_exercises:
        focus_area = exercise.get('focus_area', '')
        if focus_area:
            focus_areas.add(focus_area)

    return sorted(list(focus_areas))


def get_muscles_worked() -> List[str]:
    """Get all unique muscles from loaded exercises."""
    all_exercises = load_all_exercises()
    muscles = set()

    for exercise in all_exercises:
        exercise_muscles = exercise.get('muscles_worked', [])
        if isinstance(exercise_muscles, list):
            muscles.update(exercise_muscles)

    return sorted(list(muscles))


def calculate_workout_duration(exercises: List[Dict[str, Any]]) -> int:
    """Calculate total workout duration in seconds."""
    total_duration = 0
    for exercise in exercises:
        duration = exercise.get('duration', 30)  # Default to 30 seconds
        total_duration += duration

    # Add rest time between exercises (10 seconds between each)
    if len(exercises) > 1:
        rest_time = (len(exercises) - 1) * 10
        total_duration += rest_time

    return total_duration


def get_exercise_by_name(exercise_name: str) -> Dict[str, Any]:
    """Get a specific exercise by name."""
    all_exercises = load_all_exercises()

    for exercise in all_exercises:
        if exercise.get('name', '').lower() == exercise_name.lower():
            return exercise

    return {}


def save_custom_exercise(exercise: Dict[str, Any]) -> bool:
    """Save a custom exercise to the JSON file."""
    try:
        # Validate the exercise first
        if not validate_exercise(exercise):
            print("Error: Invalid exercise data")
            return False

        # Load existing exercises
        all_exercises = load_all_exercises()

        # Check if exercise already exists
        existing_names = [ex.get('name', '').lower() for ex in all_exercises]
        if exercise.get('name', '').lower() in existing_names:
            print(f"Error: Exercise '{exercise['name']}' already exists")
            return False

        # Add new exercise
        all_exercises.append(exercise)

        # Save back to file
        with open(EXERCISES_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_exercises, f, indent=2, ensure_ascii=False)

        print(f"Successfully added exercise: {exercise['name']}")
        return True

    except Exception as e:
        print(f"Error saving exercise: {e}")
        return False


def get_workout_stats(exercises: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Get statistics about a workout."""
    if not exercises:
        return {}

    total_duration = calculate_workout_duration(exercises)
    all_muscles = set()
    equipment_needed = set()
    focus_areas = set()

    for exercise in exercises:
        # Collect muscles worked
        muscles = exercise.get('muscles_worked', [])
        if isinstance(muscles, list):
            all_muscles.update(muscles)

        # Collect equipment needed
        equipment = exercise.get('equipment', '')
        if equipment:
            equipment_needed.add(equipment)

        # Collect focus areas
        focus_area = exercise.get('focus_area', '')
        if focus_area:
            focus_areas.add(focus_area)

    return {
        'total_exercises': len(exercises),
        'total_duration_seconds': total_duration,
        'total_duration_minutes': round(total_duration / 60, 1),
        'muscles_worked': sorted(list(all_muscles)),
        'equipment_needed': sorted(list(equipment_needed)),
        'focus_areas': sorted(list(focus_areas))
    }