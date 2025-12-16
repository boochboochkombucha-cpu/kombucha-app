import React, { useState, useEffect } from 'react';
import { OrderTab } from './components/OrderTab';
import { StatusTab } from './components/StatusTab';
import { AdminTab } from './components/AdminTab';
import { Beer, ShoppingCart, Truck, Lock } from 'lucide-react';

type Tab = 'order' | 'status' | 'admin';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<Tab>('order');
  const [greeting, setGreeting] = useState('Good Morning');

  useEffect(() => {
    const hour = new Date().getHours();
    if (hour < 12) setGreeting("Good Morning, Let's Brew!");
    else if (hour < 18) setGreeting("Good Afternoon, Keep Flowing!");
    else setGreeting("Good Evening, Cheers!");
  }, []);

  return (
    <div className="min-h-screen bg-[#FAFAF5] text-[#4a4a4a] pb-24">
      {/* Header */}
      <div className="px-6 pt-8 pb-4 bg-white/50 backdrop-blur-md sticky top-0 z-10 border-b border-white">
        <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 bg-orange-100 rounded-full flex items-center justify-center">
                <Beer className="w-5 h-5 text-orange-600" />
            </div>
            <div>
                <h1 className="text-xl font-extrabold leading-tight text-stone-800">BoochBooch</h1>
                <p className="text-xs font-bold text-orange-500 uppercase tracking-widest">Wholesale Portal</p>
            </div>
        </div>
        <p className="text-stone-400 text-sm font-medium mt-2">{greeting}</p>
      </div>

      {/* Main Content Area */}
      <main className="px-4 pt-6 max-w-md mx-auto">
        {activeTab === 'order' && <OrderTab />}
        {activeTab === 'status' && <StatusTab />}
        {activeTab === 'admin' && <AdminTab />}
      </main>

      {/* Navigation Tabs (Fixed Bottom) */}
      <div className="fixed bottom-0 left-0 w-full bg-white/80 backdrop-blur-lg border-t border-stone-100 p-2 z-50">
        <div className="flex justify-between max-w-md mx-auto bg-stone-100/50 p-1 rounded-3xl gap-2">
          <button 
            onClick={() => setActiveTab('order')}
            className={`flex-1 py-3 rounded-2xl font-bold text-sm transition-all duration-300 flex items-center justify-center gap-2 ${activeTab === 'order' ? 'bg-[#FF4B4B] text-white shadow-md transform scale-105' : 'text-stone-500 hover:text-stone-800'}`}
          >
            <ShoppingCart size={18} />
            Order
          </button>
          <button 
            onClick={() => setActiveTab('status')}
            className={`flex-1 py-3 rounded-2xl font-bold text-sm transition-all duration-300 flex items-center justify-center gap-2 ${activeTab === 'status' ? 'bg-[#FF4B4B] text-white shadow-md transform scale-105' : 'text-stone-500 hover:text-stone-800'}`}
          >
            <Truck size={18} />
            Status
          </button>
          <button 
            onClick={() => setActiveTab('admin')}
            className={`flex-1 py-3 rounded-2xl font-bold text-sm transition-all duration-300 flex items-center justify-center gap-2 ${activeTab === 'admin' ? 'bg-[#FF4B4B] text-white shadow-md transform scale-105' : 'text-stone-500 hover:text-stone-800'}`}
          >
            <Lock size={18} />
            Admin
          </button>
        </div>
      </div>
    </div>
  );
};

export default App;