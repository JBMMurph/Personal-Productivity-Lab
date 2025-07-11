import streamlit as st
import time
from datetime import datetime
import base64
import os
import random
from typing import List, Dict, Optional, Tuple

from data_loader import ensure_image, get_exercises, get_random_workout, load_all_exercises

# Configuration
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
IMAGE_DIR = os.path.join(PROJECT_ROOT, "images")
EXERCISES_FILE = os.path.join(PROJECT_ROOT, "streamlit_workout_app", "exercises.json")
PLACEHOLDER_IMAGE = os.path.join(IMAGE_DIR, "placeholder.png")


def ensure_directories_exist():
    """Create necessary directories if they don't exist."""
    if not os.path.exists(IMAGE_DIR):
        os.makedirs(IMAGE_DIR)
        st.info(f"Created {IMAGE_DIR} directory for exercise images.")


# Page configuration
st.set_page_config(
    page_title="10-Minute Workout Generator",
    page_icon="🏋️‍♂️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #ffffff;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 1rem;
        background: linear-gradient(90deg, #00f5ff, #9c27b0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: 0 0 10px rgba(0, 245, 255, 0.3);
    }

    .sub-header {
        text-align: center;
        color: #b0bec5;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }

    .stApp {
        background: linear-gradient(135deg, #1a237e, #4a148c, #1a237e);
        color: white;
    }

    .exercise-card {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }

    .current-exercise {
        background: rgba(0, 245, 255, 0.2);
        border: 2px solid #00f5ff;
        transform: scale(1.02);
        box-shadow: 0 0 20px rgba(0, 245, 255, 0.3);
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0% { box-shadow: 0 0 20px rgba(0, 245, 255, 0.3); }
        50% { box-shadow: 0 0 30px rgba(0, 245, 255, 0.5); }
        100% { box-shadow: 0 0 20px rgba(0, 245, 255, 0.3); }
    }

    .timer-display {
        font-size: 4rem;
        font-weight: bold;
        text-align: center;
        color: #00f5ff;
        margin: 1rem 0;
        text-shadow: 0 0 20px rgba(0, 245, 255, 0.5);
        font-family: 'Courier New', monospace;
    }

    .timer-low {
        color: #ff4444;
        animation: blink 1s infinite;
    }

    @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0.5; }
    }

    .muscle-tag {
        background: rgba(156, 39, 176, 0.3);
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
        margin: 0.2rem;
        display: inline-block;
        border: 1px solid rgba(156, 39, 176, 0.5);
    }

    .tip-box {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 4px solid #00f5ff;
    }

    .workout-completed {
        background: rgba(76, 175, 80, 0.2);
        border: 2px solid #4CAF50;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        margin: 2rem 0;
        animation: celebrate 3s ease-in-out;
    }

    @keyframes celebrate {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }

    .status-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: bold;
        margin: 0.2rem;
    }

    .status-active {
        background: rgba(0, 245, 255, 0.2);
        color: #00f5ff;
        border: 1px solid #00f5ff;
    }

    .status-completed {
        background: rgba(76, 175, 80, 0.2);
        color: #4CAF50;
        border: 1px solid #4CAF50;
    }

    .status-upcoming {
        background: rgba(158, 158, 158, 0.2);
        color: #9e9e9e;
        border: 1px solid #9e9e9e;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    defaults = {
        'workout': [],
        'current_exercise': 0,
        'workout_started': False,
        'workout_completed': False,
        'exercise_completed': [],
        'start_time': None,
        'pause_time': 0,
        'is_paused': False,
        'timer_container': None
    }

    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def format_time(seconds: int) -> str:
    """Format seconds into MM:SS format."""
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins}:{secs:02d}"


def analyze_exercises(exercises: List[Dict]) -> Tuple[List[str], List[str]]:
    """Analyze exercises to determine available equipment and focus areas."""
    equipment_set = set()
    focus_area_set = set()

    for exercise in exercises:
        equipment = exercise.get('equipment', '').lower()
        focus_area = exercise.get('focus_area', '').lower()

        if equipment:
            equipment_set.add(equipment)
        if focus_area:
            focus_area_set.add(focus_area)

    return sorted(equipment_set), sorted(focus_area_set)


