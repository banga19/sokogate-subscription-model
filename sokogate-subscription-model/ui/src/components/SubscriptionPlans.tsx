import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface SubscriptionPlan {
  id: number;
  name: string;
  tier: string;
  description?: string;
  price: number;
  billing_frequency: string;
  preorder_limit_per_month: number;
  preorder_value_limit: number;
  early_access_days: number;
  discount_percentage: number;
  priority_support: boolean;
  dedicated_account_manager: boolean;
  custom_reporting: boolean;
  api_access: boolean;
  is_active: boolean;
}

const SubscriptionPlans: React.FC = () => {
  const [plans, setPlans] = useState<SubscriptionPlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPlans();
  }, []);

  const fetchPlans = async () => {
    try {
      const response = await axios.get('/api/v1/subscriptions/plans');
      setPlans(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch subscription plans');
      setLoading(false);
    }
  };

  if (loading) return <div className="text-center py-8">Loading...</div>;
  if (error) return <div className="text-center py-8 text-red-600">{error}</div>;

  return (
    <div className="px-4 py-8 sm:px-0">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900">Subscription Plans</h2>
        <p className="mt-2 text-gray-600">Choose the perfect plan for your business needs</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {plans.map((plan) => (
          <div key={plan.id} className="bg-white rounded-lg shadow-md p-6">
            <div className="mb-4">
              <h3 className="text-xl font-semibold text-gray-900">{plan.name}</h3>
              <p className="text-gray-600">{plan.tier}</p>
            </div>

            <div className="mb-4">
              <span className="text-3xl font-bold text-gray-900">${plan.price}</span>
              <span className="text-gray-600">/{plan.billing_frequency}</span>
            </div>

            {plan.description && (
              <p className="text-gray-700 mb-4">{plan.description}</p>
            )}

            <ul className="space-y-2 mb-6">
              <li className="flex items-center">
                <span className="text-green-500 mr-2">✓</span>
                {plan.preorder_limit_per_month} pre-orders per month
              </li>
              <li className="flex items-center">
                <span className="text-green-500 mr-2">✓</span>
                ${plan.preorder_value_limit.toLocaleString()} monthly value limit
              </li>
              <li className="flex items-center">
                <span className="text-green-500 mr-2">✓</span>
                {plan.early_access_days}-day early access
              </li>
              <li className="flex items-center">
                <span className="text-green-500 mr-2">✓</span>
                {plan.discount_percentage}% discount on pre-orders
              </li>
              {plan.priority_support && (
                <li className="flex items-center">
                  <span className="text-green-500 mr-2">✓</span>
                  Priority support
                </li>
              )}
              {plan.dedicated_account_manager && (
                <li className="flex items-center">
                  <span className="text-green-500 mr-2">✓</span>
                  Dedicated account manager
                </li>
              )}
              {plan.custom_reporting && (
                <li className="flex items-center">
                  <span className="text-green-500 mr-2">✓</span>
                  Custom reporting
                </li>
              )}
              {plan.api_access && (
                <li className="flex items-center">
                  <span className="text-green-500 mr-2">✓</span>
                  API access
                </li>
              )}
            </ul>

            <button className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition duration-200">
              Subscribe Now
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SubscriptionPlans;