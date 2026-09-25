# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities
- Display active announcements and manage them while signed in

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| POST   | `/auth/login?username=...&password=...`                           | Sign in and receive a bearer session token                          |
| GET    | `/auth/check-session?username=...`                                | Validate the signed-in user's bearer session                        |
| POST   | `/auth/logout`                                                    | Invalidate the current bearer session                                |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |
| GET    | `/announcements`                                                  | Get announcements within their start and expiration dates            |
| GET    | `/announcements/manage`                                            | List all announcements (requires a bearer session token)              |
| POST   | `/announcements`                                                   | Create an announcement (requires a bearer session token)              |
| PUT    | `/announcements/{announcement_id}`                                 | Modify an announcement (requires a bearer session token)               |
| DELETE | `/announcements/{announcement_id}`                                | Delete an announcement (requires a bearer session token)               |

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

All data is stored in memory, which means data will be reset when the server restarts.
