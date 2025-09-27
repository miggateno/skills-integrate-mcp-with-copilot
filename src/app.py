"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
from .utils import add_numbers
from .notifications import NotificationStore, create_and_send
from fastapi import BackgroundTasks

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.get("/notifications")
def list_notifications(email: str):
    """List in-app notifications for an email address (dev)."""
    return NotificationStore.list_for_email(email)


@app.post("/notifications/{id}/read")
def mark_notification_read(id: int):
    try:
        n = NotificationStore.mark_read(id)
        return n
    except KeyError:
        raise HTTPException(status_code=404, detail="Notification not found")




@app.get("/add")
def add_endpoint(a: float, b: float):
    """Simple endpoint to add two query parameters `a` and `b`.

    Example: /add?a=2&b=3 -> {"result": 5}
    """
    result = add_numbers(a, b)
    return {"result": result}


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str, background_tasks: BackgroundTasks):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Add student or waitlist if full
    if len(activity["participants"]) < activity.get("max_participants", 0):
        activity["participants"].append(email)
        # create notification and schedule email
        create_and_send(background_tasks, email, activity_name, "signup_confirmation",
                        f"You have been signed up for {activity_name}.")
        return {"message": f"Signed up {email} for {activity_name}"}
    else:
        # simple waitlist implementation: keep a waitlist list
        waitlist = activity.setdefault("waitlist", [])
        if email in waitlist:
            raise HTTPException(status_code=400, detail="Student already on waitlist")
        waitlist.append(email)
        create_and_send(background_tasks, email, activity_name, "waitlist_confirmation",
                        f"{activity_name} is full. You've been added to the waitlist.")
        return {"message": f"Added {email} to waitlist for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str, background_tasks: BackgroundTasks):
    """Unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student
    activity["participants"].remove(email)

    # If there's a waitlist, promote first and notify
    waitlist = activity.get("waitlist", [])
    if waitlist:
        promoted = waitlist.pop(0)
        activity["participants"].append(promoted)
        create_and_send(background_tasks, promoted, activity_name, "waitlist_promoted",
                        f"You have been promoted from the waitlist to be a participant in {activity_name}.")

    create_and_send(background_tasks, email, activity_name, "unregister_confirmation",
                    f"You have been unregistered from {activity_name}.")

    return {"message": f"Unregistered {email} from {activity_name}"}
