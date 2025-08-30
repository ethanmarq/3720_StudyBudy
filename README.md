# 3720_StudyBudy

---

## Deliverables (All in Github) 

### Process Artifacts
#### backlog.md: 
- contain user stories and acceptance criteria

#### sprint_plans.md:
- Sprint Goal
- User Stories to work on
- Tasks to acomplish user story

#### stand_up_logs.md:
- Last sprint acomplishment
- Current sprint acomplishment
- whats blocking progress


#### retrospective_notes.md:
- What went well
- What could be improved
- Actions for next sprint

### AI Transcript 
marquez_ethan_ai_transcript.txt
ellis_michael_ai_transcript.txt

### AI Usage Report
3720_AI_usage_report.pdf

### Reflection Report
3720_StudyBuddy_Reflection_Report.pdf

---

## Universal Useful Commands
Help:
```
python -m studybuddy.cli --help
```

Run tests:
```
python -m pytest -q
```

## Running the Sprint 1 CLI (Profiles & Courses)

Python 3.10+ recommended. No external dependencies.

Commands:

Create user:
```
python -m studybuddy.cli create-user --name "Alice" --email alice@clemson.edu
```

Add course:
```
python -m studybuddy.cli add-course --email alice@clemson.edu --course "CPSC 3720"
```

Show profile:
```
python -m studybuddy.cli show-profile --email alice@clemson.edu
```

Data is stored in `data/users.json`. Tests isolate storage via `STUDYBUDDY_DATA_PATH` env var.

Sprint 1 Scope Implemented:
- Create profile with Clemson email validation
- Add course(s) with normalization and duplicate prevention
- Basic CLI for required actions
- Unit tests covering success and validation paths

## Availability (Story 2 CLI)

Add availability slot:
```
python -m studybuddy.cli add-availability --email alice@clemson.edu --day Mon --start 1:00pm --end 3:00pm
```

List availability:
```
python -m studybuddy.cli list-availability --email alice@clemson.edu
```

Remove a slot by index (see list output):
```
python -m studybuddy.cli remove-availability --email alice@clemson.edu --index 1
```

Show full week overview (12-hour EST):
```
python -m studybuddy.cli week-availability --email alice@clemson.edu
```

Notes:
- Overlapping or adjacent slots on the same day are automatically merged.
- Time input accepts either 24h (13:30) or 12h with am/pm (1:30pm, 9am). Internally stored in 24h; displayed in 12h in the week view.
- Days accepted: Mon Tue Wed Thu Fri Sat Sun.

## Classmate Search (Story 3 CLI)

List classmates (same course):
```
python -m studybuddy.cli search-classmates --email alice@clemson.edu --course "CPSC 3720"
```

List classmates with their weekly availability (only days with availability shown):
```
python -m studybuddy.cli search-classmates-availability --email alice@clemson.edu --course "CPSC 3720"
```

Show overlap (common availability windows) with classmates (sorted by total minutes):
```
python -m studybuddy.cli search-overlap --email alice@clemson.edu --course "CPSC 3720"
```

Output shows classmates excluding the requesting user. Availability is aggregated (merged) per day.

## Study Session Requests (Story 4 CLI)

Propose a session (must be within both users' availability and shared course):
```
python -m studybuddy.cli propose-session --from alice@clemson.edu --to bob@clemson.edu --course "CPSC 3720" --day Wed --start 2:30pm --end 3:30pm --message "Review chapter 5"
```

List pending requests (incoming & outgoing):
```
python -m studybuddy.cli list-requests --email bob@clemson.edu
```

Respond to a request (invitee only):
```
python -m studybuddy.cli respond-session --email bob@clemson.edu --id 1 --action accept
```

List confirmed sessions:
```
python -m studybuddy.cli list-sessions --email alice@clemson.edu
```

Rules:
- Both students must exist and share the course.
- Proposed time must be fully inside each participant's availability window for that day.
- Only invitee can accept/decline.
- Accepted sessions appear for both participants via list-sessions.

