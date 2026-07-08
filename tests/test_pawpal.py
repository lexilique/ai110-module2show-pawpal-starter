"""Tests for the PawPal+ core domain model."""

from pawpal_system import Pet, DailyTasks


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
