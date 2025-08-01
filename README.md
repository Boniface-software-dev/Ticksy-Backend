#  Ticksy Backend

Ticksy is a modern event ticketing and management platform built for organizers and attendees. The backend is powered by **Flask** and supports core features like authentication, event creation, ticketing, real-time availability, and MPESA payments.

---

##  Tech Stack

- **Backend Framework:** Flask (Python)
- **Database:** PostgreSQL
- **Authentication:** JWT Bearer Tokens
- **Payments:** MPESA STK Push (Safaricom API)
- **ORM:** SQLAlchemy
- **Testing:** pytest / Postman
- **Environment:** Python 3.10+

---

##  MVP Features

###  Authentication & Authorization
- JWT-based secure login system
- Role-based access control (Admin, Organizer, Attendee)
- Registration and login endpoints

###  Event & Ticketing System
- Organizers can create, update, delete events
- Support for multiple ticket types: Early Bird, Regular, VIP
- Real-time ticket availability tracking
- Attendees can browse, book, and view event details

###  Payments Integration
- MPESA STK Push for secure mobile payments
- Transaction confirmation and ticket issuance

###  Extras
- Save events to calendar
- View ticket history
- Export attendee lists (for organizers)

---

##  Project Structure
```bash
ticksy-frontend/
├── app.py
├── instance
│   └── development.db
├── migrations
│   ├── alembic.ini
│   ├── env.py
│   ├── README
│   ├── script.py.mako
│   └── versions
├── models.py
├── Pipfile
├── Pipfile.lock
├── __pycache__
│   └── models.cpython-38.pyc
├── README.md
├── resources
│   ├── admin_analytics.py
│   ├── admin_dashboard.py
│   ├── admin_events.py
│   ├── admin_users.py
│   ├── attendee_profile.py
│   ├── attendees.py
│   ├── auth.py
│   ├── events.py
│   ├── orders.py
│   ├── profile_events.py
│   ├── profile.py
│   ├── reviews.py
│   ├── saved_events.py
│   └── tickets.py
├── seed.py
└── utils
    └── logger.py
```

---

##  Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Boniface-software-dev/Ticksy-Backend
cd Ticksy-Backend
```

### 2. Install Dependencies

```bash
pipenv install && pipenv shell
```
### 3. Setup Environment Variables
Create a .env file with the following:

```bash
FLASK_ENV=development
DATABASE_URL=postgresql://username:password@localhost:5432/ticksy_db
SECRET_KEY=your_jwt_secret_key
MPESA_CONSUMER_KEY=your_consumer_key
MPESA_CONSUMER_SECRET=your_consumer_secret
MPESA_SHORTCODE=your_shortcode
MPESA_PASSKEY=your_passkey
CALLBACK_URL=https://yourdomain.com/api/payment/callback
```
### 4. Run Database Migrations

```bash
flask db init
flask db migrate
flask db upgrade
```
### 5. Start the Server

```bash
flask run
```
# API Documentation
## 🔌 Core API Endpoints

###  Authentication Routes
| Method | Endpoint       | Description                     | Access Control |
|--------|----------------|---------------------------------|----------------|
| POST   | `/signup`      | User registration               | Public         |
| POST   | `/login`       | User login (JWT issued)         | Public         |

###  User Profile Routes
| Method | Endpoint            | Description                              | Access Control       |
|--------|---------------------|------------------------------------------|----------------------|
| GET    | `/profile/me`       | Get logged-in user's profile             | Authenticated Users  |
| PUT    | `/profile/me`       | Update logged-in user's profile          | Authenticated Users  |
| GET    | `/users/<id>`       | Admin view of any user profile           | Admin Only           |

###  Event Routes
| Method | Endpoint            | Description                              | Access Control       |
|--------|---------------------|------------------------------------------|----------------------|
| GET    | `/events`           | Public: list of approved events         | Public               |
| POST   | `/events`           | Organizer: create new event             | Organizers           |
| GET    | `/events/<id>`      | Public: view event details (+calendar)  | Public               |
| PUT    | `/events/<id>`      | Organizer: update own event             | Event Owner          |
| DELETE | `/events/<id>`      | Organizer: delete own event             | Event Owner          |
| GET    | `/my-events`        | Organizer: list own events              | Organizers           |

###  Admin Moderation
| Method | Endpoint               | Description                          | Access Control |
|--------|------------------------|--------------------------------------|----------------|
| GET    | `/admin/pending`       | List unapproved events              | Admin          |
| PATCH  | `/admin/approve/<id>`  | Approve/reject an event             | Admin          |

###  Admin Reports
| Method | Endpoint            | Description                          | Query Parameters                              |
|--------|---------------------|--------------------------------------|-----------------------------------------------|
| GET    | `/admin/reports`    | Filtered reports                    | `?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`  |
|        |                     |                                      | `&event_name=tech` (optional)                 |

###  Organizer Analytics
| Method | Endpoint                   | Description                          | Access Control |
|--------|----------------------------|--------------------------------------|----------------|
| GET    | `/organizer/overview`      | Total revenue, tickets sold         | Organizers     |
| GET    | `/organizer/stats`         | Detailed stats per event            | Organizers     |

## Roles Overview

**Admin**  
- Manages users  
- Moderates events  
- Views analytics  

**Organizer**  
- Creates events  
- Tracks ticket sales  
- Exports data  

**Attendee**  
- Registers account  
- Buys tickets  
- Saves favorite events  
- Leaves reviews  

## Security  

- JWT tokens for session management  
- Role-based access at the route level  
- Environment variables to secure secrets  

## Future Plans (Backend)  

- Add support for card-based payments  
- Email notifications on booking/payment  
- QR code generation & check-in system  
---
 
## Contributors

Huge thanks to the amazing team behind **Ticksy**:

- **Joy Malinda**  
- **Boniface Muguro**  
- **Grace Zawadi**  
- **Aquila Jedidiah**  
- **Celestine Mecheo**  
- **Edwin Kipyego**  

---

## Frontend Repository

The Ticksy frontend is available at:  
[https://github.com/Boniface-software-dev/Ticksy-Frontend]

---

## License

This project was developed as a collaborative group project for educational and demonstration purposes.  
All rights reserved by the contributors listed above. Please contact the team before any reuse or distribution.

---

## Need Help?

Have questions, suggestions, or feedback?  
Open an issue or join the discussion via GitHub.

---

**Built with ❤️ by the Ticksy Team**

