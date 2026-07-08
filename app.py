import streamlit as st

from pawpal_system import DEFAULT_DAY_START, DailyTasks, Owner, Pet, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Plan a day of pet care around the time you actually have.")

# --- Session state ----------------------------------------------------------
# Keep ONE Owner (and its Scheduler) alive across Streamlit reruns.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan", time_availability=90)
    st.session_state.scheduler = Scheduler(st.session_state.owner)

owner = st.session_state.owner
scheduler = st.session_state.scheduler

TASK_TYPES = ["walk", "feed", "meds", "enrichment", "grooming", "other"]

st.divider()

# --- Owner & time budget ----------------------------------------------------
st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)
owner.time_availability = st.number_input(
    "Time available for pet care today (minutes)",
    min_value=0,
    max_value=600,
    value=owner.time_availability,
    step=15,
    help="The scheduler fills this budget from the start of the day, then stops.",
)

st.divider()

# --- Add a Pet --------------------------------------------------------------
st.subheader("Add a Pet")
col1, col2 = st.columns(2)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col2:
    breed = st.text_input("Breed", value="")
    age = st.number_input("Age (years)", min_value=0, max_value=40, value=1)

if st.button("Add pet"):
    if pet_name.strip():
        owner.add_pet(Pet(pet_name.strip(), species=species, breed=breed, age=int(age)))
        st.success(f"Added {pet_name} 🐾")
    else:
        st.warning("Give your pet a name first.")

if owner.pets:
    st.write("**Pets so far:** " + ", ".join(pet.name for pet in owner.pets))
else:
    st.info("Add at least one pet to start planning its care.")

st.divider()

# --- Add Tasks --------------------------------------------------------------
st.subheader("Add a Task")

if not owner.pets:
    st.info("No pets yet — add a pet above before adding tasks.")
else:
    pet_index = st.selectbox(
        "Which pet is this for?",
        options=range(len(owner.pets)),
        format_func=lambda i: owner.pets[i].name,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        task_title = st.text_input("Task title", value="Morning walk")
    with c2:
        task_type = st.selectbox("Type", TASK_TYPES)
    with c3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    c4, c5, c6 = st.columns(3)
    with c4:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    with c5:
        frequency = st.selectbox("Repeats", ["once", "daily", "weekly"])
    with c6:
        set_time = st.checkbox("Set preferred time", value=True)

    time_start = ""
    if set_time:
        picked = st.time_input("Preferred start time", value=None)
        if picked is not None:
            time_start = picked.strftime("%H:%M")

    if st.button("Add task"):
        if not task_title.strip():
            st.warning("Give the task a title first.")
        else:
            owner.pets[pet_index].add_task(
                DailyTasks(
                    name=task_title.strip(),
                    task_type=task_type,
                    duration_mins=int(duration),
                    priority=priority,
                    time_start=time_start,
                    frequency=frequency,
                )
            )
            st.success(f"Added “{task_title}” for {owner.pets[pet_index].name}.")

# --- Current tasks (sorted + filtered) --------------------------------------
pending = scheduler.filter_by_completion(completed=False)

if pending:
    st.markdown("### Current tasks")

    sort_choice = st.radio(
        "Sort by",
        ["Preferred time", "Priority"],
        horizontal=True,
    )
    ordered = (
        scheduler.sort_by_time(pending)
        if sort_choice == "Preferred time"
        else scheduler.priority_sort(pending)
    )

    st.dataframe(
        [
            {
                "Pet": t.pet.name if t.pet else "—",
                "Task": t.name,
                "Type": t.task_type,
                "Priority": t.priority,
                "Duration (min)": t.duration_mins,
                "Preferred": t.time_start or "any",
                "Repeats": t.frequency,
            }
            for t in ordered
        ],
        use_container_width=True,
        hide_index=True,
    )

st.divider()

# --- Build the schedule -----------------------------------------------------
st.subheader("Build Schedule")

if st.button("Generate schedule", type="primary"):
    if not pending:
        st.info("No pending tasks to schedule. Add a task above.")
    else:
        # Conflict warning FIRST, above the plan, so it's seen while actionable.
        conflicts = scheduler.detect_conflicts()
        if conflicts:
            st.warning(conflicts, icon="⚠️")
            st.caption(
                "PawPal+ will still run these one after another, but you may want to "
                "stagger their preferred times so nothing feels rushed."
            )

        plan = scheduler.generate_plan()

        if plan:
            used = sum(task.duration_mins for task, _s, _e in plan)
            st.success(
                f"Scheduled {len(plan)} task(s) — {used} of "
                f"{owner.time_availability} min used, starting {DEFAULT_DAY_START}."
            )
            st.table(
                [
                    {
                        "Time": f"{start}–{end}",
                        "Pet": task.pet.name if task.pet else "—",
                        "Task": task.name,
                        "Type": task.task_type,
                        "Priority": task.priority,
                        "Duration (min)": task.duration_mins,
                    }
                    for task, start, end in plan
                ]
            )
        else:
            st.info("Nothing fit in the available time. Try increasing your time budget.")

        if scheduler.skipped:
            skipped_names = ", ".join(
                f"{t.pet.name if t.pet else '—'}: {t.name}" for t in scheduler.skipped
            )
            st.warning(
                f"Skipped {len(scheduler.skipped)} task(s) — ran out of time: {skipped_names}",
                icon="⏰",
            )

        with st.expander("Why this plan? (full explanation)"):
            st.text(scheduler.explain())
