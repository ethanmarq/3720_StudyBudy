# 3720_StudyBudy

### Deliverables
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

Run tests:
```
python -m pytest -q
```

Sprint 1 Scope Implemented:
- Create profile with Clemson email validation
- Add course(s) with normalization and duplicate prevention
- Basic CLI for required actions
- Unit tests covering success and validation paths

