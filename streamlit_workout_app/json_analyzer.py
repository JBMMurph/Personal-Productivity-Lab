import json
import streamlit as st
from collections import Counter


def analyze_json_structure():
    """Analyze the structure of your exercises.json file"""
    st.title("🔍 JSON Structure Analyzer")

    try:
        with open('exercises.json', 'r') as f:
            data = json.load(f)

        st.success("✅ JSON file loaded successfully!")

        # Show basic info
        st.subheader("📊 Basic Information")
        st.write(f"**Data type:** {type(data).__name__}")

        if isinstance(data, dict):
            st.write(f"**Keys in JSON:** {list(data.keys())}")
            if 'exercises' in data:
                exercises = data['exercises']
                st.write(f"**Number of exercises:** {len(exercises)}")
            else:
                st.error("❌ No 'exercises' key found in JSON object")
                return
        elif isinstance(data, list):
            exercises = data
            st.write(f"**Number of exercises:** {len(exercises)}")
        else:
            st.error("❌ JSON is neither a list nor a dict with 'exercises' key")
            return

        if not exercises:
            st.error("❌ No exercises found")
            return

        # Analyze first exercise
        st.subheader("🔬 First Exercise Analysis")
        first_exercise = exercises[0]
        st.write("**Structure of first exercise:**")
        st.json(first_exercise)

        # Show all available fields
        st.subheader("📋 Available Fields")
        all_fields = set()
        for exercise in exercises:
            if isinstance(exercise, dict):
                all_fields.update(exercise.keys())

        st.write(f"**All fields found across exercises:** {sorted(all_fields)}")

        # Analyze equipment values
        if 'equipment' in all_fields:
            equipment_values = []
            for exercise in exercises:
                if 'equipment' in exercise:
                    equipment_values.append(exercise['equipment'])

            equipment_counts = Counter(equipment_values)
            st.subheader("🏋️ Equipment Analysis")
            st.write("**Equipment values found:**")
            for equipment, count in equipment_counts.items():
                st.write(f"- '{equipment}': {count} exercises")

        # Analyze focus_area values
        if 'focus_area' in all_fields:
            focus_values = []
            for exercise in exercises:
                if 'focus_area' in exercise:
                    focus_values.append(exercise['focus_area'])

            focus_counts = Counter(focus_values)
            st.subheader("🎯 Focus Area Analysis")
            st.write("**Focus area values found:**")
            for focus, count in focus_counts.items():
                st.write(f"- '{focus}': {count} exercises")

        # Show what the app expects
        st.subheader("⚠️ Expected Values")
        st.write("**The app expects these exact values:**")
        st.write("**Equipment:** 'bodyweight', 'dumbbells'")
        st.write("**Focus Area:** 'full_body', 'upper', 'lower', 'core'")

        # Check for mismatches
        st.subheader("🔧 Recommendations")
        if 'equipment' in all_fields:
            equipment_values = set(ex.get('equipment') for ex in exercises if 'equipment' in ex)
            expected_equipment = {'bodyweight', 'dumbbells'}
            if not equipment_values.issubset(expected_equipment):
                st.warning(f"❌ Non-standard equipment values found: {equipment_values - expected_equipment}")
                st.write("Consider updating these to 'bodyweight' or 'dumbbells'")

        if 'focus_area' in all_fields:
            focus_values = set(ex.get('focus_area') for ex in exercises if 'focus_area' in ex)
            expected_focus = {'full_body', 'upper', 'lower', 'core'}
            if not focus_values.issubset(expected_focus):
                st.warning(f"❌ Non-standard focus area values found: {focus_values - expected_focus}")
                st.write("Consider updating these to 'full_body', 'upper', 'lower', or 'core'")

    except FileNotFoundError:
        st.error("❌ exercises.json file not found")
    except json.JSONDecodeError as e:
        st.error(f"❌ JSON parsing error: {e}")
    except Exception as e:
        st.error(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    analyze_json_structure()