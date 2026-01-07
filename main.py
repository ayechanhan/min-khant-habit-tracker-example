import fire
from datetime import datetime
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
import json
from pathlib import Path

from models.habits import Base, Habit
from helpers.common import check_habit_exists

load_dotenv()


class HabitTracker:
    def __init__(self):
        self.habits = []
        self.engine = create_engine(
            f"sqlite:///{os.getenv('DB_PATH')}", echo=False, future=True
        )
        Base.metadata.create_all(self.engine)

    def seed(self):
        p = Path(os.getenv("SEED_PATH"))
        if not p.exists():
            print("Seed file not found.")
            return

        data = json.loads(p.read_text(encoding="utf-8"))
        habits = data.get("habits", [])
        if not isinstance(habits, list) or not habits:
            return "Empty habits to seed."

        created = 0
        skipped = 0

        with Session(self.engine) as session:
            for item in habits:
                if not isinstance(item, dict):
                    continue

                name = (item.get("habit_name") or "").strip()
                if not name:
                    continue

                periodicity = item.get("periodicity", "daily")
                ongoing = item.get("ongoing", True)
                streak = item.get("streak", 0)

                existing = session.scalar(select(Habit).where(Habit.habit_name == name))

                if existing:
                    skipped += 1
                    habit = existing
                else:
                    habit = Habit(
                        habit_name=name,
                        periodicity=periodicity,
                        on_going=ongoing,
                        streak=streak,
                    )
                    session.add(habit)
                    session.flush()
                    created += 1

            session.commit()

        return f"Seeding completed. Created: {created}, Skipped: {skipped}"

    def run(self):
        """Interactive menu."""
        print("Welcome from Habit Manager APP\n")

        while True:
            print("\nMenu:")
            print("  1) Habit Management")
            print("  2) Habit Analytics")
            print("  3) Exit")
            print("  4) Test DB connection")

            choice = input("\nSelect (1-4): ").strip()

            try:
                match choice:
                    case "1":
                        print("Choose one of the following options below: ")
                        print("  1) Create Habit")
                        print("  2) Update Habit Name")
                        print("  3) Delete Existing Habit")
                        print("  4) Show Existing Habits")

                        habit_menu_choice = input("\nSelect (1-4): ").strip()

                        match habit_menu_choice:
                            case "1":
                                habit_data = dict()
                                habit_data["name"] = input("Enter Habit Name: ").strip()
                                periodicity = (
                                    input("Enter Periodicity (daily/weekly/monthly): ")
                                    .strip()
                                    .lower()
                                )
                                while periodicity not in [
                                    "daily",
                                    "weekly",
                                    "monthly",
                                ]:
                                    print(
                                        "Invalid periodicity. Please enter daily, weekly, or monthly."
                                    )
                                    periodicity = (
                                        input(
                                            "Enter Periodicity (daily/weekly/monthly): "
                                        )
                                        .strip()
                                        .lower()
                                    )
                                habit_data["periodicity"] = periodicity
                                habit_data["created_at"] = datetime.now().strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                )
                                habit_data["updated_at"] = datetime.now().strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                )
                                habit_data["ongoing"] = True
                                habit_data["streak"] = 0
                                self.habits.append(habit_data)
                                print(
                                    f"Habit '{habit_data['name']}' created successfully."
                                )
                            case "2":
                                habit = input(
                                    "Enter the name of the habit to update: "
                                ).strip()
                                if check_habit_exists(self.habits, habit):
                                    new_name = input(
                                        "Enter the new name for the habit: "
                                    ).strip()
                                    for h in self.habits:
                                        if h["name"] == habit:
                                            h["name"] = new_name
                                            h["updated_at"] = datetime.now().strftime(
                                                "%Y-%m-%d %H:%M:%S"
                                            )
                                            print(
                                                f"Habit name updated to '{new_name}'."
                                            )
                                            break
                                else:
                                    print(f"Habit '{habit}' does not exist.")
                            case "3":
                                habit = input(
                                    "Enter the name of the habit to delete: "
                                ).strip()
                                if check_habit_exists(self.habits, habit):
                                    self.habits = [
                                        h for h in self.habits if h["name"] != habit
                                    ]
                                    print(f"Habit '{habit}' deleted successfully.")
                                else:
                                    print(f"Habit '{habit}' does not exist.")
                            case "4":
                                if not self.habits:
                                    print("No existing habits.")
                                else:
                                    print("Existing Habits:")
                                    for idx, habit in enumerate(self.habits, start=1):
                                        print(
                                            f"  {idx}. {habit['name']} (Periodicity: {habit['periodicity']}, Streak: {habit['streak']})"
                                        )
                            case _:
                                print("Invalid choice. Please select a valid option.")
                    case "2":
                        print("  1) Longest Streak Overall")
                        print("  2) Longest Streak by Habit")
                        print("  3) List By Period")
                        print("  4) Broken Habits")
                        print("  5) Back to Main Menu")

                        analytics_menu_choice = input("\nSelect (1-5): ").strip()

                    case "3":
                        print("Exiting...")
                        return
                    case "4":
                        with Session(self.engine) as session:
                            get_habits = select(Habit).order_by(Habit.id.asc())
                            habits = session.execute(get_habits).scalars().all()
                            for habit in habits:
                                print(
                                    f"""Habit: {habit.habit_name},\nPeriodicity: {habit.periodicity},\nOngoing: {habit.on_going}\nStreak: {habit.streak}"""
                                )

                    case _:
                        print("Invalid choice. Please select a valid option.")
            except KeyboardInterrupt:
                print("\nBye 👋")
                return


if __name__ == "__main__":
    fire.Fire(HabitTracker)
