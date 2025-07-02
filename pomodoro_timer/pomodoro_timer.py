import time
import argparse
from datetime import datetime

def format_time(seconds):
    """Formats seconds into MM:SS string."""
    return f"{seconds // 60:02d}:{seconds % 60:02d}"

def countdown(duration, session_type):
    """Runs a countdown for a given duration."""
    while duration >= 0:
        print(f"{session_type}: {format_time(duration)}", end='\r')
        time.sleep(1)
        duration -= 1
    print()

def log_session(session_type, duration_minutes):
    """Logs session details to a file."""
    with open("pomodoro_log.txt", "a") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{timestamp} - {session_type}: {duration_minutes} minutes\n")

def main():
    """Main function to run the Pomodoro timer."""
    parser = argparse.ArgumentParser(description="A simple command-line Pomodoro timer.")
    parser.add_argument("-w", "--work", type=int, default=25, help="Work session duration in minutes.")
    parser.add_argument("-b", "--break", type=int, default=5, help="Break session duration in minutes.", dest="break_duration")
    args = parser.parse_args()

    work_duration_minutes = args.work
    break_duration_minutes = args.break_duration
    work_duration_seconds = work_duration_minutes * 60
    break_duration_seconds = break_duration_minutes * 60
    session_count = 0

    print("Starting Pomodoro timer. Press Ctrl+C to exit.")

    try:
        while True:
            # Work session
            countdown(work_duration_seconds, "Work")
            log_session("Work", work_duration_minutes)
            session_count += 1
            print(f"Work session complete! Sessions completed: {session_count}")

            # Break session
            countdown(break_duration_seconds, "Break")
            log_session("Break", break_duration_minutes)
            print("Break session complete!")

    except KeyboardInterrupt:
        print("\nPomodoro timer stopped.")

if __name__ == "__main__":
    main()