def get_current_exercise_time() -> int:
    """Get the current time remaining for the active exercise."""
    if not st.session_state.workout or not st.session_state.workout_started:
        return 0

    current_exercise = st.session_state.workout[st.session_state.current_exercise]
    # Handle both integer and string duration formats
    duration = current_exercise.get('duration', 30)
    if isinstance(duration, str):
        # Extract number from string like "45 seconds"
        total_duration = int(duration.split()[0])
    else:
        total_duration = duration

    if st.session_state.start_time is None or st.session_state.is_paused:
        return total_duration

    elapsed = time.time() - st.session_state.start_time - st.session_state.pause_time
    remaining = max(0, total_duration - int(elapsed))

    return remaining


def start_exercise():
    """Start the current exercise timer."""
    if st.session_state.workout:
        st.session_state.workout_started = True
        st.session_state.start_time = time.time()
        st.session_state.pause_time = 0
        st.session_state.is_paused = False


def pause_exercise():
    """Pause the current exercise timer."""
    if st.session_state.start_time and not st.session_state.is_paused:
        elapsed = time.time() - st.session_state.start_time
        st.session_state.pause_time += elapsed
        st.session_state.is_paused = True


def resume_exercise():
    """Resume the current exercise timer."""
    if st.session_state.workout_started and st.session_state.is_paused:
        st.session_state.start_time = time.time()
        st.session_state.is_paused = False


def next_exercise():
    """Move to the next exercise."""
    if st.session_state.current_exercise < len(st.session_state.workout) - 1:
        # Mark current exercise as completed
        if st.session_state.current_exercise not in st.session_state.exercise_completed:
            st.session_state.exercise_completed.append(st.session_state.current_exercise)
        st.session_state.current_exercise += 1
        st.session_state.start_time = None
        st.session_state.pause_time = 0
        st.session_state.is_paused = False
    else:
        # Mark last exercise as completed
        if st.session_state.current_exercise not in st.session_state.exercise_completed:
            st.session_state.exercise_completed.append(st.session_state.current_exercise)
        # Workout completed
        st.session_state.workout_completed = True
        st.session_state.workout_started = False


def prev_exercise():
    """Move to the previous exercise."""
    if st.session_state.current_exercise > 0:
        st.session_state.current_exercise -= 1
        st.session_state.start_time = None
        st.session_state.pause_time = 0
        st.session_state.is_paused = False
        # Remove from completed if going back
        if st.session_state.current_exercise in st.session_state.exercise_completed:
            st.session_state.exercise_completed.remove(st.session_state.current_exercise)


def reset_workout():
    """Reset the entire workout."""
    st.session_state.workout_started = False
    st.session_state.workout_completed = False
    st.session_state.current_exercise = 0
    st.session_state.start_time = None
    st.session_state.pause_time = 0
    st.session_state.is_paused = False
    st.session_state.exercise_completed = []


def create_download_link(workout: List[Dict]) -> str:
    """Create a download link for the workout plan."""
    try:
        workout_text = "Your 10-Minute Workout Plan\n" + "=" * 50 + "\n\n"
        workout_text += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        for i, exercise in enumerate(workout, 1):
            workout_text += f"{i}. {exercise['name']}\n"

            # Handle duration format
            duration = exercise.get('duration', 30)
            if isinstance(duration, str):
                duration_text = duration
            else:
                duration_text = f"{duration} seconds"

            workout_text += f"Duration: {duration_text}\n"
            workout_text += f"Equipment: {exercise.get('equipment', 'bodyweight').title()}\n"
            workout_text += f"Focus Area: {exercise.get('focus_area', 'full_body').replace('_', ' ').title()}\n"
            workout_text += f"Muscles: {', '.join(exercise.get('muscles_worked', []))}\n"
            workout_text += f"Description: {exercise.get('description', '')}\n\n"

            workout_text += "Instructions:\n"
            for j, instruction in enumerate(exercise.get('instructions', []), 1):
                workout_text += f"  {j}. {instruction}\n"

            workout_text += "\nTips:\n"
            for tip in exercise.get('tips', []):
                workout_text += f"  • {tip}\n"

            workout_text += "\n" + "-" * 50 + "\n\n"

        b64 = base64.b64encode(workout_text.encode('utf-8')).decode()
        href = f'<a href="data:text/plain;base64,{b64}" download="workout_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt">📥 Download Workout Plan</a>'
        return href
    except Exception as e:
        st.error(f"Error creating download link: {e}")
        return ""


