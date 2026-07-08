"""PawPal+ core domain model (skeleton).

Class stubs generated from diagrams/uml.mmd. Attributes and method signatures
only -- no logic yet. Fill in the method bodies incrementally.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DailyTasks:
    """One pet-care task: what to do, how long it takes, and how urgent it is."""

    name: str
    task_type: str          # e.g. "walk", "feed", "meds", "enrichment", "grooming"
    duration_mins: int
    priority: str           # "low" | "medium" | "high"
    time_start: str = ""    # optional fixed time, e.g. "08:00"
    is_completed: bool = False

    def priority_level(self) -> int:
        """Return a sortable score for this task's priority (high=3/med=2/low=1)."""
        # TODO: map self.priority string to an int
        raise NotImplementedError

    def mark_complete(self) -> None:
        """Mark this task as done."""
        # TODO: set self.is_completed
        raise NotImplementedError

    def describe(self) -> str:
        """Return a human-readable one-line summary of this task."""
        # TODO: build a display string
        raise NotImplementedError


@dataclass
class Pet:
    """A pet and the care tasks it needs."""

    name: str
    species: str
    breed: str
    age: int
    tasks: list[DailyTasks] = field(default_factory=list)

    def add_task(self, task: DailyTasks) -> None:
        """Add a task to this pet's list."""
        # TODO: append task to self.tasks
        raise NotImplementedError

    def edit_task(self, index: int, changes: dict) -> None:
        """Update fields of the task at the given index."""
        # TODO: apply changes to self.tasks[index]
        raise NotImplementedError

    def remove_task(self, index: int) -> None:
        """Remove the task at the given index."""
        # TODO: delete self.tasks[index]
        raise NotImplementedError


@dataclass
class Owner:
    """The pet owner we're planning for."""

    name: str
    time_availability: int  # total minutes available for pet care today
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        # TODO: append pet to self.pets
        raise NotImplementedError


class Scheduler:
    """The brain: builds and explains a daily plan from the owner's tasks."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner
        self.plan: list = []          # last generated schedule
        self.skipped: list[DailyTasks] = []

    def all_tasks(self) -> list[DailyTasks]:
        """Gather every task across all of the owner's pets."""
        # TODO: collect tasks from each pet
        raise NotImplementedError

    def priority_sort(self, tasks: list[DailyTasks]) -> list[DailyTasks]:
        """Return tasks ordered by priority (high first)."""
        # TODO: sort using DailyTasks.priority_level()
        raise NotImplementedError

    def generate_plan(self) -> list:
        """Greedily place tasks into the time budget; skip what doesn't fit."""
        # TODO: fill self.plan / self.skipped based on owner.time_availability
        raise NotImplementedError

    def explain(self) -> str:
        """Explain why each task was chosen or skipped."""
        # TODO: build reasoning text from self.plan / self.skipped
        raise NotImplementedError
