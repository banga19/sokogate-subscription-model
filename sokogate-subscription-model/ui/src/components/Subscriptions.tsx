import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import {
  Calendar,
  DollarSign,
  Package,
  TrendingUp,
  Pause,
  Play,
  X,
  Settings,
  AlertCircle,
  CheckCircle,
  Clock
} from 'lucide-react';

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
  const { user } = useAuth();
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<number | null>(null);

  useEffect(() => {
    if (user) {
      fetchSubscriptions();
    } else {
      setLoading(false);
    }
  }, [user]);

  const fetchSubscriptions = async () => {
    if (!user) return;

    try {
      const response = await axios.get(`/api/v1/subscriptions/customer/${user.id}`);
      setSubscriptions(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch subscriptions');
      setLoading(false);
    }
  };

  const handlePauseSubscription = async (subscriptionId: number) => {
    setActionLoading(subscriptionId);
    try {
      await axios.patch(`/api/v1/subscriptions/${subscriptionId}`, { status: 'paused' });
      await fetchSubscriptions();
    } catch (err) {
      alert('Failed to pause subscription');
    } finally {
      setActionLoading(null);
    }
  };

  const handleResumeSubscription = async (subscriptionId: number) => {
    setActionLoading(subscriptionId);
    try {
      await axios.patch(`/api/v1/subscriptions/${subscriptionId}`, { status: 'active' });
      await fetchSubscriptions();
    } catch (err) {
      alert('Failed to resume subscription');
    } finally {
      setActionLoading(null);
    }
  };

  const handleCancelSubscription = async (subscriptionId: number) => {
    if (!confirm('Are you sure you want to cancel this subscription?')) return;

    setActionLoading(subscriptionId);
    try {
      await axios.patch(`/api/v1/subscriptions/${subscriptionId}`, { status: 'cancelled' });
      await fetchSubscriptions();
    } catch (err) {
      alert('Failed to cancel subscription');
    } finally {
      setActionLoading(null);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'paused':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'cancelled':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return <CheckCircle className="w-4 h-4" />;
      case 'paused':
        return <Pause className="w-4 h-4" />;
      case 'cancelled':
        return <X className="w-4 h-4" />;
      default:
        return <Clock className="w-4 h-4" />;
    }
  };

  const getUsagePercentage = (current: number, limit: number) => {
    return Math.min((current / limit) * 100, 100);
  };

  if (!user) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">Authentication Required</h3>
        <p className="mt-1 text-sm text-gray-500">Please login to view your subscriptions.</p>
      </div>
    );
  }

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
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900">My Subscriptions</h2>
        <p className="mt-2 text-gray-600">Manage your active subscriptions and monitor usage</p>
      </div>

      {subscriptions.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <Package className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No subscriptions found</h3>
          <p className="mt-1 text-sm text-gray-500">
            Subscribe to a plan to get started with Sokogate.
          </p>
          <div className="mt-6">
            <button
              onClick={() => window.location.hash = '#plans'}
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
            >
              View Plans
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          {subscriptions.map((subscription) => (
            <div key={subscription.id} className="bg-white rounded-lg shadow-lg border border-gray-200 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200">
                <div className="flex justify-between items-start">
                  <div className="flex items-center space-x-3">
                    <div className="flex-shrink-0">
                      <Package className="h-8 w-8 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="text-xl font-semibold text-gray-900">
                        {subscription.subscription_plan.name}
                      </h3>
                      <p className="text-gray-600">{subscription.subscription_plan.tier} Plan</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(subscription.status)}
                    <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getStatusColor(subscription.status)}`}>
                      {subscription.status.charAt(0).toUpperCase() + subscription.status.slice(1)}
                    </span>
                  </div>
                </div>
              </div>

              <div className="px-6 py-4">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
                  <div className="text-center">
                    <div className="flex items-center justify-center mb-2">
                      <DollarSign className="h-5 w-5 text-gray-400" />
                    </div>
                    <p className="text-sm text-gray-500">Price</p>
                    <p className="text-lg font-semibold text-gray-900">
                      ${subscription.subscription_plan.price}
                      <span className="text-sm text-gray-500">/{subscription.subscription_plan.billing_frequency}</span>
                    </p>
                  </div>

                  <div className="text-center">
                    <div className="flex items-center justify-center mb-2">
                      <Package className="h-5 w-5 text-gray-400" />
                    </div>
                    <p className="text-sm text-gray-500">Pre-orders Used</p>
                    <div className="space-y-1">
                      <p className="text-lg font-semibold text-gray-900">
                        {subscription.current_month_preorders}/{subscription.monthly_preorder_limit}
                      </p>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{ width: `${getUsagePercentage(subscription.current_month_preorders, subscription.monthly_preorder_limit)}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>

                  <div className="text-center">
                    <div className="flex items-center justify-center mb-2">
                      <TrendingUp className="h-5 w-5 text-gray-400" />
                    </div>
                    <p className="text-sm text-gray-500">Value Used</p>
                    <div className="space-y-1">
                      <p className="text-lg font-semibold text-gray-900">
                        ${subscription.current_preorder_value.toLocaleString()}/${subscription.total_preorder_value_limit.toLocaleString()}
                      </p>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-green-600 h-2 rounded-full"
                          style={{ width: `${getUsagePercentage(subscription.current_preorder_value, subscription.total_preorder_value_limit)}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>

                  <div className="text-center">
                    <div className="flex items-center justify-center mb-2">
                      <Calendar className="h-5 w-5 text-gray-400" />
                    </div>
                    <p className="text-sm text-gray-500">Next Billing</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {subscription.next_billing_date
                        ? new Date(subscription.next_billing_date).toLocaleDateString()
                        : 'N/A'
                      }
                    </p>
                  </div>
                </div>

                <div className="flex flex-wrap gap-3">
                  <button
                    className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                  >
                    <Settings className="w-4 h-4 mr-2" />
                    Manage
                  </button>

                  {subscription.status === 'active' && (
                    <button
                      onClick={() => handlePauseSubscription(subscription.id)}
                      disabled={actionLoading === subscription.id}
                      className="inline-flex items-center px-4 py-2 border border-yellow-300 shadow-sm text-sm font-medium rounded-md text-yellow-700 bg-yellow-50 hover:bg-yellow-100 disabled:opacity-50"
                    >
                      <Pause className="w-4 h-4 mr-2" />
                      {actionLoading === subscription.id ? 'Pausing...' : 'Pause'}
                    </button>
                  )}

                  {subscription.status === 'paused' && (
                    <button
                      onClick={() => handleResumeSubscription(subscription.id)}
                      disabled={actionLoading === subscription.id}
                      className="inline-flex items-center px-4 py-2 border border-green-300 shadow-sm text-sm font-medium rounded-md text-green-700 bg-green-50 hover:bg-green-100 disabled:opacity-50"
                    >
                      <Play className="w-4 h-4 mr-2" />
                      {actionLoading === subscription.id ? 'Resuming...' : 'Resume'}
                    </button>
                  )}

                  {subscription.status !== 'cancelled' && (
                    <button
                      onClick={() => handleCancelSubscription(subscription.id)}
                      disabled={actionLoading === subscription.id}
                      className="inline-flex items-center px-4 py-2 border border-red-300 shadow-sm text-sm font-medium rounded-md text-red-700 bg-red-50 hover:bg-red-100 disabled:opacity-50"
                    >
                      <X className="w-4 h-4 mr-2" />
                      {actionLoading === subscription.id ? 'Cancelling...' : 'Cancel'}
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Subscriptions;