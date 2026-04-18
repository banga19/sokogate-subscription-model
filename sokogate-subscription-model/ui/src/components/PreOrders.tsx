import React, { useState, useEffect } from 'react';
import axios from 'axios';

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
}

const PreOrders: React.FC = () => {
  const [preOrders, setPreOrders] = useState<PreOrder[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedSubscription, setSelectedSubscription] = useState<number | null>(null);
  const [selectedProduct, setSelectedProduct] = useState<number | null>(null);
  const [quantity, setQuantity] = useState(1);
  const [priorityLevel, setPriorityLevel] = useState(1);

  const [subscriptions, setSubscriptions] = useState<any[]>([]);

  useEffect(() => {
    fetchSubscriptionsAndPreOrders();
    fetchProducts();
  }, []);

  const fetchSubscriptionsAndPreOrders = async () => {
    try {
      // Get user's subscriptions first
      const subsResponse = await axios.get('/api/v1/subscriptions/customer/1');
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
    } catch (err) {
      setError('Failed to fetch pre-orders');
    }
    setLoading(false);
  };

  const fetchProducts = async () => {
    try {
      // Assuming there's a products endpoint
      const response = await axios.get('/api/v1/products');
      setProducts(response.data);
      setLoading(false);
    } catch (err) {
      // If no products endpoint, use mock data
      setProducts([
        { id: 1, name: 'Product A', description: 'Description A', price: 100 },
        { id: 2, name: 'Product B', description: 'Description B', price: 200 },
        { id: 3, name: 'Product C', description: 'Description C', price: 300 },
      ]);
      setLoading(false);
    }
  };

  const handleCreatePreOrder = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedSubscription || !selectedProduct) return;

    try {
      const response = await axios.post(`/api/v1/subscriptions/${selectedSubscription}/pre-orders`, {
        product_id: selectedProduct,
        quantity,
        priority_level: priorityLevel,
      });
      setPreOrders([...preOrders, response.data]);
      setShowCreateForm(false);
      setSelectedSubscription(null);
      setSelectedProduct(null);
      setQuantity(1);
      setPriorityLevel(1);
    } catch (err) {
      setError('Failed to create pre-order');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'confirmed':
        return 'bg-blue-100 text-blue-800';
      case 'shipped':
        return 'bg-green-100 text-green-800';
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
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Pre-Orders</h2>
          <p className="mt-2 text-gray-600">Manage your pre-orders and early access items</p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition duration-200"
        >
          Create Pre-Order
        </button>
      </div>

      {showCreateForm && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h3 className="text-xl font-semibold mb-4">Create New Pre-Order</h3>
          <form onSubmit={handleCreatePreOrder}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Subscription</label>
                <select
                  value={selectedSubscription || ''}
                  onChange={(e) => setSelectedSubscription(Number(e.target.value))}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  required
                >
                  <option value="">Select a subscription</option>
                  {subscriptions.map((sub) => (
                    <option key={sub.id} value={sub.id}>
                      {sub.subscription_plan.name} ({sub.subscription_plan.tier})
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Product</label>
                <select
                  value={selectedProduct || ''}
                  onChange={(e) => setSelectedProduct(Number(e.target.value))}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  required
                >
                  <option value="">Select a product</option>
                  {products.map((product) => (
                    <option key={product.id} value={product.id}>
                      {product.name} - ${product.price}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Quantity</label>
                <input
                  type="number"
                  min="1"
                  value={quantity}
                  onChange={(e) => setQuantity(Number(e.target.value))}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Priority Level</label>
                <select
                  value={priorityLevel}
                  onChange={(e) => setPriorityLevel(Number(e.target.value))}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value={1}>1 - Low</option>
                  <option value={2}>2</option>
                  <option value={3}>3 - Medium</option>
                  <option value={4}>4</option>
                  <option value={5}>5 - High</option>
                </select>
              </div>
            </div>
            <div className="flex space-x-4">
              <button
                type="submit"
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition duration-200"
              >
                Create Pre-Order
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowCreateForm(false);
                  setSelectedSubscription(null);
                  setSelectedProduct(null);
                  setQuantity(1);
                  setPriorityLevel(1);
                }}
                className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700 transition duration-200"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {preOrders.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500">No pre-orders found. Create your first pre-order to get started.</p>
        </div>
      ) : (
        <div className="space-y-6">
          {preOrders.map((preOrder) => (
            <div key={preOrder.id} className="bg-white rounded-lg shadow-md p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-semibold text-gray-900">
                    Pre-Order #{preOrder.id}
                  </h3>
                  <p className="text-gray-600">Product ID: {preOrder.product_id}</p>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(preOrder.status)}`}>
                  {preOrder.status}
                </span>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div>
                  <p className="text-sm text-gray-500">Quantity</p>
                  <p className="font-semibold">{preOrder.quantity}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Unit Price</p>
                  <p className="font-semibold">${preOrder.unit_price}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Discount</p>
                  <p className="font-semibold">${preOrder.discount_applied}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Total</p>
                  <p className="font-semibold">${preOrder.total_amount}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4">
                <div>
                  <p className="text-sm text-gray-500">Priority Level</p>
                  <p className="font-semibold">{preOrder.priority_level}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Payment Status</p>
                  <p className="font-semibold">{preOrder.payment_status}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Created</p>
                  <p className="font-semibold">{new Date(preOrder.created_at).toLocaleDateString()}</p>
                </div>
              </div>

              {preOrder.expected_availability_date && (
                <div className="mb-4">
                  <p className="text-sm text-gray-500">Expected Availability</p>
                  <p className="font-semibold">{new Date(preOrder.expected_availability_date).toLocaleDateString()}</p>
                </div>
              )}

              <div className="flex space-x-4">
                <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition duration-200">
                  View Details
                </button>
                {preOrder.status === 'pending' && (
                  <button className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition duration-200">
                    Cancel
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default PreOrders;