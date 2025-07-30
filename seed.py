from models import db, User, Event, Ticket, Order, OrderItem, Review, Report, AuditLog, EventPass, SavedEvent
from app import app, bcrypt
from datetime import datetime, timedelta
import random
import uuid

with app.app_context():
    print("Dropping and recreating database")
    db.drop_all()
    db.create_all()

    print("🌱 Seeding users...")
    users = []

    # Admins
    users.append(User(first_name="Celestine", last_name="Mecheo", email="celestine@example.com", phone="0700000001", password=bcrypt.generate_password_hash("celestine123").decode('utf-8'), role="admin"))
    users.append(User(first_name="Bob", last_name="Boss", email="bob@admin.com", phone="0700000002", password=bcrypt.generate_password_hash("admin123").decode('utf-8'), role="admin"))

    # Organizers
    organizers = [
        {"first_name": "Wanjiru", "last_name": "Mwangi", "email": "wanjiru@events.co.ke", "phone": "0701223344"},
        {"first_name": "Brian", "last_name": "Otieno", "email": "brian@events.co.ke", "phone": "0711223344"},
        {"first_name": "Njeri", "last_name": "Kariuki", "email": "njeri@events.co.ke", "phone": "0721223344"},
    ]

    for org in organizers:
        users.append(User(
            first_name=org["first_name"],
            last_name=org["last_name"],
            email=org["email"],
            phone=org["phone"],
            password=bcrypt.generate_password_hash("organizer123").decode('utf-8'),
            role="organizer"
        ))

    # Attendees (20 for more variety)
    attendees = []
    for i in range(20):
        attendees.append(User(
            first_name=f"Attendee{i+1}",
            last_name=f"Last{i+1}",
            email=f"attendee{i+1}@gmail.com",
            phone=f"07{random.randint(10000000,99999999)}",
            password=bcrypt.generate_password_hash("attendee123").decode('utf-8'),
            role="attendee"
        ))

    users.extend(attendees)
    db.session.add_all(users)
    db.session.commit()

    print("🌱 Seeding events & tickets...")

    categories = ["Music", "Tech", "Food", "Culture", "Adventure", "Fashion"]
    events = []
    tickets = []

    for i in range(50):  # Create 50 diverse events
        organizer = random.choice(users[2:5])
        start = datetime.now() - timedelta(days=random.randint(1, 60))
        end = start + timedelta(hours=5)
        event = Event(
            title=f"Event {i+1} - {random.choice(['Summit', 'Festival', 'Expo', 'Weekend', 'Camp'])}",
            description="This is a well-curated event experience.",
            location=random.choice(["Nairobi", "Naivasha", "Mombasa", "Kisumu", "Eldoret"]),
            start_time=start,
            end_time=end,
            category=random.choice(categories),
            tags="music,tech,fun,food",
            status="approved",
            is_approved=True,
            image_url=f"https://source.unsplash.com/400x300/?event,{i+1}",
            organizer_id=organizer.id,
            attendee_count=0
        )
        db.session.add(event)
        db.session.flush()
        events.append(event)

        for t in ["Regular", "VIP", "VVIP"]:
            qty = random.randint(50, 200)
            sold = random.randint(10, qty)
            tickets.append(Ticket(
                type=t,
                price=1500 * (1 if t == "Regular" else 2 if t == "VIP" else 3),
                quantity=qty,
                sold=sold,
                event_id=event.id
            ))

    db.session.add_all(tickets)
    db.session.commit()

    print("🌱 Seeding orders, items, passes, reviews...")

    for attendee in users[5:]:  # Attendees only
        for _ in range(random.randint(3, 6)):
            ticket = random.choice(tickets)
            quantity = random.randint(1, 4)
            order = Order(
                order_id=str(uuid.uuid4()),
                attendee_id=attendee.id,
                status="paid",
                total_amount=ticket.price * quantity,
                mpesa_receipt=f"MPESA{random.randint(100000,999999)}"
            )
            db.session.add(order)
            db.session.flush()

            item = OrderItem(order_id=order.id, ticket_id=ticket.id, quantity=quantity)
            db.session.add(item)
            db.session.flush()

            for _ in range(quantity):
                db.session.add(EventPass(
                    ticket_code=str(uuid.uuid4())[:8].upper(),
                    attendee_first_name=attendee.first_name,
                    attendee_last_name=attendee.last_name,
                    attendee_email=attendee.email,
                    attendee_phone=attendee.phone,
                    att_status=random.choice([True, False]),
                    order_item_id=item.id
                ))

            ticket.event.attendee_count += quantity

            if random.choice([True, False]):
                db.session.add(Review(
                    rating=random.randint(3, 5),
                    comment=random.choice(["Amazing", "Loved it", "Inspiring", "Well organized"]),
                    attendee_id=attendee.id,
                    event_id=ticket.event.id
                ))

    db.session.commit()

    print("🌱 Seeding saved events & reports...")

    for attendee in users[5:]:
        for _ in range(random.randint(1, 5)):
            db.session.add(SavedEvent(
                user_id=attendee.id,
                event_id=random.choice(events).id
            ))

    for admin in users[:2]:
        for _ in range(10):
            db.session.add(Report(
                report_data="Auto-generated monthly performance.",
                admin_id=admin.id,
                event_id=random.choice(events).id
            ))
            db.session.add(AuditLog(
                action="Generated report",
                user_id=admin.id,
                target_type="Event",
                target_id=random.choice(events).id,
                status="Success",
                ip_address="127.0.0.1",
                extra_data={"tool": "Seeder", "reason": "load test"}
            ))

    db.session.commit()
    print("✅ Seeding complete.")