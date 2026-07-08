# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.

class Owner {
    + name: str
    + pets: list[Pet]
    + time_availability: int
    + add_pet(Pet)
} 

class Pet {
    + name: str
    + species: str
    + breed: str
    + age: int
    + tasks: list[DailyTasks] tasks  
    + add_task(task) 
    + edit_task(index, changes) 
    + remove_task(index)
}

class DailyTasks {
    + name: str
    + task_type: str
    + duration_mins: int
    + priority: str
    + time_start: str
    + is_completed: bool
    + priority_level() int -> gets task's prioirty level
    + mark_complete()  -> marks task as complete
    + describe() str  -> describes task
}

class Scheduler {
    + Owner owner
    + list plan
    + all_tasks() list[DailyTasks] -> gets all tasks
    + priority_sort(tasks) list[DailyTasks] -> sorts tasks by priority
    + generate_plan() list -> creates plan
    + explain() str -> explains plan
}


- What classes did you include, and what responsibilities did you assign to each?
- 

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
