"""PawPal+ demo script.

Builds a small owner/pets/tasks scenario and prints today's schedule to the
terminal. Run it with:  python main.py
"""

from pawpal_system import Owner, Pet, DailyTasks, Scheduler


def build_scenario() -> Owner:
    """Create an owner with two pets and a handful of care tasks."""
    owner = Owner("Alexa", time_availability=90)

    logan = Pet("Logan", species="dog", breed="Shi Tzu and Poodle", age=7)
    mimo = Pet("Mimo", species="dog", breed="Bichon Frise", age=6)
    owner.add_pet(logan)
    owner.add_pet(mimo)

    # At least three tasks, each with a different preferred time.
    logan.add_task(
        DailyTasks("Morning walk", task_type="walk", duration_mins=30,
                   priority="high", time_start="08:00")
    )
    logan.add_task(
        DailyTasks("Dinner", task_type="feed", duration_mins=10,
                   priority="high", time_start="18:00")
    )
    mimo.add_task(
        DailyTasks("Give meds", task_type="meds", duration_mins=5,
                   priority="medium", time_start="09:00")
    )
    mimo.add_task(
        DailyTasks("Brush fur", task_type="grooming", duration_mins=20,
                   priority="low", time_start="12:00")
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


if __name__ == "__main__":
    main()
