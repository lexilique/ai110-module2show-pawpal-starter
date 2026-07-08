"""PawPal+ demo script.

Builds a small owner/pets/tasks scenario and prints today's schedule to the
terminal. Run it with:  python main.py
"""

from datetime import date

from pawpal_system import Owner, Pet, DailyTasks, Scheduler


def build_scenario() -> Owner:
    """Create an owner with two pets and a handful of care tasks."""
    owner = Owner("Alexa", time_availability=90)

    logan = Pet("Logan", species="dog", breed="Shi Tzu and Poodle", age=7)
    mimo = Pet("Mimo", species="dog", breed="Bichon Frise", age=6)
    owner.add_pet(logan)
    owner.add_pet(mimo)

    today = date.today()

    # At least three tasks, each with a different preferred time and a
    # recurrence: daily chores repeat tomorrow, grooming repeats next week.
    logan.add_task(
        DailyTasks("Dinner", task_type="feed", duration_mins=10,
                   priority="high", time_start="18:00",
                   frequency="daily", due_date=today)
    )

    mimo.add_task(
        DailyTasks("Brush fur", task_type="grooming", duration_mins=20,
                   priority="low", time_start="12:00",
                   frequency="weekly", due_date=today)
    )

    logan.add_task(
        DailyTasks("Morning walk", task_type="walk", duration_mins=30,
                   priority="high", time_start="08:00",
                   frequency="daily", due_date=today)
    )

    mimo.add_task(
        DailyTasks("Give meds", task_type="meds", duration_mins=5,
                   priority="medium", time_start="09:00",
                   frequency="daily", due_date=today)
    )

    # Deliberate clash: Logan's breakfast wants 09:00, the same slot as Mimo's
    # meds above — used to exercise the Scheduler's conflict detection.
    logan.add_task(
        DailyTasks("Breakfast", task_type="feed", duration_mins=10,
                   priority="high", time_start="09:00",
                   frequency="daily", due_date=today)
    )

    return owner


def main() -> None:
    owner = build_scenario()
    scheduler = Scheduler(owner)
    scheduler.generate_plan()

    print("=" * 48)
    print("Today's Schedule")
    print("=" * 48)
    print(scheduler.explain())

    # Lightweight conflict check — prints a warning if any tasks share a time,
    # otherwise stays quiet. Never raises, so it can't break the schedule.
    warning = scheduler.detect_conflicts()
    if warning:
        print("\n" + warning)

    # Complete the daily morning walk -> a fresh occurrence auto-appears for
    # tomorrow, so the routine never has to be re-entered by hand.
    walk = next(t for pet in owner.pets for t in pet.tasks if t.name == "Morning walk")
    upcoming = walk.mark_complete()
    print("\n" + "=" * 48)
    print(f"Completed '{walk.name}'. "
          f"Next occurrence due {upcoming.due_date} ({upcoming.frequency}).")


if __name__ == "__main__":
    main()
