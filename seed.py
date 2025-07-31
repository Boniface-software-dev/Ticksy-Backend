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
    organizers_info = [
        {"first_name": "Wanjiru", "last_name": "Mwangi", "email": "wanjiru@events.co.ke", "phone": "0701223344"},
        {"first_name": "Brian", "last_name": "Otieno", "email": "brian@events.co.ke", "phone": "0711223344"},
        {"first_name": "Njeri", "last_name": "Kariuki", "email": "njeri@events.co.ke", "phone": "0721223344"},
    ]
    organizer_users = []
    for org in organizers_info:
        user = User(
            first_name=org["first_name"],
            last_name=org["last_name"],
            email=org["email"],
            phone=org["phone"],
            password=bcrypt.generate_password_hash("organizer123").decode('utf-8'),
            role="organizer"
        )
        users.append(user)
        organizer_users.append(user)

    # Attendees
    attendees = [
        User(
            first_name=f"Attendee{i+1}",
            last_name=f"Last{i+1}",
            email=f"attendee{i+1}@gmail.com",
            phone=f"07{random.randint(10000000, 99999999)}",
            password=bcrypt.generate_password_hash("attendee123").decode('utf-8'),
            role="attendee"
        ) for i in range(20)
    ]
    users.extend(attendees)
    db.session.add_all(users)
    db.session.commit()

    print("🌱 Seeding events & tickets...")
    categories = ["Music", "Tech", "Food", "Culture", "Adventure", "Fashion"]
    events = []
    tickets = []

    rejected_events = []
    pending_events = []
    approved_future_events = []
    approved_past_events = []

    # Rejected Events
    for org in organizer_users:
        for _ in range(3):
            rejected_events.append(Event(
                title=f"{org.first_name}'s Rejected Event",
                description="Rejected event for testing.",
                location=random.choice(["Nairobi", "Naivasha", "Mombasa", "Kisumu", "Eldoret"]),
                start_time=datetime.now() + timedelta(days=random.randint(5, 60)),
                end_time=datetime.now() + timedelta(days=random.randint(5, 60), hours=4),
                category=random.choice(categories),
                tags="test,rejected",
                status="rejected",
                is_approved=False,
                image_url="https://source.unsplash.com/400x300/?rejected,event",
                organizer_id=org.id,
                attendee_count=0
            ))

    # Pending Events
    for org in organizer_users:
        for _ in range(3):
            pending_events.append(Event(
                title=f"{org.first_name}'s Pending Event",
                description="Pending approval.",
                location=random.choice(["Nairobi", "Naivasha", "Mombasa", "Kisumu", "Eldoret"]),
                start_time=datetime.now() + timedelta(days=random.randint(5, 60)),
                end_time=datetime.now() + timedelta(days=random.randint(5, 60), hours=4),
                category=random.choice(categories),
                tags="pending,unapproved",
                status="pending",
                is_approved=False,
                image_url="https://source.unsplash.com/400x300/?pending,event",
                organizer_id=org.id,
                attendee_count=0
            ))

    # One extra pending event
    extra_org = random.choice(organizer_users)
    pending_events.append(Event(
        title="Extra Pending Event",
        description="Extra pending event for distribution.",
        location="Eldoret",
        start_time=datetime.now() + timedelta(days=20),
        end_time=datetime.now() + timedelta(days=20, hours=4),
        category="Culture",
        tags="pending,extra",
        status="pending",
        is_approved=False,
        image_url="https://source.unsplash.com/400x300/?event,extra",
        organizer_id=extra_org.id,
        attendee_count=0
    ))

    # Approved Future Events
    for org in organizer_users:
        for _ in range(7):
            start = datetime.now() + timedelta(days=random.randint(5, 90))
            end = start + timedelta(hours=4)
            approved_future_events.append(Event(
                title=f"{org.first_name}'s Future Event",
                description="An exciting upcoming event.",
                location=random.choice(["Nairobi", "Naivasha", "Mombasa"]),
                start_time=start,
                end_time=end,
                category=random.choice(categories),
                tags="future,approved",
                status="approved",
                is_approved=True,
                image_url="https://source.unsplash.com/400x300/?event,future",
                organizer_id=org.id,
                attendee_count=0
            ))

    # Approved Past Events
    for _ in range(10):
        org = random.choice(organizer_users)
        start = datetime.now() - timedelta(days=random.randint(5, 90))
        end = start + timedelta(hours=5)
        approved_past_events.append(Event(
            title=f"{org.first_name}'s Past Event",
            description="An exciting past event.",
            location=random.choice(["Nairobi", "Kisumu", "Mombasa"]),
            start_time=start,
            end_time=end,
            category=random.choice(categories),
            tags="past,approved",
            status="approved",
            is_approved=True,
            image_url="https://source.unsplash.com/400x300/?event,past",
            organizer_id=org.id,
            attendee_count=0
        ))

    all_events = rejected_events + pending_events + approved_future_events + approved_past_events
    db.session.add_all(all_events)
    db.session.flush()

    # Create tickets for approved events
    for event in approved_future_events + approved_past_events:
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

    print("🌱 Seeding orders, passes, reviews...")
    for attendee in users[5:]:
        for _ in range(random.randint(2, 4)):
            ticket = random.choice(tickets)
            event = next((e for e in approved_future_events + approved_past_events if e.id == ticket.event_id), None)
            if not event:
                continue

            quantity = random.randint(1, 4)
            order = Order(
                order_id=str(uuid.uuid4()),
                attendee_id=attendee.id,
                status="paid",
                total_amount=ticket.price * quantity,
                mpesa_receipt=f"MPESA{random.randint(100000, 999999)}"
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

            event.attendee_count += quantity

            if event.start_time < datetime.now():
                db.session.add(Review(
                    rating=random.randint(3, 5),
                    comment=random.choice(["Amazing", "Loved it", "Inspiring", "Well organized"]),
                    attendee_id=attendee.id,
                    event_id=event.id
                ))

    db.session.commit()

    print("🌱 Seeding saved events & reports...")
    for attendee in users[5:]:
        for _ in range(random.randint(1, 4)):
            db.session.add(SavedEvent(
                user_id=attendee.id,
                event_id=random.choice(all_events).id
            ))

    for admin in users[:2]:
        for _ in range(10):
            event_id = random.choice(all_events).id
            db.session.add(Report(
                report_data="Auto-generated monthly performance.",
                admin_id=admin.id,
                event_id=event_id
            ))
            db.session.add(AuditLog(
                action="Generated report",
                user_id=admin.id,
                target_type="Event",
                target_id=event_id,
                status="Success",
                ip_address="127.0.0.1",
                extra_data={"tool": "Seeder", "reason": "load test"}
            ))

    db.session.commit()
    print("✅ Seeding complete.")
