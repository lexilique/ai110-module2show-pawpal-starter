# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- My inital design had four classes: Owner, Pet, DailyTasks, and Scheduler. 

- What classes did you include, and what responsibilities did you assign to each?
- Owner determined how much time the owner had, what pets they had, and the option to add pets. Pet described each pet (e.g. breed, age, etc.), what tasks they were assigned, and the option to add/edit/remove tasks. DailyTasks was what created each task and where the user would add priority, time/duration, and if it was completed. Schedule create the plan and explained why it create the plan.


**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
I changed the relationship between tasks and pets. This ensure that tasks goes to specific pets in case there are multiple pets

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- My scheduler considers what time each task starts and the duration of the task. It also considers priority levels but mainly looks at time
- How did you decide which constraints mattered most?
- I prioritized fitting in as many tasks as possible so I focused on when tasks started and how long they were

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- My scheduler focuses on cramming as many tasks as possible into a plan. So it ignores preferred start times when generating a plan.  
- Why is that tradeoff reasonable for this scenario?
- This trade off is resonable for this scenario because many tasks are shorter and does not go over the owner's alloted time constraints.
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- I used Claude for this project
- What kinds of prompts or questions were most helpful?
- I think the prompts where I mentioned certain parts of my code and asked the AI to explain them were the most helpful.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- When drafting my UML diagram Claude suggested to add more classes but I had to specify that I only wanted four classes for this program
- How did you evaluate or verify what the AI suggested?
- I looked back at the README.md file and the instructions to make sure that what the AI was suggesting followed the intentions of this program.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- I tested the program's sorting, how it recognized and recreated recurring tasks,  scheduling conflicts, and tested different constraints such as having no availability for tasks.
- Why were these tests important?
- These tests are important because they model real life situations. 

**b. Confidence**

- How confident are you that your scheduler works correctly?
- I am pretty confident that my scheduler works correctly because I made sure to test and consider most edge cases
- What edge cases would you test next if you had more time?
- I would test my scheduler's capability to prioritize time and priority levels when making plans.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
- I was the most satisfied with creating and reworking the backend of this project. I was able to fix the logic and create a working scheduler
**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
- I would add the option to add multiple owners and assign specific tasks that certain owners have to complete.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
- One important thing I learned about system design is that you need to make sure you understand how each component/class works with other classes and how they interact. 
