import json
import random
import os
import argparse

EXERCISES_FILE = os.path.join(os.path.dirname(__file__), 'exercises.json')

def load_exercises():
    if not os.path.exists(EXERCISES_FILE):
        # This part is now for fallback, the main json has descriptions
        default_exercises = {}
        with open(EXERCISES_FILE, 'w') as f:
            json.dump(default_exercises, f, indent=2)
        return default_exercises
    try:
        with open(EXERCISES_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        print(f"Error reading {EXERCISES_FILE}. A default set will be created.")
        return load_exercises()

def generate_workout(exercises, equipment, muscle_focus_list):
    combined_exercise_list = {}
    for focus in muscle_focus_list:
        try:
            exercise_dict = exercises[equipment][focus]
            if not exercise_dict:
                print(f"Warning: No exercises found for {equipment} - {focus}. Skipping.")
                continue
            combined_exercise_list.update(exercise_dict)
        except KeyError:
            print(f"Warning: Invalid muscle focus '{focus}'. Skipping.")
            continue

    if not combined_exercise_list:
        print("No exercises found for the selected criteria. Please check your choices.")
        return None

    exercise_names = list(combined_exercise_list.keys())
    num_exercises = min(len(exercise_names), 6)
    if num_exercises == 0:
        print("No exercises available to generate a workout.")
        return None
        
    selected_exercise_names = random.sample(exercise_names, num_exercises)
    
    selected_exercises = [(name, combined_exercise_list[name]) for name in selected_exercise_names]
    return selected_exercises

def main():
    parser = argparse.ArgumentParser(description="Generate a 10-minute low-impact workout plan.")
    parser.add_argument("equipment", nargs='?', default=None, help="The equipment to use (e.g., bodyweight, dumbbells)")
    parser.add_argument("muscle_focus", nargs='?', default=None, help="Comma-separated list of muscle groups (e.g., 'lower,core')")
    args = parser.parse_args()

    exercises = load_exercises()

    print("Welcome to the 10-Minute Low-Impact Workout Generator!")

    equipment = args.equipment
    muscle_focus_input = args.muscle_focus

    if not equipment:
        while True:
            try:
                equipment = input(f"Choose your equipment ({', '.join(exercises.keys())}): ").lower()
                if equipment in exercises:
                    break
                print("Invalid equipment. Please choose from the available options.")
            except EOFError:
                print("\nOperation cancelled.")
                return

    muscle_focus_list = []
    if not muscle_focus_input:
        while True:
            try:
                muscle_focus_input = input(f"Choose your muscle focus ({', '.join(exercises[equipment].keys())}). You can enter multiple, separated by commas: ").lower()
                
                potential_focuses = [focus.strip() for focus in muscle_focus_input.split(',')]
                valid_focuses = []
                invalid_focuses = []

                for focus in potential_focuses:
                    if focus in exercises[equipment]:
                        valid_focuses.append(focus)
                    else:
                        invalid_focuses.append(focus)
                
                if invalid_focuses:
                    print(f"Invalid muscle focus options: {', '.join(invalid_focuses)}. Please choose from the available options.")
                
                if valid_focuses:
                    muscle_focus_list = valid_focuses
                    break
                else:
                    print("Please enter at least one valid muscle focus.")

            except EOFError:
                print("\nOperation cancelled.")
                return
    else:
        muscle_focus_list = [focus.strip() for focus in muscle_focus_input.split(',')]
        for focus in muscle_focus_list:
            if focus not in exercises[equipment]:
                print(f"Invalid muscle focus '{focus}' provided in arguments. Exiting.")
                return

    if not muscle_focus_list:
        print("No valid muscle focus selected. Exiting.")
        return

    workout = generate_workout(exercises, equipment, muscle_focus_list)

    if workout:
        print("\nYour 10-minute workout plan:")
        print("--------------------------------")
        print("Aim for 60 seconds of work for each exercise, followed by 40 seconds of rest.")
        for i, (name, description) in enumerate(workout):
            print(f"\n{i+1}. {name}")
            print(f"   Description: {description}")
        print("\n--------------------------------")
        print("Enjoy your workout!")

if __name__ == "__main__":
    main()
