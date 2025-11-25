import React, { useEffect, useState } from 'react';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  BarChart, Bar, PieChart, Pie, Cell, Legend
} from 'recharts';
import { Activity, Trash2, AlertTriangle, Crosshair } from 'lucide-react';
import { api } from '../services/api';
import { Statistics, ChartDataPoint, DailyStat } from '../types';

const COLORS = ['#22c55e', '#eab308', '#f97316', '#ef4444', '#3b82f6'];

const StatCard = ({ title, value, icon: Icon, subtext, color }: any) => (
  <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 flex items-start justify-between hover:border-slate-700 transition-colors">
    <div>
      <p className="text-slate-400 text-sm font-medium">{title}</p>
      <h3 className="text-3xl font-bold mt-2 text-white">{value}</h3>
      {subtext && <p className="text-xs text-slate-500 mt-1">{subtext}</p>}
    </div>
    <div className={`p-3 rounded-lg bg-opacity-10 ${color.replace('text-', 'bg-')}`}>
      <Icon className={`w-6 h-6 ${color}`} />
    </div>
  </div>
);

const Dashboard = () => {
  const [stats, setStats] = useState<Statistics | null>(null);
  const [dailyData, setDailyData] = useState<DailyStat[]>([]);
  const [classData, setClassData] = useState<ChartDataPoint[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [overview, daily, classes] = await Promise.all([
            api.getOverviewStats(),
            api.getDailyStats(),
            api.getStatsByClass()
        ]);
        setStats(overview);
        setDailyData(daily);
        setClassData(classes);
      } catch (error) {
        console.error("Failed to load dashboard data", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <div className="text-center p-20 text-slate-500 animate-pulse">Loading dashboard...</div>;

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold text-white">Overview</h2>
          <p className="text-slate-400">Real-time waste detection analytics</p>
        </div>
        <div className="flex gap-2">
            <span className="px-3 py-1 rounded-full bg-green-500/10 text-green-400 text-xs border border-green-500/20 flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                System Active
            </span>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard 
          title="Total Detections" 
          value={stats?.total_detections.toLocaleString()} 
          icon={Activity} 
          color="text-blue-500"
        />
        <StatCard 
          title="Objects Found" 
          value={stats?.total_objects.toLocaleString()} 
          icon={Trash2} 
          color="text-green-500"
          subtext="+12% from last week"
        />
        <StatCard 
          title="Active Alerts" 
          value={stats?.total_alerts} 
          icon={AlertTriangle} 
          color="text-orange-500"
          subtext="Requires attention"
        />
        <StatCard 
          title="Avg. Confidence" 
          value={`${(stats?.avg_confidence || 0 * 100).toFixed(1)}%`} 
          icon={Crosshair} 
          color="text-purple-500"
        />
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-6">Detection Trends (7 Days)</h3>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={dailyData}>
                <defs>
                  <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#22c55e" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                <XAxis dataKey="date" stroke="#94a3b8" axisLine={false} tickLine={false} />
                <YAxis stroke="#94a3b8" axisLine={false} tickLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#f1f5f9' }}
                  itemStyle={{ color: '#22c55e' }}
                />
                <Area type="monotone" dataKey="count" stroke="#22c55e" fillOpacity={1} fill="url(#colorCount)" strokeWidth={3} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-6">Waste Composition</h3>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={classData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {classData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                   contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
      
       {/* Top Classes Bar Chart */}
       <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-6">Top Waste Categories</h3>
          <div className="h-[250px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={classData} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} />
                <XAxis type="number" stroke="#94a3b8" />
                <YAxis dataKey="name" type="category" stroke="#94a3b8" width={100} />
                <Tooltip cursor={{fill: '#1e293b'}} contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155' }} />
                <Bar dataKey="value" fill="#3b82f6" radius={[0, 4, 4, 0]} barSize={20} />
              </BarChart>
            </ResponsiveContainer>
          </div>
       </div>

    </div>
  );
};

export default Dashboard;