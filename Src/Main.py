import time
from Event import Events
from datetime import date
from System import System


def display_events(events: list) -> None:
    if not events:
        print("No events found.")
        return

    today = date.today().isoformat()
    print(f"\n{'='*60}")
    print(f"  Calendar Events  (today: {today})")
    print(f"{'='*60}")

    sorted_events = sorted(events, key=lambda e: e["date"])
    for evt in sorted_events:
        marker = "[LOCKED]" if evt["solid"] else "       "
        indicator = " <-- TODAY" if evt["date"] == today else ""
        print(f"  {evt['date']}  {evt['stime']} - {evt['etime']} {marker} {evt['event']}{indicator}")

    print(f"{'='*60}\n")


def select_event(events: list) -> int:
    """Show a numbered list of events and return the chosen index, or -1 to cancel."""
    if not events:
        print("No events found.")
        return -1
    sorted_events = sorted(events, key=lambda e: e["date"])
    print()
    for i, evt in enumerate(sorted_events):
        marker = " [LOCKED]" if evt["solid"] else ""
        print(f"  {i + 1}. {evt['date']}  {evt['stime']} - {evt['etime']}{marker}  {evt['event']}")
    print()
    raw = input("Select event number (or 0 to cancel): ").strip()
    if not raw.isdigit():
        print("Invalid input.")
        return -1
    num = int(raw)
    if num == 0:
        return -1
    if num < 1 or num > len(sorted_events):
        print("Number out of range.")
        return -1
    return num - 1


def main():
    con: bool = True
    while con:
        loader = Events("","","", "", False)
        events = loader._load_events()
        print("1. View all events")
        print("2. Look up a date")
        print("3. Add an event")
        print("4. Edit an event")
        print("5. Delete an event")
        print("6. Quit")
        choice = input("Choice: ").strip()

        if choice == "1":
            display_events(events)
            time.sleep(2)

        elif choice == "2":
            target = input("Enter date (YYYY-MM-DD): ").strip()
            try:
                result = System(events).get_event(target)
                locked = " [LOCKED]" if result["solid"] else ""
                print(f"\n  {target}: {result['event']}{locked}\n")
            except ValueError as e:
                print(f"\n  {e}\n")

        elif choice == "3":
            evt_date = input("Date (YYYY-MM-DD): ").strip()
            evt_stime = input(" Start Time (HH:MM): ").strip()
            evt_etime = input(" End Time (HH:MM): ").strip()
            evt_name = input("Event name: ").strip()
            evt_solid = input("Lock this event? (y/n): ").strip().lower() == "y"
            try:
                new_event = Events(evt_date, evt_stime, evt_etime, evt_name, evt_solid)
            except ValueError as e:
                print(f"\n  Invalid input: {e}\n")
                continue
            sys = System(events)
            if sys.is_solid(evt_date):
                print("\n  Another event is solid during that time.")
                print("  Event not saved.\n")
                continue
            if sys.is_overlapped(evt_date, evt_stime):
                print("\n  Warning: This event overlaps with an existing event.\n")
                replace = input("  Do you want to add it anyway? (y/n): ").strip().lower() == "y"
                if not replace:
                    print("\n  Event not saved.\n")
                    continue
            new_event._create_event()
            print(f"\n  Saved: {evt_date} - from {evt_stime} to {evt_etime} — {evt_name}\n")

        elif choice == "4":
            idx = select_event(events)
            if idx == -1:
                continue
            sorted_events = sorted(events, key=lambda e: e["date"])
            evt = sorted_events[idx]
            print(f"\n  Editing: {evt['date']}  {evt['stime']} - {evt['etime']}  {evt['event']}")
            print("  (Press Enter to keep current value)\n")
            new_date  = input(f"  New date [{evt['date']}]: ").strip() or None
            new_stime = input(f"  New start time [{evt['stime']}]: ").strip() or None
            new_etime = input(f"  New end time [{evt['etime']}]: ").strip() or None
            new_name  = input(f"  New event name [{evt['event']}]: ").strip() or None
            solid_raw = input(f"  Lock event? (y/n) [{'y' if evt['solid'] else 'n'}]: ").strip().lower()
            new_solid = True if solid_raw == "y" else (False if solid_raw == "n" else None)
            loader._edit_event(idx, ndate=new_date, nstime=new_stime, netime=new_etime, nevent=new_name, nsolid=new_solid)
            print("\n  Event updated.\n")

        elif choice == "5":
            idx = select_event(events)
            if idx == -1:
                continue
            sorted_events = sorted(events, key=lambda e: e["date"])
            evt = sorted_events[idx]
            confirm = input(f"  Delete '{evt['event']}' on {evt['date']}? (y/n): ").strip().lower()
            if confirm == "y":
                loader._delete_event(idx)
                print("\n  Event deleted.\n")
            else:
                print("\n  Cancelled.\n")

        elif choice == "6":
            con = False

        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
