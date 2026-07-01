# Case Library CLI Boundary Summary

This gate keeps case-library generation offline and separate from live/runtime systems.

Allowed:

- Read replay event log.
- Build case-library seed.
- Write JSON and Markdown.

Forbidden:

- Live feed connection.
- Alert bridge.
- Broker execution.
- Trading signal wording.
- Runtime artifact contract mutation.