def display_timer():
    """Display and update the timer."""
    if st.session_state.workout_started and not st.session_state.workout_completed:
        current_time = get_current_exercise_time()

        # Check if exercise should auto-advance
        if current_time <= 0 and st.session_state.start_time is not None and not st.session_state.is_paused:
            next_exercise()
            st.rerun()

        # Display timer
        timer_class = "timer-display timer-low" if current_time <= 5 else "timer-display"

        # Use a placeholder to update the timer
        if 'timer_placeholder' not in st.session_state:
            st.session_state.timer_placeholder = st.empty()

        st.session_state.timer_placeholder.markdown(
            f'<div class="{timer_class}">{format_time(current_time)}</div>',
            unsafe_allow_html=True
        )

        # Only rerun if timer is actually running
        if st.session_state.start_time is not None and not st.session_state.is_paused and current_time > 0:
            time.sleep(1)
            st.rerun()


def main():
    """Main application function."""
    try:
        ensure_directories_exist()
        init_session_state()
        exercises = load_all_exercises()

        if not exercises:
            st.error("No exercises could be loaded. Please check your setup.")
            return

        # Header
        st.markdown('<div class="main-header">🏋️‍♂️ 10-Minute Workout Generator</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Transform your fitness with personalized quick workouts</div>',
                    unsafe_allow_html=True)

        # Analyze available options
        available_equipment, available_focus_areas = analyze_exercises(exercises)

        # Show available data summary
        st.markdown(f"**Available:** {len(exercises)} exercises | "
                    f"Equipment: {', '.join(available_equipment)} | "
                    f"Focus Areas: {', '.join(available_focus_areas)}")

        # Workout generation controls
        col1, col2, col3 = st.columns(3)

        with col1:
            equipment_options = ['all'] + available_equipment
            equipment_labels = ['All Equipment'] + [eq.replace('_', ' ').title() for eq in available_equipment]
            equipment = st.selectbox(
                "🏋️ Equipment",
                equipment_options,
                format_func=lambda x: equipment_labels[equipment_options.index(x)]
            )

        with col2:
            focus_options = ['all'] + available_focus_areas
            focus_labels = ['All Areas'] + [fa.replace('_', ' ').title() for fa in available_focus_areas]
            focus_area = st.selectbox(
                "🎯 Focus Area",
                focus_options,
                format_func=lambda x: focus_labels[focus_options.index(x)]
            )

        with col3:
            st.write("")  # Spacing
            if st.button("🔄 Generate Workout", type="primary"):
                new_workout = get_random_workout(equipment, focus_area)
                if new_workout:
                    st.session_state.workout = new_workout
                    reset_workout()
                    st.success(f"Generated workout with {len(new_workout)} exercises!")
                    st.rerun()

        # Settings
        with st.expander("⚙️ Settings"):
            show_details = st.checkbox("📋 Show Detailed Instructions", value=True)
            show_images = st.checkbox("🖼️ Show Exercise Images", value=True)
            auto_advance = st.checkbox("⏭️ Auto-advance to next exercise", value=True)

        # Workout display
        if st.session_state.workout:
            st.markdown("---")

            # Workout summary
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("💪 Exercises", len(st.session_state.workout))
            with col2:
                # Handle both duration formats for total time calculation
                total_time = 0
                for ex in st.session_state.workout:
                    duration = ex.get('duration', 30)
                    if isinstance(duration, str):
                        total_time += int(duration.split()[0])
                    else:
                        total_time += duration
                st.metric("⏱️ Total Time", format_time(total_time))
            with col3:
                equipment_display = equipment.replace('_', ' ').title() if equipment != 'all' else 'Mixed'
                st.metric("🎯 Equipment", equipment_display)
            with col4:
                download_link = create_download_link(st.session_state.workout)
                if download_link:
                    st.markdown(download_link, unsafe_allow_html=True)

            # Workout completed message
            if st.session_state.workout_completed:
                st.markdown(f"""
                <div class="workout-completed">
                    <h2>🎉 Workout Complete!</h2>
                    <p>Great job finishing your 10-minute workout!</p>
                    <p>You've completed all {len(st.session_state.workout)} exercises. Keep up the great work!</p>
                </div>
                """, unsafe_allow_html=True)

                if st.button("🔄 Start New Workout", type="primary"):
                    reset_workout()
                    st.rerun()

            # Timer and controls section
            elif st.session_state.workout_started:
                st.markdown("### 🏃‍♀️ Workout Timer")

                # Display timer
                display_timer()

                # Exercise info
                current_exercise = st.session_state.workout[st.session_state.current_exercise]
                st.markdown(
                    f"**Exercise {st.session_state.current_exercise + 1} of {len(st.session_state.workout)}: {current_exercise['name']}**")

                # Progress bar
                progress = (st.session_state.current_exercise + 1) / len(st.session_state.workout)
                st.progress(progress)

                # Timer controls
                col1, col2, col3, col4, col5 = st.columns(5)

                with col1:
                    if st.button("⏮️ Previous", disabled=st.session_state.current_exercise == 0):
                        prev_exercise()
                        st.rerun()

                with col2:
                    if st.session_state.is_paused or st.session_state.start_time is None:
                        if st.button("▶️ Start/Resume"):
                            resume_exercise()
                            st.rerun()
                    else:
                        if st.button("⏸️ Pause"):
                            pause_exercise()
                            st.rerun()

                with col3:
                    if st.button("🔄 Reset Exercise"):
                        st.session_state.start_time = None
                        st.session_state.pause_time = 0
                        st.session_state.is_paused = False
                        st.rerun()

                with col4:
                    if st.button("⏭️ Next",
                                 disabled=st.session_state.current_exercise >= len(st.session_state.workout) - 1):
                        next_exercise()
                        st.rerun()

                with col5:
                    if st.button("⏹️ Stop"):
                        reset_workout()
                        st.rerun()

            # Start workout button (when workout not started)
            else:
                st.markdown("### 🚀 Ready to Start?")
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    if st.button("🚀 Start Workout", type="primary", use_container_width=True):
                        start_exercise()
                        st.rerun()

            # Exercise cards
            st.markdown("### 📋 Exercise Details")

            for i, exercise in enumerate(st.session_state.workout):
                # Determine card status
                if i in st.session_state.exercise_completed:
                    status = "completed"
                    status_badge = '<span class="status-badge status-completed">✅ Completed</span>'
                elif st.session_state.workout_started and i == st.session_state.current_exercise:
                    status = "active"
                    status_badge = '<span class="status-badge status-active">🏃‍♀️ Active</span>'
                else:
                    status = "upcoming"
                    status_badge = '<span class="status-badge status-upcoming">⏳ Upcoming</span>'

                card_class = "exercise-card current-exercise" if status == "active" else "exercise-card"

                with st.container():
                    st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)

                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{i + 1}. {exercise['name']}**")
                        st.markdown(status_badge, unsafe_allow_html=True)

                        # Handle duration display
                        duration = exercise.get('duration', 30)
                        if isinstance(duration, str):
                            duration_text = duration
                        else:
                            duration_text = f"{duration} seconds"
                        st.markdown(f"⏱️ {duration_text}")

                        # Display muscle tags
                        muscles_html = "".join(
                            [f'<span class="muscle-tag">{muscle}</span>' for muscle in
                             exercise.get('muscles_worked', [])])
                        st.markdown(muscles_html, unsafe_allow_html=True)

                        st.markdown(f"*{exercise.get('description', 'No description available')}*")

                        if show_details:
                            st.markdown("**How to Perform:**")
                            for j, instruction in enumerate(exercise.get('instructions', []), 1):
                                st.markdown(f"{j}. {instruction}")

                            st.markdown("**💡 Tips:**")
                            for tip in exercise.get('tips', []):
                                st.markdown(f"• {tip}")

                    with col2:
                        if show_images:
                            image_path = ensure_image(exercise)
                            if image_path and os.path.exists(image_path):
                                st.image(image_path, width=200)
                            else:
                                st.markdown("🏋️‍♂️")  # Fallback emoji if no image

                    st.markdown('</div>', unsafe_allow_html=True)

        else:
            st.info("Click 'Generate Workout' to create your personalized 10-minute workout!")

        # Quick tips
        st.markdown("---")
        st.markdown("### 💡 Quick Tips")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div class="tip-box">', unsafe_allow_html=True)
            st.markdown("**🌱 Beginner?** Start with bodyweight exercises and focus on form over speed.")
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="tip-box">', unsafe_allow_html=True)
            st.markdown("**🔥 Advanced?** Try adding dumbbells or increase duration for more challenge.")
            st.markdown('</div>', unsafe_allow_html=True)

        with col3:
            st.markdown('<div class="tip-box">', unsafe_allow_html=True)
            st.markdown(
                "**⏰ Time-based:** Perform each exercise for the suggested duration with 10-15 second rest between exercises.")
            st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("Please try refreshing the page or generating a new workout.")


if __name__ == "__main__":
    main()