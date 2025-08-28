# Iterations – Agile (Scrum-Style)

This document outlines the three planned 1-day sprints for the **Study Buddy Scheduling App**. Each sprint includes planned features, implementation details, testing steps, and example stand-up logs.

---

## Sprint 1: Profiles & Availability

### Planned Features
- Students can create a profile with name, email, and enrolled courses.
- Students can add/remove their weekly availability.

### Implementation
- Build simple CLI or web forms for entering data.
- Store profile and availability in a basic data structure (JSON or database).

### Testing
- Verify profile creation works with valid/invalid inputs.
- Confirm availability updates persist after save.

### Stand-Up Log (Sample)
- **Progress**: Profile creation implemented.  
- **Blockers**: Availability input format confusion (HH:MM vs. blocks).  
- **Next Steps**: Standardize time format.

---

## Sprint 2: Matching & Suggestions

### Planned Features
- System suggests potential study partners based on overlapping availability and courses.
- Display match results in a readable format.

### Implementation
- Matching algorithm compares student schedules.
- Integrate with availability from Sprint 1.

### Testing
- Test with overlapping vs. non-overlapping schedules.
- Ensure multiple matches appear sorted by best overlap.

### Stand-Up Log (Sample)
- **Progress**: Matching logic implemented for 2 users.  
- **Blockers**: Handling larger groups (3+ users).  
- **Next Steps**: Extend to multiple matches, refine sorting.

---

## Sprint 3: Meeting Confirmation & Polish

### Planned Features
- Students can send/accept meeting requests.
- Confirmed sessions are logged for both users.
- Clean up user interface / command flow.

### Implementation
- Add confirmation system (simple yes/no prompt or clickable option).
- Store confirmed meetings in a separate structure.
- Polish code and comments for final demo.

### Testing
- Verify confirmation works with multiple requests.
- Test declining vs. accepting requests.
- Regression test: ensure profiles and matching still function.

### Stand-Up Log (Sample)
- **Progress**: Confirmation logic built and tested with small sample.  
- **Blockers**: UI formatting bugs in CLI.  
- **Next Steps**: Final polish + prep demo.

---

## Iteration Reviews

At the end of each sprint, the team reflected on outcomes:

- **Sprint 1 Review**  
  Profiles and availability successfully implemented. Time format standardization required adjustment.  

- **Sprint 2 Review**  
  Matching feature worked for pairs but needed refinement for larger groups. Backlog adjusted to prioritize reliability over complexity.  

- **Sprint 3 Review**  
  Meeting confirmation implemented and integrated with existing features. Minor UI formatting issues resolved during polish phase.  


---

## Sprint One
Date: 
Team Member: 
Yesterday's Work:
Today's Plan:
Blockers:

Team Member: 
Yesterday's Work:
Today's Plan:
Blockers:


## Sprint Two
Date: 
Team Member: 
Yesterday's Work:
Today's Plan:
Blockers:

Team Member: 
Yesterday's Work:
Today's Plan:
Blockers:


## Sprint Three
Date: 
Team Member: 
Yesterday's Work:
Today's Plan:
Blockers:


Team Member: 
Yesterday's Work:
Today's Plan:
Blockers:


