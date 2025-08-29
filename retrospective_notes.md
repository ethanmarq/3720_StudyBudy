# Retrospective Notes

## Sprint One
Date: 8/29/2025

What went well: 
Python CLI script works smoothly using a json backend with python calls to populate it. Tests to test functionality all pass.

What could be improved: 
Adding more python calls to show other peoples availability and a help menu to see avaiable actions to take.

Action items for next sprint:
Work on Story two, add help menu, add calender, mark availability on calender, save calender and use it for matchmaking. 


## Sprint Two
Date: 8/29/2025

What went well:
Added help menu, added week calender, availability shows under week days, and saves in the json databse

What could be improved: 
Process to handle other users availability to request, accept, decline study times. 

Action items for next sprint: 
Work on user stories three and four which include listing user courses and when one is selected it will display other users aviability when it is selected. Sending study requests for available times listed by other students, accepting and declining study requests, listing scheduled times.  


## Sprint Three
Date: 8/29/2025

What went well:
Implemented classmate search, availability display, overlap calculation, and session proposal/acceptance in modular services. Overlap logic correctly merges and ranks by total shared minutes. Session workflow (propose, list, respond, confirm) worked first pass in manual smoke tests. CLI remained consistent with earlier commands.


What could be improved:
Earlier alignment on naming / command verbs (e.g., list-requests vs list-sessions) to stay fully consistent. Additional validation for overlapping pending sessions or double booking could be added. More negative-path tests still needed for session edge cases.

Action items for future (post-project):
Add double-booking prevention, cancellation command, and optional duration auto-suggestion from overlap windows. Improve formatting (table style) for large availability outputs. Add persistence layer abstraction for easier future database swap.

