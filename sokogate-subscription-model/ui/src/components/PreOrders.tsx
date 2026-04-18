import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import {
  Plus,
  Package,
  DollarSign,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  ShoppingCart,
  Star,
  Truck
} from 'lucide-react';

interface PreOrder {
  id: number;
  subscription_id: number;
  customer_id: number;
  product_id: number;
  quantity: number;
  unit_price: number;
  discount_applied: number;
  total_amount: number;
  status: string;
  expected_availability_date?: string;
  pre_order_deadline?: string;
  priority_level: number;
  estimated_delivery_date?: string;
  payment_status: string;
  created_at: string;
}

interface Product {
  id: number;
  name: string;
  description?: string;
  price: number;
  category?: string;
  stock_status?: string;
}

interface Subscription {
  id: number;
  subscription_plan: {
    name: string;
    tier: string;
  };
  status: string;
}

const PreOrders: React.FC = () => {
  const { user } = useAuth();
  const [preOrders, setPreOrders] = useState<PreOrder[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedSubscription, setSelectedSubscription] = useState<number | null>(null);
  const [selectedProduct, setSelectedProduct] = useState<number | null>(null);
  const [quantity, setQuantity] = useState(1);
  const [priorityLevel, setPriorityLevel] = useState(1);
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    if (user) {
      fetchData();
    } else {
      setLoading(false);
    }
  }, [user]);

  const fetchData = async () => {
    if (!user) return;

    try {
      setLoading(true);

      // Get user's subscriptions
      const subsResponse = await axios.get(`/api/v1/subscriptions/customer/${user.id}`);
      setSubscriptions(subsResponse.data);

      // Get pre-orders for all subscriptions
      const allPreOrders: PreOrder[] = [];
      for (const sub of subsResponse.data) {
        try {
          const preOrdersResponse = await axios.get(`/api/v1/subscriptions/${sub.id}/pre-orders`);
          allPreOrders.push(...preOrdersResponse.data);
        } catch (err) {
          // Ignore errors for individual subscriptions
        }
      }
      setPreOrders(allPreOrders);

      // Get products
      try {
        const productsResponse = await axios.get('/api/v1/products');
        setProducts(productsResponse.data);
      } catch (err) {
        // Use mock data if endpoint doesn't exist
        setProducts([
          { id: 1, name: 'Cement - Premium Grade', description: 'High-quality Portland cement', price: 25.99, category: 'Building Materials', stock_status: 'Pre-order' },
          { id: 2, name: 'Steel Rebars - 12mm', description: 'Corrosion-resistant steel reinforcement', price: 45.50, category: 'Reinforcement', stock_status: 'Pre-order' },
          { id: 3, name: 'Sand - Construction Grade', description: 'Clean, washed construction sand', price: 18.75, category: 'Aggregates', stock_status: 'Available' },
          { id: 4, name: 'Bricks - Red Clay', description: 'Standard red clay bricks', price: 0.85, category: 'Masonry', stock_status: 'Pre-order' },
        ]);
      }
    } catch (err) {
      setError('Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePreOrder = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedSubscription || !selectedProduct || !user) return;

    setCreating(true);
    try {
      const response = await axios.post(`/api/v1/subscriptions/${selectedSubscription}/pre-orders`, {
        product_id: selectedProduct,
        quantity,
        priority_level: priorityLevel,
      });
      setPreOrders([...preOrders, response.data]);
      setShowCreateForm(false);
      resetForm();
    } catch (err) {
      setError('Failed to create pre-order');
    } finally {
      setCreating(false);
    }
  };

  const resetForm = () => {
    setSelectedSubscription(null);
    setSelectedProduct(null);
    setQuantity(1);
    setPriorityLevel(1);
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'confirmed':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'shipped':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'delivered':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'cancelled':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'pending':
        return <Clock className="w-4 h-4" />;
      case 'confirmed':
        return <CheckCircle className="w-4 h-4" />;
      case 'shipped':
        return <Truck className="w-4 h-4" />;
      case 'delivered':
        return <CheckCircle className="w-4 h-4" />;
      case 'cancelled':
        return <XCircle className="w-4 h-4" />;
      default:
        return <AlertCircle className="w-4 h-4" />;
    }
  };

  const getPriorityStars = (level: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`w-4 h-4 ${i < level ? 'text-yellow-400 fill-current' : 'text-gray-300'}`}
      />
    ));
  };

  if (!user) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">Authentication Required</h3>
        <p className="mt-1 text-sm text-gray-500">Please login to view your pre-orders.</p>
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
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Pre-Orders</h2>
          <p className="mt-2 text-gray-600">Manage your pre-orders and early access to construction materials</p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
        >
          <Plus className="w-4 h-4 mr-2" />
          Create Pre-Order
        </button>
      </div>

      {showCreateForm && (
        <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-6 mb-8">
          <h3 className="text-xl font-semibold text-gray-900 mb-6">Create New Pre-Order</h3>
          <form onSubmit={handleCreatePreOrder} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Subscription
                </label>
                <select
                  value={selectedSubscription || ''}
                  onChange={(e) => setSelectedSubscription(Number(e.target.value))}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                >
                  <option value="">Choose a subscription</option>
                  {subscriptions
                    .filter(sub => sub.status === 'active')
                    .map((sub) => (
                    <option key={sub.id} value={sub.id}>
                      {sub.subscription_plan.name} ({sub.subscription_plan.tier})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Product
                </label>
                <select
                  value={selectedProduct || ''}
                  onChange={(e) => setSelectedProduct(Number(e.target.value))}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                >
                  <option value="">Choose a product</option>
                  {products.map((product) => (
                    <option key={product.id} value={product.id}>
                      {product.name} - ${product.price.toFixed(2)}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Quantity
                </label>
                <input
                  type="number"
                  min="1"
                  value={quantity}
                  onChange={(e) => setQuantity(Number(e.target.value))}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Priority Level
                </label>
                <select
                  value={priorityLevel}
                  onChange={(e) => setPriorityLevel(Number(e.target.value))}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value={1}>1 - Low Priority</option>
                  <option value={2}>2</option>
                  <option value={3}>3 - Medium Priority</option>
                  <option value={4}>4</option>
                  <option value={5}>5 - High Priority</option>
                </select>
              </div>
            </div>

            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => {
                  setShowCreateForm(false);
                  resetForm();
                }}
                className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={creating}
                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {creating ? 'Creating...' : 'Create Pre-Order'}
              </button>
            </div>
          </form>
        </div>
      )}

      {preOrders.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <ShoppingCart className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No pre-orders found</h3>
          <p className="mt-1 text-sm text-gray-500">
            Create your first pre-order to get early access to construction materials.
          </p>
          <div className="mt-6">
            <button
              onClick={() => setShowCreateForm(true)}
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
            >
              <Plus className="w-4 h-4 mr-2" />
              Create Pre-Order
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          {preOrders.map((preOrder) => (
            <div key={preOrder.id} className="bg-white rounded-lg shadow-lg border border-gray-200 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200">
                <div className="flex justify-between items-start">
                  <div className="flex items-center space-x-3">
                    <div className="flex-shrink-0">
                      <Package className="h-8 w-8 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="text-xl font-semibold text-gray-900">
                        Pre-Order #{preOrder.id}
                      </h3>
                      <p className="text-gray-600">Product ID: {preOrder.product_id}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(preOrder.status)}
                    <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getStatusColor(preOrder.status)}`}>
                      {preOrder.status.charAt(0).toUpperCase() + preOrder.status.slice(1)}
                    </span>
                  </div>
                </div>
              </div>

              <div className="px-6 py-4">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
                  <div className="text-center">
                    <div className="flex items-center justify-center mb-2">
                      <Package className="h-5 w-5 text-gray-400" />
                    </div>
                    <p className="text-sm text-gray-500">Quantity</p>
                    <p className="text-lg font-semibold text-gray-900">{preOrder.quantity}</p>
                  </div>

                  <div className="text-center">
                    <div className="flex items-center justify-center mb-2">
                      <DollarSign className="h-5 w-5 text-gray-400" />
                    </div>
                    <p className="text-sm text-gray-500">Unit Price</p>
                    <p className="text-lg font-semibold text-gray-900">${preOrder.unit_price.toFixed(2)}</p>
                  </div>

                  <div className="text-center">
                    <div className="flex items-center justify-center mb-2">
                      <Star className="h-5 w-5 text-gray-400" />
                    </div>
                    <p className="text-sm text-gray-500">Priority</p>
                    <div className="flex justify-center">
                      {getPriorityStars(preOrder.priority_level)}
                    </div>
                  </div>

                  <div className="text-center">
                    <div className="flex items-center justify-center mb-2">
                      <DollarSign className="h-5 w-5 text-gray-400" />
                    </div>
                    <p className="text-sm text-gray-500">Total</p>
                    <p className="text-lg font-semibold text-gray-900">${preOrder.total_amount.toFixed(2)}</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  <div>
                    <p className="text-sm text-gray-500">Payment Status</p>
                    <p className="font-semibold text-gray-900">{preOrder.payment_status}</p>
                  </div>

                  <div>
                    <p className="text-sm text-gray-500">Created</p>
                    <p className="font-semibold text-gray-900">
                      {new Date(preOrder.created_at).toLocaleDateString()}
                    </p>
                  </div>

                  {preOrder.expected_availability_date && (
                    <div>
                      <p className="text-sm text-gray-500">Expected Availability</p>
                      <p className="font-semibold text-gray-900">
                        {new Date(preOrder.expected_availability_date).toLocaleDateString()}
                      </p>
                    </div>
                  )}
                </div>

                {preOrder.discount_applied > 0 && (
                  <div className="bg-green-50 border border-green-200 rounded-md p-3 mb-4">
                    <p className="text-sm text-green-800">
                      <strong>Discount Applied:</strong> ${preOrder.discount_applied.toFixed(2)}
                    </p>
                  </div>
                )}

                <div className="flex flex-wrap gap-3">
                  <button className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
                    View Details
                  </button>

                  {preOrder.status === 'pending' && (
                    <button className="inline-flex items-center px-4 py-2 border border-red-300 shadow-sm text-sm font-medium rounded-md text-red-700 bg-red-50 hover:bg-red-100">
                      <XCircle className="w-4 h-4 mr-2" />
                      Cancel
                    </button>
                  )}

                  {preOrder.status === 'confirmed' && (
                    <button className="inline-flex items-center px-4 py-2 border border-blue-300 shadow-sm text-sm font-medium rounded-md text-blue-700 bg-blue-50 hover:bg-blue-100">
                      <Truck className="w-4 h-4 mr-2" />
                      Track Delivery
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

export default PreOrders;