# Sokogate B2B Subscription & Pre-Order System

A comprehensive subscription management system for Sokogate's B2B e-commerce platform that enables customers to subscribe to different tiers and pre-order products with various benefits and limitations.

## 🚀 Features

### Subscription Management
- **Three-tier subscription system** (Basic, Premium, Enterprise)
- **Flexible billing cycles** (Monthly, Quarterly, Annual)
- **Automated recurring billing** with payment processing
- **Subscription lifecycle management** (Create, Pause, Resume, Cancel)
- **Usage tracking and limits** enforcement

### Pre-Order System
- **Tiered pre-order limits** based on subscription level
- **Early access periods** for subscribers
- **Automatic discounts** based on subscription tier
- **Pre-order scheduling** with availability windows
- **Priority levels** for order processing
- **Real-time inventory tracking** for pre-order limits

### Analytics & Reporting
- **Subscription usage analytics**
- **Pre-order performance metrics**
- **Customer behavior tracking**
- **Revenue reporting** by subscription tier
- **Custom reporting** (Premium/Enterprise tiers)

## 📋 Subscription Tiers

### Basic - $29.99/month
- ✅ 10 pre-orders per month
- ✅ $5,000 monthly pre-order value limit
- ✅ 3-day early access to new products
- ✅ 2.5% discount on all pre-orders
- ✅ API access
- ✅ Track up to 100 products

### Premium - $79.99/month
- ✅ 50 pre-orders per month
- ✅ $25,000 monthly pre-order value limit
- ✅ 7-day early access to new products
- ✅ 5% discount on all pre-orders
- ✅ Priority support
- ✅ Custom reporting dashboard
- ✅ Advanced analytics
- ✅ Track up to 500 products
- ✅ Bulk operations

### Enterprise - $199.99/month
- ✅ **Unlimited** pre-orders
- ✅ **Unlimited** pre-order value
- ✅ 14-day early access to new products
- ✅ 7.5% discount on all pre-orders
- ✅ Dedicated account manager
- ✅ 99.9% SLA guarantee
- ✅ Custom integrations
- ✅ White-label options
- ✅ All Premium features included

## 🏗️ Architecture

### Database Models
```
├── Subscription
│   ├── Customer relationship
│   ├── SubscriptionPlan relationship
│   ├── Pre-order limits and tracking
│   └── Billing information
├── SubscriptionPlan
│   ├── Pricing tiers
│   ├── Feature definitions
│   └── Billing frequencies
├── PreOrder
│   ├── Product relationships
│   ├── Pricing and discounts
│   ├── Status tracking
│   └── Fulfillment information
├── Customer
│   ├── Business information
│   ├── Billing/shipping addresses
│   └── Credit and payment terms
└── Product
    ├── Pre-order eligibility
    ├── Availability windows
    └── Pricing information
```

### API Structure
```
├── /api/v1/subscriptions/
│   ├── GET /plans - List subscription plans
│   ├── POST / - Create subscription
│   ├── GET /{id} - Get subscription details
│   ├── PUT /{id}/pause - Pause subscription
│   ├── PUT /{id}/resume - Resume subscription
│   ├── DELETE /{id} - Cancel subscription
│   ├── GET /{id}/usage - Usage statistics
│   ├── POST /{id}/pre-orders - Create pre-order
│   ├── GET /{id}/pre-orders - List pre-orders
│   └── PUT /pre-orders/{id}/cancel - Cancel pre-order
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 18+ (for frontend development)
- PostgreSQL or MySQL database (or SQLite for development)
- Redis (for caching)
- Stripe account (for payments)

### Installation Steps

1. **Clone the repository**
```bash
git clone https://github.com/sokogate/subscription-system.git
cd subscription-system
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize database**
```bash
python database/init_db.py
```

6. **Run the application**
```bash
uvicorn main:app --reload
```

## Frontend Setup

The frontend is built with React, TypeScript, and Vite.

1. **Navigate to the frontend directory**
```bash
cd ui
```

2. **Install frontend dependencies**
```bash
npm install
```

3. **Start the development server**
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173` (default Vite port).

## Running the Full Application

To run both backend and frontend simultaneously:

1. **Start the backend** (in one terminal):
```bash
cd /path/to/sokogate-subscription-model
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

2. **Start the frontend** (in another terminal):
```bash
cd ui
npm run dev
```

3. **Access the application**:
   - Frontend: `http://localhost:5173`
   - Backend API: `http://localhost:8000`
   - API Documentation: `http://localhost:8000/docs` (Swagger UI)

### Environment Configuration

