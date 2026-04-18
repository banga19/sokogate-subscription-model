# Sokogate Subscription Model UI

A React-based web interface for managing Sokogate's B2B subscription system.

## Features

- **Subscription Plans**: View available subscription tiers with detailed features
- **Subscription Management**: Manage active subscriptions, pause/resume/cancel
- **Pre-Order System**: Create and track pre-orders with priority levels
- **Responsive Design**: Modern UI built with Tailwind CSS

## Tech Stack

- React 18 with TypeScript
- Vite for build tooling
- Tailwind CSS for styling
- Axios for API calls
- React Router for navigation

## Getting Started

### Prerequisites

- Node.js 16+
- npm or yarn

### Installation

1. Navigate to the UI directory:
   ```bash
   cd ui
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

The UI will be available at `http://localhost:5173`

### Backend Setup

The UI expects the FastAPI backend to be running on `http://localhost:8000`. Make sure to:

1. Set up the Python virtual environment
2. Install backend dependencies: `pip install -r requirements.txt`
3. Start the backend: `python3 main.py`

## API Integration

The UI communicates with the backend through the following endpoints:

- `GET /api/v1/subscriptions/plans` - Get subscription plans
- `GET /api/v1/subscriptions/customer/{customer_id}` - Get customer subscriptions
- `POST /api/v1/subscriptions/{subscription_id}/pre-orders` - Create pre-order
- `GET /api/v1/subscriptions/{subscription_id}/pre-orders` - Get pre-orders

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Project Structure

```
src/
├── components/
│   ├── SubscriptionPlans.tsx
│   ├── Subscriptions.tsx
│   └── PreOrders.tsx
├── App.tsx
├── main.tsx
└── index.css
```

## Usage

1. **View Plans**: Browse available subscription tiers on the Plans page
2. **Manage Subscriptions**: View and manage your subscriptions on the Subscriptions page
3. **Create Pre-Orders**: Use the Pre-Orders page to place orders for upcoming products

Note: This is a demo UI. In production, authentication and proper customer ID management would be implemented.