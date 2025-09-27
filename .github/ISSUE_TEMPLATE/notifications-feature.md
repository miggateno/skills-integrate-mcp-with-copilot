---
name: Notifications (email + in-app) for signups and waitlist
about: Feature request — send confirmations, reminders, and waitlist promotions
title: "Feature: Notifications for signups and waitlist promotions"
labels: enhancement, feature
assignees: ''
---

## Summary

Add a notifications system to the High School Management System that sends email and in-app notifications for:

- Signup confirmations
- Unregister confirmations
- Waitlist promotions (when a slot opens)
- Optional reminders for upcoming activities (daily/weekly)

This will improve student engagement and reduce administrative overhead.

## Goals

- Deliver reliable signup/unregister confirmations.
- Maintain an in-app notifications feed for users.
- Automatically promote users from the waitlist when slots open and notify them.
- Support background processing so notifications don't block requests.

## Proposed implementation

1. Add a Notification model (database) with fields: id, user_id, activity_id, type, message, read, created_at.
2. Integrate a background worker (FastAPI BackgroundTasks for small scale, or Celery/RQ for production) to send emails and write in-app notifications.
3. Add email provider integration (SMTP or services like SendGrid). For dev, allow a local/no-op adapter that logs messages.
4. Update signup/unregister/waitlist logic to enqueue notification tasks and create in-app notifications.
5. Expose endpoints to list and mark notifications read: `GET /notifications`, `POST /notifications/{id}/read`.
6. Add tests for notification enqueueing and delivery (mocking the email provider).

## Acceptance criteria

- When a student signs up, an in-app notification is created and an email is scheduled.
- When an activity is full, further signups are added to a waitlist and receive a waitlist confirmation.
- When a user is promoted from the waitlist, they receive an email and an in-app notification.
- Background tasks are used for sending emails so API responses remain fast.

## Notes / Future work

- Support SMS notifications.
- Add user preferences for notification channels and scheduling.
- Retry and dead-letter handling for failed emails.

---

Please copy this template into the repository Issues on GitHub if you'd like me to open it there for you (I can do it with a PAT), or I can create a PR that adds this as a task list in the repo.
