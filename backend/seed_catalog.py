from app.database import Base, engine, SessionLocal
from app.models import Product

Base.metadata.create_all(bind=engine)
samples = [
    # Medicines
    dict(name='Paracetamol 500mg', category='Medicines', description='Fever and mild to moderate pain relief.', price=25.00, stock=150, prescription_required=False, image_url='https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500'),
    dict(name='Amoxicillin 250mg', category='Medicines', description='Antibiotic for bacterial infections. Valid doctor prescription required.', price=85.00, stock=60, prescription_required=True, image_url='https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500'),
    dict(name='Metformin 500mg', category='Medicines', description='Type 2 diabetes medication. Prescription required.', price=42.00, stock=80, prescription_required=True, image_url='https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500'),
    dict(name='Cetirizine 10mg', category='Medicines', description='Allergy relief antihistamine.', price=30.00, stock=120, prescription_required=False, image_url='https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500'),
    dict(name='Omeprazole 20mg', category='Medicines', description='Heartburn and acid reflux reduction.', price=55.00, stock=90, prescription_required=False, image_url='https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500'),
    # Vitamins
    dict(name='Vitamin C 500mg', category='Vitamins', description='Immune support supplement.', price=180.00, stock=40, prescription_required=False, image_url='https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=500'),
    dict(name='Vitamin D3 1000 IU', category='Vitamins', description='Bone health and daily immune function.', price=220.00, stock=150, prescription_required=False, image_url='https://images.unsplash.com/photo-1587854692152-cbe660dbde88?w=500'),
    dict(name='Omega-3 Fish Oil', category='Vitamins', description='Heart, joint and brain health support.', price=350.00, stock=100, prescription_required=False, image_url='https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=500'),
    dict(name='Multivitamin Daily', category='Vitamins', description='Comprehensive daily multivitamin with zinc.', price=299.00, stock=180, prescription_required=False, image_url='https://images.unsplash.com/photo-1626671155227-cf98c5ed7b73?w=500'),
    # Personal Care
    dict(name='Gentle Skin Care Lotion', category='Personal Care', description='Gentle daily moisturising lotion.', price=320.00, stock=18, prescription_required=False, image_url='https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=500'),
    dict(name='Antiseptic Hand Sanitiser', category='Personal Care', description='70% alcohol-based germ protection.', price=99.00, stock=300, prescription_required=False, image_url='https://images.unsplash.com/photo-1584265549882-284fd78f99b7?w=500'),
    dict(name='Medicated Anti-Dandruff Shampoo', category='Personal Care', description='Ketoconazole scalp therapy.', price=275.00, stock=45, prescription_required=False, image_url='https://images.unsplash.com/photo-1626201901862-e9b6e3e49adc?w=500'),
    # Health Devices
    dict(name='Digital Thermometer', category='Health Devices', description='Fast and accurate digital thermometer.', price=249.00, stock=25, prescription_required=False, image_url='https://images.unsplash.com/photo-1583947215259-38e31be8751f?w=500'),
    dict(name='Digital Blood Pressure Monitor', category='Health Devices', description='Automatic upper arm BP monitor with memory.', price=1899.00, stock=20, prescription_required=False, image_url='https://images.unsplash.com/photo-1615461066841-6116e61058f4?w=500'),
    dict(name='Fingertip Pulse Oximeter', category='Health Devices', description='SpO2 and pulse rate monitoring.', price=699.00, stock=35, prescription_required=False, image_url='https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500'),
    dict(name='Blood Glucose Monitor Kit', category='Health Devices', description='Glucometer kit with 25 test strips.', price=999.00, stock=6, prescription_required=False, image_url='https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500'),
    # Baby Care
    dict(name='Baby Care Essentials', category='Baby Care', description='Gentle baby lotion and wash pack.', price=150.00, stock=20, prescription_required=False, image_url='https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500'),
    dict(name='Natural Baby Massage Oil', category='Baby Care', description='Pure almond and sesame oil blend for infants.', price=185.00, stock=60, prescription_required=False, image_url='https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=500'),
    # Wellness
    dict(name='Ashwagandha Herbal Extract', category='Wellness', description='Stress reduction and vitality capsules.', price=420.00, stock=90, prescription_required=False, image_url='https://images.unsplash.com/photo-1540822659965-7e6c0d47acb4?w=500'),
    dict(name='Triphala Digestive Tablets', category='Wellness', description='Ayurvedic digestive balance formulation.', price=150.00, stock=110, prescription_required=False, image_url='https://images.unsplash.com/photo-1540822659965-7e6c0d47acb4?w=500'),
]
db = SessionLocal()
try:
    added = 0
    for item in samples:
        existing = db.query(Product).filter(Product.name == item['name']).first()
        if not existing:
            db.add(Product(**item))
            added += 1
    db.commit()
    print(f'Catalog seeded: added {added} new products.')
finally:
    db.close()
