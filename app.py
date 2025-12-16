import React, { useState, useEffect, useMemo } from 'react';
import { Button } from './ui/Button';
import { Input, Select } from './ui/Input';
import { StorageService } from '../services/storage';
import { Order, OrderStatus } from '../types';
import { Lock, TrendingUp, DollarSign, Settings } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const COLORS = ['#FDBA74', '#FB923C', '#F97316', '#EA580C'];

export const AdminTab: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [password, setPassword] = useState('');
  const [orders, setOrders] = useState<Order[]>([]);
  const [editingId, setEditingId] = useState<string | null>(null);
  
  const [editStatus, setEditStatus] = useState<OrderStatus>('Pending');
  const [editDate, setEditDate] = useState('');

  const DEMO_PASS = 'admin123';

  useEffect(() => {
    if (isAuthenticated) {
      setOrders(StorageService.getOrders());
    }
  }, [isAuthenticated]);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (password === DEMO_PASS) {
      setIsAuthenticated(true);
    } else {
      alert('Incorrect password (hint: admin123)');
    }
  };

  const productionData = useMemo(() => {
    const pending = orders.filter(o => o.status !== 'Completed');
    const counts: Record<string, number> = {};
    pending.forEach(o => {
      counts[o.flavor] = (counts[o.flavor] || 0) + o.quantity;
    });
    return Object.keys(counts).map(key => ({
      name: key,
      quantity: counts[key]
    }));
  }, [orders]);

  const revenueEstimate = useMemo(() => {
    const pendingUnits = orders
      .filter(o => o.status !== 'Completed')
      .reduce((sum, o) => sum + o.quantity, 0);
    return pendingUnits * 50; 
  }, [orders]);

  const startEdit = (order: Order) => {
    setEditingId(order.id);
    setEditStatus(order.status);
    setEditDate(order.arrivalDate);
  };

  const saveEdit = () => {
    if (editingId) {
      StorageService.updateOrder(editingId, {
        status: editStatus,
        arrivalDate: editDate
      });
      setOrders(StorageService.getOrders());
      setEditingId(null);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="flex flex-col items-center justify-center py-10 animate-in fade-in duration-500">
        <div className="bg-white p-4 rounded-full shadow-md mb-6">
          <Lock className="w-8 h-8 text-stone-400" />
        </div>
        <h2 className="text-xl font-bold text-stone-700 mb-6">Admin Access</h2>
        <form onSubmit={handleLogin} className="w-full max-w-xs">
          <Input 
            type="password" 
            placeholder="Password" 
            value={password}
            onChange={e => setPassword(e.target.value)}
            className="text-center"
          />
          <Button type="submit">Unlock Dashboard</Button>
        </form>
      </div>
    );
  }

  return (
    <div className="animate-in slide-in-from-bottom-4 duration-500 space-y-6">
      
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white p-5 rounded-3xl shadow-sm border border-stone-100 flex flex-col justify-between">
            <div className="flex items-center gap-2 text-stone-500 mb-2">
                <TrendingUp className="w-4 h-4" />
                <span className="text-xs font-bold uppercase tracking-wider">Pending Units</span>
            </div>
            <span className="text-3xl font-extrabold text-stone-800">
                {orders.filter(o => o.status !== 'Completed').reduce((sum, o) => sum + o.quantity, 0)}
            </span>
        </div>
        <div className="bg-white p-5 rounded-3xl shadow-sm border border-stone-100 flex flex-col justify-between">
            <div className="flex items-center gap-2 text-stone-500 mb-2">
                <DollarSign className="w-4 h-4" />
                <span className="text-xs font-bold uppercase tracking-wider">Est. Revenue</span>
            </div>
            <span className="text-3xl font-extrabold text-stone-800">
                ${revenueEstimate.toLocaleString()}
            </span>
        </div>
      </div>

      <div className="bg-white p-6 rounded-3xl shadow-sm border border-stone-100">
        <h3 className="font-bold text-stone-700 mb-4">Production Plan (Pending)</h3>
        {productionData.length > 0 ? (
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={productionData}>
                <XAxis dataKey="name" tick={{fill: '#78716c', fontSize: 12}} axisLine={false} tickLine={false} />
                <YAxis hide />
                <Tooltip 
                    cursor={{fill: '#f5f5f4'}}
                    contentStyle={{borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'}}
                />
                <Bar dataKey="quantity" radius={[8, 8, 8, 8]}>
                    {productionData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        ) : (
            <div className="text-center py-10 text-stone-400">All caught up! No pending orders.</div>
        )}
      </div>

      <div className="bg-white p-6 rounded-3xl shadow-sm border border-stone-100">
        <h3 className="font-bold text-stone-700 mb-4 flex items-center gap-2">
            <Settings className="w-5 h-5 text-stone-400" />
            Manage Orders
        </h3>
        <div className="space-y-4 max-h-96 overflow-y-auto pr-2">
          {orders.map(order => (
            <div key={order.id} className="p-4 border border-stone-100 rounded-2xl bg-stone-50">
              {editingId === order.id ? (
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="font-bold text-stone-800">{order.clientName}</span>
                    <button onClick={() => setEditingId(null)} className="text-xs text-stone-400 hover:text-stone-600">Cancel</button>
                  </div>
                  <Select 
                    options={['Pending', 'In Production', 'Completed']} 
                    value={editStatus}
                    onChange={e => setEditStatus(e.target.value as OrderStatus)}
                    className="text-sm py-2"
                  />
                  <Input 
                    value={editDate}
                    onChange={e => setEditDate(e.target.value)}
                    placeholder="YYYY-MM-DD"
                    className="text-sm py-2"
                  />
                  <Button onClick={saveEdit} className="h-10 text-sm">Save Changes</Button>
                </div>
              ) : (
                <div className="flex justify-between items-center">
                  <div>
                    <div className="font-bold text-stone-700">{order.clientName}</div>
                    <div className="text-xs text-stone-500">{order.flavor} ({order.quantity})</div>
                    <div className="text-xs text-orange-500 font-semibold mt-1">{order.status}</div>
                  </div>
                  <button 
                    onClick={() => startEdit(order)}
                    className="px-4 py-2 bg-white rounded-xl text-sm font-bold text-stone-600 shadow-sm border border-stone-200 hover:bg-stone-50"
                  >
                    Edit
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};