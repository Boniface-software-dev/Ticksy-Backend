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

    # Attendees
    attendees = [
        {"first_name": "Kevin", "last_name": "Odhiambo", "email": "kevin@gmail.com", "phone": "0711221122"},
        {"first_name": "Grace", "last_name": "Wambui", "email": "grace@gmail.com", "phone": "0702334455"},
        {"first_name": "Dennis", "last_name": "Kiptoo", "email": "dennis@gmail.com", "phone": "0711445566"},
        {"first_name": "Sharon", "last_name": "Achieng", "email": "sharon@gmail.com", "phone": "0722334455"},
        {"first_name": "Abdi", "last_name": "Hussein", "email": "abdi@gmail.com", "phone": "0701443344"},
    ]

    for att in attendees:
        users.append(User(
            first_name=att["first_name"],
            last_name=att["last_name"],
            email=att["email"],
            phone=att["phone"],
            password=bcrypt.generate_password_hash("attendee123").decode('utf-8'),
            role="attendee"
        ))

    db.session.add_all(users)
    db.session.commit()

    print("🌱 Seeding events & tickets...")

    sample_events = [
        {
            "title": "Blankets & Wine Nairobi",
            "desc": "A premier music and arts experience in Nairobi.",
            "image": "https://media.istockphoto.com/id/638492408/vector/craft-beer-festival-poster-design-template.jpg?s=612x612&w=0&k=20&c=GDHheEEP5gm4MHokMlbmrKMuEiXUtmFQwZUc-JBpAU0=",
            "location": "Loresho Gardens",
            "category": "Music",
            "tags": "music,live,fun"
        },
        {
            "title": "Koroga Festival",
            "desc": "Celebrating African music, food and culture.",
            "image": "https://media.istockphoto.com/id/1382746448/vector/covid19-new-variant-web-banner-template-and-video-thumbnail-editable-promotion-banner-design.jpg?s=1024x1024&w=is&k=20&c=7AspM_7IK6tXtdvMQAtXLF7K2shPlr6OFnUjqLNSdsU=",
            "location": "Carnivore Grounds",
            "category": "Culture",
            "tags": "afrobeat,food,festival"
        },
        {
            "title": "Nairobi Restaurant Week",
            "desc": "Taste the best from top Nairobi restaurants.",
            "image": "https://media.istockphoto.com/id/1188510295/vector/abstract-vector-colorful-gradient-landing-page-template.jpg?s=612x612&w=0&k=20&c=UhbIpbiUJ1RV9c9w8RqBv5MDShCbWvN4o29BreCMaIw=",
            "location": "Various Locations",
            "category": "Food",
            "tags": "foodie,restaurants,cuisine"
        },
        {
            "title": "Lake Naivasha Hike & Camp",
            "desc": "Join us for an exciting adventure and bonfire night.",
            "image": "https://media.istockphoto.com/id/1364100879/vector/se-strong-with-our-training-social-media-post-design-template-use-green-gradient-colors-on.jpg?s=612x612&w=0&k=20&c=Rv9WcfBAmSgNgiWaXwPpCMSs5Px4X6jecx7RluRjSZ4=",
            "location": "Naivasha",
            "category": "Adventure",
            "tags": "hiking,camping,nature"
        },
        {
            "title": "Techstars Startup Weekend Nairobi",
            "desc": "Bring your startup idea to life in 54 hours.",
            "image": "https://media.istockphoto.com/id/1364100879/vector/se-strong-with-our-training-social-media-post-design-template-use-green-gradient-colors-on.jpg?s=612x612&w=0&k=20&c=Rv9WcfBAmSgNgiWaXwPpCMSs5Px4X6jecx7RluRjSZ4=",
            "location": "iHub, Nairobi",
            "category": "Tech",
            "tags": "startup,networking,pitch"
        },
        {
            "title": "Art in the Park",
            "desc": "Explore contemporary art from local artists.",
            "image": "https://media.istockphoto.com/id/1364100879/vector/se-strong-with-our-training-social-media-post-design-template-use-green-gradient-colors-on.jpg?s=612x612&w=0&k=20&c=Rv9WcfBAmSgNgiWaXwPpCMSs5Px4X6jecx7RluRjSZ4=",
            "location": "Uhuru Park",
            "category": "Art",
            "tags": "art,exhibition,local"
        },
        {
            "title": "Nairobi Fashion Week",
            "desc": "Showcasing the best of African fashion.",
            "image": "https://media.istockphoto.com/id/1364100879/vector/se-strong-with-our-training-social-media-post-design-template-use-green-gradient-colors-on.jpg?s=612x612&w=0&k=20&c=Rv9WcfBAmSgNgiWaXwPpCMSs5Px4X6jecx7RluRjSZ4=",
            "location": "Sarova Panafric Hotel",
            "category": "Fashion",
            "tags": "fashion,design,style"
        },
        {
            "title": "Nairobi Book Fair",
            "desc": "A celebration of literature and authors.",
            "image": "https://media.istockphoto.com/id/1364100879/vector/se-strong-with-our-training-social-media-post-design-template-use-green-gradient-colors-on.jpg?s=612x612&w=0&k=20&c=Rv9WcfBAmSgNgiWaXwPpCMSs5Px4X6jecx7RluRjSZ4=",
            "location": "Kenyatta International Convention Centre",
            "category": "Literature",
            "tags": "books,authors,reading"
        },
        {
            "title": "Nairobi Film Festival",
            "desc": "Screening the best of local and international films.",
            "image": "https://media.istockphoto.com/id/1364100879/vector/se-strong-with-our-training-social-media-post-design-template-use-green-gradient-colors-on.jpg?s=612x612&w=0&k=20&c=Rv9WcfBAmSgNgiWaXwPpCMSs5Px4X6jecx7RluRjSZ4=",
            "location": "Prestige Cinema",
            "category": "Film",
            "tags": "movies,screening,cinema"
        },
        {
            "title": "Nairobi Tech Expo",
            "desc": "Showcasing the latest in technology and innovation.",
            "image": "https://media.istockphoto.com/id/1364100879/vector/se-strong-with-our-training-social-media-post-design-template-use-green-gradient-colors-on.jpg?s=612x612&w=0&k=20&c=Rv9WcfBAmSgNgiWaXwPpCMSs5Px4X6jecx7RluRjSZ4=",
            "location": "Kenyatta International Convention Centre",
            "category": "Tech",
            "tags": "technology,innovation,expo"
        },
        {
            "title": "Nairobi Jazz Festival",
            "desc": "Celebrating jazz music with top local and international artists.",
            "image": "https://media.istockphoto.com/id/1364100879/vector/se-strong-with-our-training-social-media-post-design-template-use-green-gradient-colors-on.jpg?s=612x612&w=0&k=20&c=Rv9WcfBAmSgNgiWaXwPpCMSs5Px4X6jecx7RluRjSZ4=",
            "location": "Carnivore Grounds",
            "category": "Music",
            "tags": "jazz,live,concert"
        },
        {
            "title": "Nairobi Photography Exhibition",
            "desc": "Showcasing stunning photography from local artists.",
            "image": "https://media.istockphoto.com/id/1364100879/vector/se-strong-with-our-training-social-media-post-design-template-use-green-gradient-colors-on.jpg?s=612x612&w=0&k=20&c=Rv9WcfBAmSgNgiWaXwPpCMSs5Px4X6jecx7RluRjSZ4=",
            "location": "Alliance Française",
            "category": "Art",
            "tags": "photography,exhibition,art"
        } 

        
    ]

    events = []
    tickets = []

    for idx, ev in enumerate(sample_events):
        organizer = users[2 + (idx % 3)]
        event = Event(
            title=ev["title"],
            description=ev["desc"],
            location=ev["location"],
            start_time=datetime.now() + timedelta(days=idx+1),
            end_time=datetime.now() + timedelta(days=idx+1, hours=4),
            category=ev["category"],
            tags=ev["tags"],
            status="approved",
            is_approved=True,
            image_url=ev["image"],
            organizer_id=organizer.id,
            attendee_count=0
        )
        db.session.add(event)
        db.session.flush()
        events.append(event)

        tickets.append(Ticket(type="Regular", price=1500.00, quantity=150, sold=40, event_id=event.id))
        tickets.append(Ticket(type="VIP", price=3000.00, quantity=50, sold=10, event_id=event.id))

    db.session.add_all(tickets)
    db.session.commit()

    print("🌱 Seeding orders, order items, passes, reviews...")

    for attendee in users[-5:]:
        for _ in range(2):
            ticket = random.choice(tickets)
            quantity = random.randint(1, 2)
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

            for q in range(quantity):
                db.session.add(EventPass(
                    ticket_code=str(uuid.uuid4())[:8].upper(),
                    attendee_first_name=f"Guest{q+1}",
                    attendee_last_name=attendee.last_name,
                    attendee_email=f"guest{q+1}_{attendee.email}",
                    attendee_phone=f"07{random.randint(10000000,99999999)}",
                    att_status=random.choice([True, False]),
                    order_item_id=item.id
                ))

            ticket.event.attendee_count += quantity

            if random.choice([True, False]):
                db.session.add(Review(
                    rating=random.randint(3, 5),
                    comment=random.choice(["Loved it!", "Great experience!", "Would attend again."]),
                    attendee_id=attendee.id,
                    event_id=ticket.event.id
                ))

    db.session.commit()

    print("🌱 Seeding saved events...")
    for attendee in users[-5:]:
        db.session.add(SavedEvent(user_id=attendee.id, event_id=random.choice(events).id))

    db.session.commit()

    print("🌱 Seeding reports & logs...")
    for admin in users[:2]:
        db.session.add(Report(
            report_data="Analytics for July Events.",
            admin_id=admin.id,
            event_id=random.choice(events).id
        ))

        db.session.add(AuditLog(
            action="Seeded initial test events",
            user_id=admin.id,
            target_type="Event",
            target_id=random.choice(events).id,
            status="Success",
            ip_address="127.0.0.1",
            extra_data={"note": "Initial seed"}
        ))

    db.session.commit()
    print("Seeding complete")
