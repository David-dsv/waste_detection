import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Alert, SEVERITY_COLORS } from '../types';
import { Check, Clock, AlertTriangle } from 'lucide-react';

const AlertsPage = () => {
    const [alerts, setAlerts] = useState<Alert[]>([]);
    const [filter, setFilter] = useState<'all' | 'pending' | 'resolved'>('all');

    const loadAlerts = async () => {
        try {
            const data = await api.getAlerts();
            setAlerts(data);
        } catch (e) {
            console.error(e);
        }
    };

    useEffect(() => {
        loadAlerts();
    }, []);

    const handleResolve = async (id: number) => {
        try {
            await api.resolveAlert(id);
            // Optimistic update or reload
            setAlerts(prev => prev.map(a => a.id === id ? { ...a, status: 'resolved' } : a));
        } catch (e) {
            console.error("Failed to resolve");
        }
    };

    const filteredAlerts = alerts.filter(a => filter === 'all' || a.status === filter);

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-2xl font-bold text-white">Alert Center</h2>
                    <p className="text-slate-400">Manage automated waste detection alerts</p>
                </div>
                <div className="flex bg-slate-900 rounded-lg p-1 border border-slate-800">
                    {['all', 'pending', 'resolved'].map(f => (
                        <button
                            key={f}
                            onClick={() => setFilter(f as any)}
                            className={`px-4 py-2 rounded-md text-sm capitalize transition-all ${filter === f ? 'bg-slate-700 text-white' : 'text-slate-400 hover:text-white'}`}
                        >
                            {f}
                        </button>
                    ))}
                </div>
            </div>

            <div className="grid gap-4">
                {filteredAlerts.length === 0 ? (
                    <div className="text-center py-20 bg-slate-900/50 rounded-2xl border border-slate-800 border-dashed">
                        <p className="text-slate-500">No alerts found matching your filter.</p>
                    </div>
                ) : (
                    filteredAlerts.map(alert => (
                        <div key={alert.id} className="bg-slate-900 border border-slate-800 rounded-xl p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 hover:border-slate-700 transition-all">
                            <div className="flex items-start gap-4">
                                <div className={`p-3 rounded-full ${alert.status === 'resolved' ? 'bg-slate-800 text-slate-500' : 'bg-red-500/10 text-red-500'}`}>
                                    {alert.status === 'resolved' ? <Check className="w-6 h-6" /> : <AlertTriangle className="w-6 h-6" />}
                                </div>
                                <div>
                                    <div className="flex items-center gap-3 mb-1">
                                        <h3 className="font-bold text-lg text-slate-200">Alert #{alert.id}</h3>
                                        <span className={`text-xs px-2 py-0.5 rounded border uppercase ${SEVERITY_COLORS[alert.severity]}`}>
                                            {alert.severity}
                                        </span>
                                        {alert.status === 'pending' && <span className="text-xs bg-red-500 text-white px-2 py-0.5 rounded animate-pulse">Live</span>}
                                    </div>
                                    <p className="text-slate-400 text-sm mb-1">{alert.message}</p>
                                    <div className="flex items-center gap-4 text-xs text-slate-500">
                                        <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {new Date(alert.created_at).toLocaleString()}</span>
                                        <span>•</span>
                                        <span>{alert.location}</span>
                                    </div>
                                </div>
                            </div>

                            {alert.status !== 'resolved' && (
                                <button 
                                    onClick={() => handleResolve(alert.id)}
                                    className="bg-slate-800 hover:bg-green-600 hover:text-white text-slate-300 px-4 py-2 rounded-lg text-sm font-medium transition-colors border border-slate-700 hover:border-green-500 flex items-center gap-2 whitespace-nowrap"
                                >
                                    <Check className="w-4 h-4" /> Mark Resolved
                                </button>
                            )}
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default AlertsPage;