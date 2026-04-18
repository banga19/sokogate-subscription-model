import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import {
  Check,
  Star,
  Zap,
  Crown,
  Shield
} from 'lucide-react';

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
  const { user } = useAuth();
  const [plans, setPlans] = useState<SubscriptionPlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [subscribing, setSubscribing] = useState<number | null>(null);

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

  const handleSubscribe = async (planId: number) => {
    if (!user) {
      alert('Please login to subscribe to a plan');
      return;
    }

    setSubscribing(planId);
    try {
      await axios.post('/api/v1/subscriptions/', {
        customer_id: user.id,
        plan_id: planId
      });
      alert('Subscription created successfully!');
    } catch (err) {
      alert('Failed to create subscription. Please try again.');
    } finally {
      setSubscribing(null);
    }
  };

  const getTierIcon = (tier: string) => {
    switch (tier.toLowerCase()) {
      case 'starter':
        return <Star className="w-6 h-6 text-blue-500" />;
      case 'professional':
        return <Zap className="w-6 h-6 text-purple-500" />;
      case 'enterprise':
        return <Crown className="w-6 h-6 text-yellow-500" />;
      default:
        return <Shield className="w-6 h-6 text-gray-500" />;
    }
  };

  const getTierColor = (tier: string) => {
    switch (tier.toLowerCase()) {
      case 'starter':
        return 'border-blue-200 bg-blue-50';
      case 'professional':
        return 'border-purple-200 bg-purple-50';
      case 'enterprise':
        return 'border-yellow-200 bg-yellow-50';
      default:
        return 'border-gray-200 bg-gray-50';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <p className="text-red-800">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="px-4 py-8 sm:px-0">
      <div className="text-center mb-12">
        <h2 className="text-4xl font-bold text-gray-900 mb-4">Choose Your Plan</h2>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Select the perfect subscription plan that fits your business needs and start benefiting from our construction materials platform.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-7xl mx-auto">
        {plans.map((plan) => (
          <div
            key={plan.id}
            className={`relative rounded-xl shadow-lg p-8 border-2 transition-all duration-300 hover:shadow-xl hover:scale-105 ${getTierColor(plan.tier)}`}
          >
            {plan.tier === 'Professional' && (
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                <span className="bg-purple-500 text-white px-4 py-1 rounded-full text-sm font-medium">
                  Most Popular
                </span>
              </div>
            )}

            <div className="text-center mb-6">
              <div className="flex justify-center mb-4">
                {getTierIcon(plan.tier)}
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">{plan.name}</h3>
              <p className="text-gray-600 mb-4">{plan.tier} Plan</p>

              <div className="mb-4">
                <span className="text-5xl font-bold text-gray-900">${plan.price}</span>
                <span className="text-gray-600 text-lg">/{plan.billing_frequency}</span>
              </div>

              {plan.description && (
                <p className="text-gray-700 text-sm">{plan.description}</p>
              )}
            </div>

            <div className="space-y-4 mb-8">
              <div className="flex items-center">
                <Check className="w-5 h-5 text-green-500 mr-3 flex-shrink-0" />
                <span className="text-gray-700">
                  <strong>{plan.preorder_limit_per_month}</strong> pre-orders per month
                </span>
              </div>

              <div className="flex items-center">
                <Check className="w-5 h-5 text-green-500 mr-3 flex-shrink-0" />
                <span className="text-gray-700">
                  <strong>${plan.preorder_value_limit.toLocaleString()}</strong> monthly value limit
                </span>
              </div>

              <div className="flex items-center">
                <Check className="w-5 h-5 text-green-500 mr-3 flex-shrink-0" />
                <span className="text-gray-700">
                  <strong>{plan.early_access_days}-day</strong> early access to materials
                </span>
              </div>

              <div className="flex items-center">
                <Check className="w-5 h-5 text-green-500 mr-3 flex-shrink-0" />
                <span className="text-gray-700">
                  <strong>{plan.discount_percentage}%</strong> discount on pre-orders
                </span>
              </div>

              {plan.priority_support && (
                <div className="flex items-center">
                  <Check className="w-5 h-5 text-green-500 mr-3 flex-shrink-0" />
                  <span className="text-gray-700">Priority customer support</span>
                </div>
              )}

              {plan.dedicated_account_manager && (
                <div className="flex items-center">
                  <Check className="w-5 h-5 text-green-500 mr-3 flex-shrink-0" />
                  <span className="text-gray-700">Dedicated account manager</span>
                </div>
              )}

              {plan.custom_reporting && (
                <div className="flex items-center">
                  <Check className="w-5 h-5 text-green-500 mr-3 flex-shrink-0" />
                  <span className="text-gray-700">Custom reporting & analytics</span>
                </div>
              )}

              {plan.api_access && (
                <div className="flex items-center">
                  <Check className="w-5 h-5 text-green-500 mr-3 flex-shrink-0" />
                  <span className="text-gray-700">API access for integrations</span>
                </div>
              )}
            </div>

            <button
              onClick={() => handleSubscribe(plan.id)}
              disabled={subscribing === plan.id}
              className={`w-full py-3 px-6 rounded-lg font-semibold text-white transition-all duration-200 ${
                plan.tier === 'Professional'
                  ? 'bg-purple-600 hover:bg-purple-700 shadow-lg'
                  : 'bg-gray-800 hover:bg-gray-900'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              {subscribing === plan.id ? 'Subscribing...' : 'Subscribe Now'}
            </button>
          </div>
        ))}
      </div>

      <div className="text-center mt-12">
        <p className="text-gray-600">
          Need a custom plan?{' '}
          <a href="mailto:contact@sokogate.com" className="text-blue-600 hover:text-blue-800 font-medium">
            Contact our sales team
          </a>
        </p>
      </div>
    </div>
  );
};

export default SubscriptionPlans;