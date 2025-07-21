from models import db, User, Event, Ticket, Order, OrderItem, Review, Report, AuditLog, EventPass, SavedEvent
from app import app, bcrypt
from datetime import datetime, timedelta
import random
import uuid

with app.app_context():
    print(" Cleaning database...")
    EventPass.query.delete()
    AuditLog.query.delete()
    SavedEvent.query.delete()
    Report.query.delete()
    Review.query.delete()
    OrderItem.query.delete()
    Order.query.delete()
    Ticket.query.delete()
    Event.query.delete()
    User.query.delete()
    db.session.commit()

    print("🌱 Seeding users...")
    users = []

    # Admins
    users.append(User(first_name="Celestine", last_name="Mecheo", email="celestine@example.com", phone="0700000001", password=bcrypt.generate_password_hash("celestine123").decode('utf-8'), role="admin"))
    users.append(User(first_name="Bob", last_name="Boss", email="bob@admin.com", phone="0700000002", password=bcrypt.generate_password_hash("admin123").decode('utf-8'), role="admin"))

    # Organizers
    for i in range(1, 4):
        users.append(User(
            first_name=f"Organizer{i}",
            last_name="Org",
            email=f"org{i}@events.com",
            phone=f"070100000{i}",
            password=bcrypt.generate_password_hash("org123").decode('utf-8'),
            role="organizer"
        ))

    # Attendees
    for i in range(1, 6):
        users.append(User(
            first_name=f"Attendee{i}",
            last_name="User",
            email=f"attendee{i}@mail.com",
            phone=f"071000000{i}",
            password=bcrypt.generate_password_hash("pass123").decode('utf-8'),
            role="attendee"
        ))

    db.session.add_all(users)
    db.session.commit()

    print("🌱 Seeding events & tickets...")
    events = []
    tickets = []

    for i in range(1, 6):
        organizer = users[2 + (i % 3)]
        event = Event(
            title=f"Event {i}",
            description=f"This is the description for Event {i}.",
            location="Nairobi",
            start_time=datetime.now() + timedelta(days=i),
            end_time=datetime.now() + timedelta(days=i, hours=3),
            category="Music",
            tags="live,concert",
            status=random.choice(["approved", "pending", "rejected"]),
            is_approved=True if i % 2 == 0 else False,
            image_url=f"https://example.com/event{i}.jpg",
            organizer_id=organizer.id,
            attendee_count=0
        )
        db.session.add(event)
        db.session.flush()
        events.append(event)

        for j in range(1, 3):
            t = Ticket(
                type=f"Tier {j}",
                price=1000 + j * 200,
                quantity=100,
                sold=random.randint(10, 50),
                event_id=event.id
            )
            db.session.add(t)
            tickets.append(t)

    db.session.commit()

    print("🌱 Seeding orders, order items, event passes, reviews...")
    for attendee in users[-5:]:
        for i in range(2):
            ticket = random.choice(tickets)
            quantity = random.randint(1, 3)
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

            # Seed EventPasses per quantity
            for q in range(quantity):
                event_pass = EventPass(
                    ticket_code=str(uuid.uuid4())[:8].upper(),
                    attendee_first_name=f"Guest{q+1}",
                    attendee_last_name=attendee.last_name,
                    attendee_email=f"guest{q+1}_{attendee.email}",
                    attendee_phone=f"07{random.randint(10000000,99999999)}",
                    att_status=random.choice([True, False]),
                    order_item_id=item.id
                )
                db.session.add(event_pass)

            ticket.event.attendee_count += quantity

            if random.choice([True, False]):
                review = Review(
                    rating=random.randint(3, 5),
                    comment=random.choice(["Amazing!", "Enjoyed it!", "Could be better."]),
                    attendee_id=attendee.id,
                    event_id=ticket.event.id
                )
                db.session.add(review)

    db.session.commit()

    print("🌱 Seeding saved events...")
    for attendee in users[-5:]:
        saved = SavedEvent(user_id=attendee.id, event_id=random.choice(events).id)
        db.session.add(saved)

    db.session.commit()

    print("🌱 Seeding reports & audit logs...")
    for admin in users[:2]:
        r = Report(
            report_data="Sample analytics report for system performance.",
            admin_id=admin.id,
            event_id=random.choice(events).id
        )
        db.session.add(r)

        log = AuditLog(
            action="Seeded report and approved event",
            user_id=admin.id,
            target_type="Event",
            target_id=random.choice(events).id,
            status="Success",
            ip_address="127.0.0.1",
            extra_data={"source": "seed_script"}
        )
        db.session.add(log)

    db.session.commit()
    print("🌱 Seeding complete!")
