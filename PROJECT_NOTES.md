# Intent Based Campus Automation System

## Current Status

The project now has a working admin and student flow with professional dashboards, intent-based requests, PDF generation, and admin management features.

## Completed Features

### Authentication
- Admin login
- Student login
- Session-based role access

### Student Features
- Professional student dashboard UI
- Natural-language request input
- Leave request through intent detection
- Leave request history table
- Approved leave PDF download
- Bonafide request without teacher approval
- Bonafide PDF download from student dashboard
- Campus notice display on student dashboard

### Admin Features
- Professional admin dashboard UI
- Create user
- Search user
- Edit existing user details
- Reset user password
- Delete user
- View all leave requests
- Approve leave
- Reject leave
- Download leave PDF
- Create notice
- Delete notice

### Bonafide Certificate
- Generated automatically from student request
- Uses real database details:
  - username
  - full name
  - roll number
  - department
  - course
  - year/semester
- Improved PDF design with:
  - institute header
  - certificate number
  - issue date
  - bordered layout
  - formal certificate body
  - signatory area
- Text fitting and wrapping fixed for long content

### Database Updates
- `users` table expanded with:
  - `full_name`
  - `roll_number`
  - `department`
  - `course`
  - `year_semester`
- `notices` table added

## Important Project Logic

### Leave Flow
1. Student enters leave request in plain English.
2. Intent module detects leave request.
3. Leave details are extracted.
4. Leave request is stored in database.
5. Admin approves or rejects.
6. Student can download PDF only after approval.

### Bonafide Flow
1. Student enters bonafide request in dashboard.
2. Intent module detects bonafide request.
3. System fetches student details from database.
4. PDF is generated automatically.
5. No teacher approval is required.
6. Download button appears in student dashboard.

### Notice Board Flow
1. Admin creates notice from admin dashboard.
2. Notice is saved in database.
3. Student dashboard shows latest notices.

## Important Files

### Templates
- `templates/student.html`
- `templates/admin.html`
- `templates/admin_leaves.html`
- `templates/login.html`

### Routes
- `app/routes/auth_routes.py`
- `app/routes/student_routes.py`
- `app/routes/admin_routes.py`
- `app/routes/chat_routes.py`

### Services
- `app/services/auth_service.py`
- `app/services/intent_service.py`
- `app/services/leave_service.py`
- `app/services/bonafide_service.py`
- `app/services/pdf_service.py`

### Data Layer
- `app/models.py`
- `app/database.py`

## Viva / Report Highlights

- Intent-based campus automation
- Role-based login system
- Leave management automation
- Bonafide certificate automation
- PDF generation
- Search, edit, and reset-password admin tools
- Notice board integration

## Pending / Good Next Features

- Student profile page
- Student change-password feature
- Attendance module
- Timetable query through intent
- Faculty module
- Better notice workflow after publishing
- Notice filters or search

## Useful Reminders

- If a newly added route or feature does not appear in browser, restart the FastAPI server.
- Existing older student accounts may have missing academic details if they were created before the new fields were added.
- Bonafide generation needs student profile details to be filled.

## Suggested Next Build Order

1. Student profile page
2. Student password change
3. Attendance module
4. Timetable intent
5. Faculty role
