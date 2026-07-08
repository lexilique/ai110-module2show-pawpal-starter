# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

================================================
Today's Schedule
================================================
Daily plan for Alexa (65 of 90 min used):
  08:00-08:10 — Logan: Dinner (feed, 10 min, priority: high, preferred 18:00) → chosen (priority high, fit the remaining time)
  08:10-08:40 — Logan: Morning walk (walk, 30 min, priority: high, preferred 08:00) → chosen (priority high, fit the remaining time)
  08:40-08:45 — Mimo: Give meds (meds, 5 min, priority: medium, preferred 09:00) → chosen (priority medium, fit the remaining time)
  08:45-09:05 — Mimo: Brush fur (grooming, 20 min, priority: low, preferred 12:00) → chosen (priority low, fit the remaining time)

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here

tests/test_pawpal.py .............                            [100%]

======================== 13 passed in 0.05s =========================
```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | sort_by_time() | sorts by each tasks' start time |
| Filtering | filter_by_completion(completed)| filters tasks by completion|
| Conflict handling | detect_conflicts() | filters and notifies user about any conflicts like overlapping start times |
| Recurring tasks | next_occurrence(), mark_complete()|if recurring task is marked as complete it is returned again in the next plan|

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. A user is able to add an owner with a name and their time availability. A Pet can also be assigned to them along with basic pet information
2. After adding an owner and pet, you can assign tasks to a pet. Tasks can be given a priority level, duration, preferred start time, and whether or not this task is recurring. You are able to add, edit, or remove tasks.
3. After adding tasks to your pet, the program creates a schedule for the day based on how much time the owner has to spend. 
4. When generating schedules, if any conflicts such as tasks having overlapping times occurs there is a warning and you are able to see why this plan was created.
5. After generating the schedule, you can mark tasks as complete. For any recurring tasks, if the user marks it as complete it will respawn.

```
================================================
Today's Schedule
================================================
Daily plan for Alexa (75 of 90 min used):
  08:00-08:30 — Logan: Morning walk (walk, 30 min, priority: high, preferred 08:00) → chosen (priority high, fit the remaining time)
  08:30-08:40 — Logan: Breakfast (feed, 10 min, priority: high, preferred 09:00) → chosen (priority high, fit the remaining time)
  08:40-08:45 — Mimo: Give meds (meds, 5 min, priority: medium, preferred 09:00) → chosen (priority medium, fit the remaining time)
  08:45-09:05 — Mimo: Brush fur (grooming, 20 min, priority: low, preferred 12:00) → chosen (priority low, fit the remaining time)
  09:05-09:15 — Logan: Dinner (feed, 10 min, priority: high, preferred 18:00) → chosen (priority high, fit the remaining time)

Conflict warning: multiple tasks share a start time:
  ! 09:00 — Logan's 'Breakfast', Mimo's 'Give meds'

================================================
Completed 'Morning walk'. Next occurrence due 2026-07-08 (daily).
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
