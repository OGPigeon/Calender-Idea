import time
from Event import Events
from datetime import date
from System import System


def display_events(events: list) -> None:
    if not events:
        print("No events found.")
        return

    today = date.today().isoformat()
    print(f"\n{'='*40}")
    print(f"  Calendar Events  (today: {today})")
    print(f"{'='*40}")

    sorted_events = sorted(events, key=lambda e: e["date"])
    for evt in sorted_events:
        marker = "[LOCKED]" if evt["solid"] else "       "
        indicator = " <-- TODAY" if evt["date"] == today else ""
        print(f"  {evt['date']}  {marker}  {evt['event']}{indicator}")

    print(f"{'='*40}\n")


def main():
    con: bool = True
    while con:
        loader = Events("","","", "", False)
        events = loader._load_events()
        print("1. View all events")
        print("2. Look up a date")
        print("3. Add an event")
        print("4. Delete an event")
        print("5. Quite")
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
                return
            sys = System(events)
            if sys.is_solid(evt_date):
                print("\n Another event is solid during that time.\n")
                print("\n  Event not saved.\n")
                return
            if sys.is_overlapped(evt_date, evt_stime):
                print("\n  Warning: This event overlaps with an existing event.\n")
                replace = input("  Do you want to add it anyway? (y/n): ").strip().lower() == "y"
                loader._delete_event(evt_date,evt_stime,evt_etime)
                if not replace:
                    print("\n  Event not saved.\n")
                    return
            new_event._create_event()
            print(f"\n  Saved: {evt_date} - from {evt_stime} to {evt_etime} — {evt_name}\n")

        elif choice == "4":
            evt_date = input("Date (YYYY-MM-DD): ").strip()
            evt_stime = input(" Start Time (HH:MM): ").strip()
            evt_etime = input(" End Time (HH:MM): ").strip()
            loader._delete_event(evt_date,evt_stime,evt_etime)
            print("\n Event Deleted \n")
        
        elif choice == "5":
            con = False

        else:
            print("Invalid choice.")


if __name__ == "__main__":
        main()
