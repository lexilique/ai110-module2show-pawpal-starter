"""PawPal+ core domain model.

Four classes model the pet-care planning problem:
  - DailyTasks : a single care activity (what, how long, how urgent, done?)
  - Pet        : a pet and the tasks it needs
  - Owner      : a person who manages one or more pets
  - Scheduler  : the "brain" that gathers tasks and builds a daily plan

Scheduling strategy is priority-first greedy: sort tasks high -> low, then place
them back-to-back from the start of the day until the owner's time budget runs
out; anything that doesn't fit is skipped.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Maps the priority strings to sortable scores (higher = more urgent).
PRIORITY_SCORES = {"high": 3, "medium": 2, "low": 1}

# When the planned day starts. Tasks are laid out sequentially from here.
DEFAULT_DAY_START = "08:00"


def _to_minutes(hhmm: str) -> int:
    """Convert an "HH:MM" clock string to minutes since midnight."""
    hours, minutes = hhmm.split(":")
    return int(hours) * 60 + int(minutes)


def _to_hhmm(total_minutes: int) -> str:
    """Convert minutes since midnight back to an "HH:MM" clock string."""
    total_minutes %= 24 * 60  # wrap around midnight, just in case
    return f"{total_minutes // 60:02d}:{total_minutes % 60:02d}"


@dataclass
class DailyTasks:
    """One pet-care task: what to do, how long it takes, and how urgent it is."""

    name: str
    # Back-reference to the owning pet, so the scheduler can say WHICH pet a task
    # belongs to when building/explaining the plan (#1). Set automatically by
    # Pet.add_task(). kw_only keeps it out of the positional-field ordering, and
    # repr=False avoids an infinite Pet <-> DailyTasks repr loop.
    pet: "Pet | None" = field(default=None, repr=False, kw_only=True)
    task_type: str          # e.g. "walk", "feed", "meds", "enrichment", "grooming"
    duration_mins: int
    priority: str           # "low" | "medium" | "high"
    time_start: str = ""    # optional PREFERRED/fixed time, e.g. "08:00"
    is_completed: bool = False

    def priority_level(self) -> int:
        """Return a sortable priority score (high=3/med=2/low=1; unknown=0)."""
        return PRIORITY_SCORES.get(self.priority.lower().strip(), 0)

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.is_completed = True

    def describe(self) -> str:
        """Return a human-readable one-line summary of this task."""
        detail = f"{self.task_type}, {self.duration_mins} min, priority: {self.priority}"
        if self.time_start:
            detail += f", preferred {self.time_start}"
        status = " [done]" if self.is_completed else ""
        return f"{self.name} ({detail}){status}"


@dataclass
class Pet:
    """A pet and the care tasks it needs."""

    name: str
    species: str
    breed: str
    age: int
    tasks: list[DailyTasks] = field(default_factory=list)

    def add_task(self, task: DailyTasks) -> None:
        """Add a task to this pet's list and back-link it to this pet."""
        task.pet = self          # keep the DailyTasks.pet back-reference in sync (#1)
        self.tasks.append(task)

    def edit_task(self, index: int, changes: dict) -> None:
        """Update the task at `index` from a {field: value} dict of changes."""
        task = self.tasks[index]
        for field_name, value in changes.items():
            if not hasattr(task, field_name):
                raise AttributeError(f"DailyTasks has no field '{field_name}'")
            setattr(task, field_name, value)

    def remove_task(self, index: int) -> None:
        """Remove the task at the given index."""
        del self.tasks[index]


@dataclass
class Owner:
    """The pet owner we're planning for."""

    name: str
    time_availability: int  # total minutes available for pet care today
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)


class Scheduler:
    """The brain: builds and explains a daily plan from the owner's tasks."""

    def __init__(self, owner: Owner) -> None:
        """Bind the scheduler to an owner and start with an empty plan."""
        self.owner = owner
        # Each plan entry records WHEN a scheduled task happens (#2):
        #   (task: DailyTasks, start_time: str, end_time: str)
        # The task carries its own .pet back-reference (#1), so entries don't
        # need to repeat it. Times are "HH:MM" strings.
        self.plan: list[tuple[DailyTasks, str, str]] = []
        self.skipped: list[DailyTasks] = []

    def all_tasks(self) -> list[DailyTasks]:
        """Gather every task across all of the owner's pets."""
        return [task for pet in self.owner.pets for task in pet.tasks]

    def priority_sort(self, tasks: list[DailyTasks]) -> list[DailyTasks]:
        """Return tasks ordered by priority (high first), ties by shorter duration."""
        return sorted(tasks, key=lambda t: (-t.priority_level(), t.duration_mins))

    def generate_plan(self) -> list:
        """Greedily schedule pending tasks by priority into the time budget."""
        self.plan = []
        self.skipped = []

        pending = [task for task in self.all_tasks() if not task.is_completed]
        ordered = self.priority_sort(pending)

        remaining = self.owner.time_availability
        clock = _to_minutes(DEFAULT_DAY_START)

        for task in ordered:
            if task.duration_mins <= remaining:
                start, end = clock, clock + task.duration_mins
                self.plan.append((task, _to_hhmm(start), _to_hhmm(end)))
                clock = end
                remaining -= task.duration_mins
            else:
                self.skipped.append(task)

        return self.plan

    def explain(self) -> str:
        """Explain why each task was chosen or skipped."""
        used = sum(task.duration_mins for task, _start, _end in self.plan)
        lines = [
            f"Daily plan for {self.owner.name} "
            f"({used} of {self.owner.time_availability} min used):"
        ]

        if self.plan:
            for task, start, end in self.plan:
                pet_name = task.pet.name if task.pet else "Unknown pet"
                lines.append(
                    f"  {start}-{end} — {pet_name}: {task.describe()} "
                    f"→ chosen (priority {task.priority}, fit the remaining time)"
                )
        else:
            lines.append("  (nothing scheduled)")

        if self.skipped:
            lines.append("Skipped — ran out of time:")
            for task in self.skipped:
                pet_name = task.pet.name if task.pet else "Unknown pet"
                lines.append(
                    f"  - {pet_name}: {task.describe()} "
                    f"→ skipped (not enough time left)"
                )

        return "\n".join(lines)
