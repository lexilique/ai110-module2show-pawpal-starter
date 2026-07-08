"""PawPal+ core domain model.

Four classes model the pet-care planning problem:
  - DailyTasks : a single care activity (what, how long, how urgent, done?)
  - Pet        : a pet and the tasks it needs
  - Owner      : a person who manages one or more pets
  - Scheduler  : the "brain" that gathers tasks and builds a daily plan

Scheduling strategy is time-ordered greedy: sort tasks by preferred start time,
then place them back-to-back from the start of the day until the owner's time
budget runs out; anything that doesn't fit is skipped. Recurring tasks respawn
on completion, and a lightweight check warns about tasks sharing a start time.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta

# Maps the priority strings to sortable scores (higher = more urgent).
PRIORITY_SCORES = {"high": 3, "medium": 2, "low": 1}

# How far ahead the next occurrence of a recurring task lands. "once" (the
# default) means the task does not repeat, so it maps to None.
RECURRENCE_STEPS = {
    "daily": timedelta(days=1),
    "weekly": timedelta(weeks=1),
}

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
    frequency: str = "once"  # "once" | "daily" | "weekly"
    due_date: date | None = None  # the day this occurrence is due
    is_completed: bool = False

    def priority_level(self) -> int:
        """Return a sortable priority score (high=3/med=2/low=1; unknown=0)."""
        return PRIORITY_SCORES.get(self.priority.lower().strip(), 0)

    def next_occurrence(self) -> "DailyTasks | None":
        """Build the next occurrence of a recurring task, or None if one-off.

        Uses timedelta so date math is accurate across month/year boundaries.
        The next due date is measured from this task's own due_date (falling
        back to today if it has none), so completing a task late doesn't drift
        the whole series forward.
        """
        step = RECURRENCE_STEPS.get(self.frequency.lower().strip())
        if step is None:
            return None  # "once" or unrecognized -> does not repeat

        base = self.due_date or date.today()
        return DailyTasks(
            name=self.name,
            task_type=self.task_type,
            duration_mins=self.duration_mins,
            priority=self.priority,
            time_start=self.time_start,
            frequency=self.frequency,
            due_date=base + step,
        )

    def mark_complete(self) -> "DailyTasks | None":
        """Mark this task done; if it recurs, spawn and return the next one.

        A recurring task's follow-up is added to the same pet automatically via
        the .pet back-reference, so the schedule refills itself. Returns the new
        occurrence (or None for a one-off task).
        """
        self.is_completed = True

        upcoming = self.next_occurrence()
        if upcoming is not None and self.pet is not None:
            self.pet.add_task(upcoming)
        return upcoming

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

    def filter_by_completion(self, completed: bool) -> list[DailyTasks]:
        """Return tasks matching the given completion status.

        `filter_by_completion(False)` gives the still-to-do (pending) tasks;
        `filter_by_completion(True)` gives the ones already marked done.
        """
        return [task for task in self.all_tasks() if task.is_completed == completed]

    def priority_sort(self, tasks: list[DailyTasks]) -> list[DailyTasks]:
        """Return tasks ordered by priority (high first), ties by shorter duration."""
        return sorted(tasks, key=lambda t: (-t.priority_level(), t.duration_mins))

    def sort_by_time(self, tasks: list[DailyTasks]) -> list[DailyTasks]:
        """Return tasks ordered by preferred start time (earliest first).

        The lambda `key` converts each task's "HH:MM" `time_start` into minutes
        since midnight so the sort compares clock times, not raw strings. Tasks
        with no preferred time ("") are pushed to the end via a large sentinel.
        """
        return sorted(
            tasks,
            key=lambda t: _to_minutes(t.time_start) if t.time_start else 24 * 60,
        )

    def generate_plan(self) -> list:
        """Greedily schedule pending tasks into the owner's time budget.

        Pending tasks are ordered by preferred start time (via `sort_by_time`),
        then laid out back-to-back from DEFAULT_DAY_START. Each task that fits
        the remaining minutes is placed and given a start/end; anything that no
        longer fits is recorded in `self.skipped`. Returns the built plan.
        """
        self.plan = []
        self.skipped = []

        pending = self.filter_by_completion(completed=False)
        ordered = self.sort_by_time(pending)

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

    def detect_conflicts(self) -> str:
        """Lightweight check for tasks that want the same preferred start time.

        Groups every pending task that has a `time_start` by that time and
        flags any clock time claimed by more than one task — whether they
        belong to the same pet or different pets. Returns a human-readable
        warning string, or "" when nothing clashes, so callers can simply do
        `if scheduler.detect_conflicts(): ...` without any risk of crashing.
        """
        by_time: dict[str, list[DailyTasks]] = {}
        for task in self.filter_by_completion(completed=False):
            if task.time_start:
                by_time.setdefault(task.time_start, []).append(task)

        lines = []
        for start in sorted(by_time, key=_to_minutes):
            clashing = by_time[start]
            if len(clashing) > 1:
                who = ", ".join(
                    f"{t.pet.name if t.pet else 'Unknown pet'}'s '{t.name}'"
                    for t in clashing
                )
                lines.append(f"  ! {start} — {who}")

        if not lines:
            return ""
        return "Conflict warning: multiple tasks share a start time:\n" + "\n".join(lines)

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
