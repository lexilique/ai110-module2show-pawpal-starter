"""Tests for the PawPal+ core domain model."""

from datetime import date

from pawpal_system import Owner, Pet, DailyTasks, Scheduler


def test_mark_complete_changes_status():
    """mark_complete() flips a task from not-done to done."""
    task = DailyTasks("Morning walk", task_type="walk", duration_mins=30, priority="high")

    assert task.is_completed is False  # starts incomplete
    task.mark_complete()
    assert task.is_completed is True   # now marked done


def test_add_task_increases_pet_task_count():
    """Adding a task to a Pet grows that pet's task list by one."""
    pet = Pet("Luna", species="dog", breed="Golden Retriever", age=3)

    assert len(pet.tasks) == 0  # no tasks yet
    pet.add_task(DailyTasks("Feeding", task_type="feed", duration_mins=10, priority="high"))
    assert len(pet.tasks) == 1  # exactly one after adding


# --- helpers ---------------------------------------------------------------

def _scheduler_with(tasks, time_availability=120):
    """Build an Owner/Pet/Scheduler around a list of tasks for testing."""
    pet = Pet("Luna", species="dog", breed="Golden Retriever", age=3)
    for task in tasks:
        pet.add_task(task)
    owner = Owner("Alexa", time_availability=time_availability)
    owner.add_pet(pet)
    return Scheduler(owner)


# --- sorting correctness ---------------------------------------------------

def test_sort_by_time_returns_chronological_order():
    """sort_by_time() orders tasks by preferred start time, earliest first."""
    noon = DailyTasks("Brush fur", task_type="grooming", duration_mins=20,
                      priority="low", time_start="12:00")
    early = DailyTasks("Morning walk", task_type="walk", duration_mins=30,
                       priority="high", time_start="08:00")
    mid = DailyTasks("Give meds", task_type="meds", duration_mins=5,
                     priority="medium", time_start="09:30")

    scheduler = _scheduler_with([noon, early, mid])
    ordered = scheduler.sort_by_time(scheduler.all_tasks())

    assert [t.time_start for t in ordered] == ["08:00", "09:30", "12:00"]


def test_sort_by_time_pushes_blank_times_to_end():
    """Tasks with no preferred time sort after every timed task."""
    timed = DailyTasks("Walk", task_type="walk", duration_mins=30,
                       priority="high", time_start="10:00")
    untimed = DailyTasks("Play", task_type="enrichment", duration_mins=15,
                         priority="low")  # time_start defaults to ""

    scheduler = _scheduler_with([untimed, timed])
    ordered = scheduler.sort_by_time(scheduler.all_tasks())

    assert ordered[0] is timed and ordered[1] is untimed


# --- recurrence logic ------------------------------------------------------

def test_daily_task_completion_creates_next_day_task():
    """Completing a daily task spawns a new occurrence due the following day."""
    pet = Pet("Luna", species="dog", breed="Golden Retriever", age=3)
    task = DailyTasks("Morning walk", task_type="walk", duration_mins=30,
                      priority="high", frequency="daily", due_date=date(2026, 7, 7))
    pet.add_task(task)

    upcoming = task.mark_complete()

    assert upcoming is not None
    assert upcoming.due_date == date(2026, 7, 8)   # one day later
    assert upcoming.is_completed is False          # the new one is pending
    assert len(pet.tasks) == 2                      # respawn added to the pet
    assert pet.tasks[1] is upcoming


def test_once_task_completion_does_not_respawn():
    """A one-off task produces no follow-up and leaves the task list unchanged."""
    pet = Pet("Luna", species="dog", breed="Golden Retriever", age=3)
    task = DailyTasks("Vet visit", task_type="meds", duration_mins=45,
                      priority="high", frequency="once")
    pet.add_task(task)

    upcoming = task.mark_complete()

    assert upcoming is None
    assert len(pet.tasks) == 1


# --- conflict detection ----------------------------------------------------

def test_detect_conflicts_flags_duplicate_times():
    """Two pending tasks sharing a start time are reported as a conflict."""
    a = DailyTasks("Walk", task_type="walk", duration_mins=30,
                   priority="high", time_start="09:00")
    b = DailyTasks("Feed", task_type="feed", duration_mins=10,
                   priority="high", time_start="09:00")

    scheduler = _scheduler_with([a, b])
    warning = scheduler.detect_conflicts()

    assert "09:00" in warning
    assert "Conflict warning" in warning


def test_detect_conflicts_returns_empty_when_no_clash():
    """Distinct start times produce no warning (falsy string)."""
    a = DailyTasks("Walk", task_type="walk", duration_mins=30,
                   priority="high", time_start="08:00")
    b = DailyTasks("Feed", task_type="feed", duration_mins=10,
                   priority="high", time_start="09:00")

    scheduler = _scheduler_with([a, b])

    assert scheduler.detect_conflicts() == ""


def test_detect_conflicts_ignores_completed_tasks():
    """A completed task at the same time as a pending one is not a conflict."""
    pending = DailyTasks("Walk", task_type="walk", duration_mins=30,
                         priority="high", time_start="09:00")
    done = DailyTasks("Feed", task_type="feed", duration_mins=10,
                      priority="high", time_start="09:00", is_completed=True)

    scheduler = _scheduler_with([pending, done])

    assert scheduler.detect_conflicts() == ""


# --- scheduling / budget edge cases ----------------------------------------

def test_generate_plan_lays_tasks_back_to_back():
    """Tasks that fit are placed sequentially from the default day start."""
    walk = DailyTasks("Walk", task_type="walk", duration_mins=30,
                      priority="high", time_start="08:00")
    feed = DailyTasks("Feed", task_type="feed", duration_mins=10,
                      priority="high", time_start="09:00")

    scheduler = _scheduler_with([walk, feed], time_availability=120)
    plan = scheduler.generate_plan()

    assert [(start, end) for _t, start, end in plan] == [("08:00", "08:30"),
                                                         ("08:30", "08:40")]
    assert scheduler.skipped == []


def test_generate_plan_skips_oversized_but_keeps_scheduling():
    """A task too big to fit is skipped, yet a later smaller task still fits."""
    big = DailyTasks("Long hike", task_type="walk", duration_mins=90,
                     priority="high", time_start="08:00")
    small = DailyTasks("Quick feed", task_type="feed", duration_mins=10,
                       priority="high", time_start="09:00")

    scheduler = _scheduler_with([big, small], time_availability=30)
    plan = scheduler.generate_plan()

    assert [t.name for t, _s, _e in plan] == ["Quick feed"]
    assert [t.name for t in scheduler.skipped] == ["Long hike"]


def test_generate_plan_with_zero_availability_skips_everything():
    """With no time budget, nothing is scheduled and nothing crashes."""
    task = DailyTasks("Walk", task_type="walk", duration_mins=30,
                      priority="high", time_start="08:00")

    scheduler = _scheduler_with([task], time_availability=0)
    plan = scheduler.generate_plan()

    assert plan == []
    assert len(scheduler.skipped) == 1


def test_empty_owner_generates_empty_plan():
    """An owner with no pets/tasks yields an empty plan without error."""
    owner = Owner("Alexa", time_availability=90)
    scheduler = Scheduler(owner)

    assert scheduler.generate_plan() == []
    assert "nothing scheduled" in scheduler.explain()
