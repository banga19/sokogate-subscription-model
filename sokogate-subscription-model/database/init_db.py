from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import yaml
from datetime import datetime
from ..models.subscription import Base, SubscriptionPlan, Customer
from ..config.settings import DATABASE_URL

def load_subscription_plans():
    """Load subscription plans from YAML configuration"""
    with open('config/subscription_plans.yaml', 'r') as file:
        config = yaml.safe_load(file)
    return config['subscription_plans']

def create_database():
    """Create database tables"""
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    return engine

def seed_subscription_plans(engine):
    """Seed the database with subscription plans from config"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Load plans from YAML
        plans_config = load_subscription_plans()
        
        for tier, plan_data in plans_config.items():
            # Create plans for each billing frequency
            for billing_freq, price in plan_data['pricing'].items():
                existing_plan = db.query(SubscriptionPlan).filter(
                    SubscriptionPlan.tier == tier,
                    SubscriptionPlan.billing_frequency == billing_freq
                ).first()
                
                if not existing_plan:
                    plan = SubscriptionPlan(
                        name=f"{plan_data['name']} - {billing_freq.title()}",
                        tier=tier,
                        description=plan_data['description'],
                        price=price,
                        billing_frequency=billing_freq,
                        preorder_limit_per_month=plan_data['features']['preorder_limit_per_month'],
                        preorder_value_limit=plan_data['features']['preorder_value_limit'],
                        early_access_days=plan_data['features']['early_access_days'],
                        discount_percentage=plan_data['features']['discount_percentage'],
                        priority_support=plan_data['features']['priority_support'],
                        dedicated_account_manager=plan_data['features']['dedicated_account_manager'],
                        custom_reporting=plan_data['features']['custom_reporting'],
                        api_access=plan_data['features']['api_access'],
                        is_active=True
                    )
                    db.add(plan)
        
        db.commit()
        print("Subscription plans seeded successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding subscription plans: {e}")
    finally:
        db.close()

def create_sample_data(engine):
    """Create sample customers and data for testing"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Sample customers
        sample_customers = [
            {
                "company_name": "TechStart Inc.",
                "contact_email": "admin@techstart.com",
                "contact_phone": "+1-555-0101",
                "business_type": "Technology Startup",
                "billing_address": {
                    "street": "123 Tech Street",
                    "city": "San Francisco",
                    "state": "CA",
                    "zip": "94105",
                    "country": "USA"
                },
                "shipping_address": {
                    "street": "123 Tech Street",
                    "city": "San Francisco", 
                    "state": "CA",
                    "zip": "94105",
                    "country": "USA"
                }
            },
            {
                "company_name": "Global Retail Corp",
                "contact_email": "procurement@globalretail.com",
                "contact_phone": "+1-555-0202",
                "business_type": "Retail",
                "billing_address": {
                    "street": "456 Commerce Ave",
                    "city": "New York",
                    "state": "NY", 
                    "zip": "10001",
                    "country": "USA"
                },
                "shipping_address": {
                    "street": "789 Warehouse Blvd",
                    "city": "Newark",
                    "state": "NJ",
                    "zip": "07102", 
                    "country": "USA"
                }
            },
            {
                "company_name": "Manufacturing Solutions Ltd",
                "contact_email": "orders@manufacturingsolutions.com",
                "contact_phone": "+1-555-0303",
                "business_type": "Manufacturing",
                "credit_limit": 100000.00,
                "payment_terms": "net_45",
                "billing_address": {
                    "street": "321 Industrial Way",
                    "city": "Detroit",
                    "state": "MI",
                    "zip": "48201",
                    "country": "USA"
                },
                "shipping_address": {
                    "street": "321 Industrial Way",
                    "city": "Detroit",
                    "state": "MI", 
                    "zip": "48201",
                    "country": "USA"
                }
            }
        ]
        
        for customer_data in sample_customers:
            existing_customer = db.query(Customer).filter(
                Customer.contact_email == customer_data["contact_email"]
            ).first()
            
            if not existing_customer:
                customer = Customer(**customer_data)
                db.add(customer)
        
        db.commit()
        print("Sample customers created successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error creating sample data: {e}")
    finally:
        db.close()

def main():
    """Main initialization function"""
    print("Initializing Sokogate Subscription Database...")
    
    # Create database and tables
    engine = create_database()
    print("Database tables created successfully!")
    
    # Seed subscription plans
    seed_subscription_plans(engine)
    
    # Create sample data
    create_sample_data(engine)
    
    print("Database initialization complete!")

if __name__ == "__main__":
    main()
