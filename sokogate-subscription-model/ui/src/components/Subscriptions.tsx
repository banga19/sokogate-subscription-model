import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface SubscriptionPlan {
  id: number;
  name: string;
  tier: string;
  price: number;
  billing_frequency: string;
}

interface Subscription {
  id: number;
  customer_id: number;
  subscription_plan_id: number;
  status: string;
  start_date: string;
  end_date?: string;
  next_billing_date?: string;
  monthly_preorder_limit: number;
  current_month_preorders: number;
  total_preorder_value_limit: number;
  current_preorder_value: number;
  auto_renew: boolean;
  subscription_plan: SubscriptionPlan;
}

const Subscriptions: React.FC = () => {
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSubscriptions();
  }, []);

  const fetchSubscriptions = async () => {
    try {
      // For demo purposes, using customer_id 1. In real app, get from auth
      const response = await axios.get('/api/v1/subscriptions/customer/1');
      setSubscriptions(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch subscriptions');
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'paused':
        return 'bg-yellow-100 text-yellow-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) return <div className="text-center py-8">Loading...</div>;
  if (error) return <div className="text-center py-8 text-red-600">{error}</div>;

  return (
    <div className="px-4 py-8 sm:px-0">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900">My Subscriptions</h2>
        <p className="mt-2 text-gray-600">Manage your active subscriptions</p>
      </div>

      {subscriptions.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500">No subscriptions found. Subscribe to a plan to get started.</p>
        </div>
      ) : (
        <div className="space-y-6">
          {subscriptions.map((subscription) => (
            <div key={subscription.id} className="bg-white rounded-lg shadow-md p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-semibold text-gray-900">
                    {subscription.subscription_plan.name}
                  </h3>
                  <p className="text-gray-600">{subscription.subscription_plan.tier}</p>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(subscription.status)}`}>
                  {subscription.status}
                </span>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div>
                  <p className="text-sm text-gray-500">Price</p>
                  <p className="font-semibold">${subscription.subscription_plan.price}/{subscription.subscription_plan.billing_frequency}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Pre-orders Used</p>
                  <p className="font-semibold">{subscription.current_month_preorders}/{subscription.monthly_preorder_limit}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Value Used</p>
                  <p className="font-semibold">${subscription.current_preorder_value.toLocaleString()}/${subscription.total_preorder_value_limit.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Next Billing</p>
                  <p className="font-semibold">
                    {subscription.next_billing_date ? new Date(subscription.next_billing_date).toLocaleDateString() : 'N/A'}
                  </p>
                </div>
              </div>

              <div className="flex space-x-4">
                <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition duration-200">
                  Manage
                </button>
                {subscription.status === 'active' && (
                  <button className="bg-yellow-600 text-white px-4 py-2 rounded-md hover:bg-yellow-700 transition duration-200">
                    Pause
                  </button>
                )}
                <button className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition duration-200">
                  Cancel
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Subscriptions;