For the frontend to communicate with the backend, ensure the API base URL is correctly set in the frontend code (usually in `src/contexts/AuthContext.tsx` or similar).

### Development Notes
- The backend includes CORS middleware to allow requests from the frontend.
- For production deployment, configure the frontend build and backend accordingly.
- Database migrations can be run with `alembic upgrade head` if using Alembic for schema changes.
```env
DATABASE_URL=postgresql://user:password@localhost/sokogate_subscriptions
STRIPE_SECRET_KEY=sk_test_your_stripe_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
REDIS_URL=redis://localhost:6379
ALLOWED_ORIGINS=["http://localhost:3000", "https://app.sokogate.com"]
```

## 📡 API Usage Examples

### Create a Subscription
```python
import requests

response = requests.post("http://localhost:8000/api/v1/subscriptions/", json={
    "customer_id": 1,
    "subscription_plan_id": 2,
    "payment_method_id": "pm_1234567890",
    "auto_renew": True
})
```

### Create a Pre-Order
```python
response = requests.post("http://localhost:8000/api/v1/subscriptions/1/pre-orders", json={
    "product_id": 101,
    "quantity": 5,
    "priority_level": 1
})
```

### Get Subscription Usage
```python
response = requests.get("http://localhost:8000/api/v1/subscriptions/1/usage")
print(response.json())
# {
#   "current_month_preorders": 8,
#   "monthly_preorder_limit": 10,
#   "current_preorder_value": 2500.00,
#   "total_preorder_value_limit": 5000.00,
#   "usage_percentage": {
#     "orders": 80,
#     "value": 50
#   }
# }
```

## 🔄 Business Logic Flow

### Subscription Creation Flow
1. **Validate customer** and subscription plan
2. **Check for existing** active subscriptions
3. **Process initial payment** via Stripe
4. **Create subscription** record with limits
5. **Send welcome notification** to customer
6. **Set up recurring billing** schedule

### Pre-Order Creation Flow
1. **Validate subscription** is active
2. **Check product eligibility** for pre-orders
3. **Validate availability window** and inventory limits
4. **Check subscription limits** (count and value)
5. **Calculate pricing** with subscription discounts
6. **Create pre-order** and update counters
7. **Send confirmation** to customer

### Billing Cycle Processing
1. **Find subscriptions** due for renewal
2. **Process payments** for each subscription
3. **Update billing dates** and reset counters
4. **Handle failed payments** with retry logic
5. **Send notifications** for billing events

## 🔒 Security Features

- **API authentication** with JWT tokens
- **Payment data encryption** with Stripe
- **Rate limiting** on API endpoints
- **Input validation** and sanitization
- **SQL injection protection** with SQLAlchemy ORM
- **CORS configuration** for web security

## 📊 Monitoring & Analytics

### Key Metrics Tracked
- **Monthly Recurring Revenue (MRR)** by tier
- **Customer churn rate** and retention
- **Pre-order conversion rates**
- **Average order value** by subscription tier
- **API usage** and performance metrics
- **Payment success/failure rates**

### Available Reports
- Subscription tier distribution
- Pre-order volume trends
- Customer lifetime value
- Revenue forecasting
- Usage pattern analysis

## 🧪 Testing

### Run Tests
```bash
pytest tests/ -v
```

### Test Coverage
```bash
pytest --cov=. tests/
```

### API Testing
Use the included Postman collection or access the interactive API docs at:
```
http://localhost:8000/docs
```

## 🚀 Deployment

### Docker Deployment
```bash
docker build -t sokogate-subscriptions .
docker run -p 8000:8000 --env-file .env sokogate-subscriptions
```

### Production Considerations
- Use a production WSGI server (e.g., Gunicorn)
- Set up database connection pooling
- Configure Redis for caching and sessions
- Set up monitoring with Prometheus/Grafana
- Configure log aggregation
- Set up backup and disaster recovery

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support and questions:
- 📧 Email: support@sokogate.com
- 💬 Slack: #subscription-system
- 📖 Documentation: https://docs.sokogate.com/subscriptions
- 🐛 Issues: https://github.com/sokogate/subscription-system/issues

## 🗺️ Roadmap

### Q1 2025
- [ ] Add webhook support for real-time notifications
- [ ] Implement subscription plan migrations
- [ ] Add multi-currency support
- [ ] Enhanced analytics dashboard

### Q2 2025
- [ ] Mobile app API endpoints
- [ ] Advanced discount rules engine
- [ ] Subscription pause/resume improvements
- [ ] Integration with inventory management

### Q3 2025
- [ ] Machine learning for demand forecasting
- [ ] Advanced reporting suite
- [ ] Multi-tenant architecture
- [ ] Enhanced security features
