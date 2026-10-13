# Campus Customs Dashboard Design

## Look and feel

The dashboard is a calm, premium “desk people want to sit at”: Yale navy anchors the navigation and headings, Yale gold marks the bulldog and money/approval moments, and pale blue-gray surfaces keep a busy operations board easy to scan. The layout uses a compact dark rail, a roomy command header, three at-a-glance metrics, and a two-column work surface. A custom inline bulldog SVG keeps the mark crisp, fast, and dependency-free.

## Layout choices

- The left rail identifies the desk and connection state, with Live board, Approval queue, and Guardrails as familiar work areas.
- The top metrics show open-ticket count, current checking balance, and the always-on human approval gate.
- The ticket inbox is the left work queue; selecting a ticket makes the chosen item explicit before running agents.
- The Agent floor is the right-side live feed so the user can watch role-specific work without losing the ticket list.
- Boss’s summary appears only after a run, followed by a separate approval card when a payment or purchase needs a human click.

## Agent readability

Each role has a distinct color and symbol, while the event line shows the latest action and summary rather than an undifferentiated transcript. The board polls the backend audit endpoint every 2.5 seconds, so tool calls and agent summaries appear in the same visual order that the append-only audit trail records them.

## Resolved tickets and cash

Resolved tickets use a green check mark and green Resolved pill; open tickets keep a numbered blue marker and amber Open pill. The checking balance is visible in the top metrics and reloads after approval, so a successful outflow visibly lowers the amount. The approval form makes the amount, reference, type, and approving person explicit before the backend can change cash.

## Special creative choices

- The bulldog is an original inline SVG “desk mascot,” avoiding a generic placeholder image while matching the Yale palette.
- The Agent floor is framed like a team room: each specialist has a “standing by” state until their first event, then changes to a live status dot.
- The interface uses small mono labels such as `INBOX`, `LIVE FEED`, and `YOUR APPROVAL` to give the board the feel of a well-run operations room.
- The approval card is warm cream/gold instead of the normal blue, making the irreversible money moment visually distinct without using alarmist red.
