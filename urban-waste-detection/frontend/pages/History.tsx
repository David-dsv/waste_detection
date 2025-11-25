import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { DetectionResponse } from '../types';
import { Search, Filter, Trash2, Eye } from 'lucide-react';

const HistoryPage = () => {
    const [items, setItems] = useState<DetectionResponse[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const load = async () => {
            try {
                const { items } = await api.getDetections('limit=20');
                setItems(items);
            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        };
        load();
    }, []);

    const handleDelete = async (id: number) => {
        if(confirm("Are you sure you want to delete this record?")) {
            await api.deleteDetection(id);
            setItems(prev => prev.filter(i => i.detection_id !== id));
        }
    }

    return (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
            <div className="p-6 border-b border-slate-800 flex flex-col md:flex-row justify-between items-center gap-4">
                <h2 className="text-xl font-bold text-white">Detection History</h2>
                <div className="flex gap-2 w-full md:w-auto">
                    <div className="relative flex-1 md:w-64">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                        <input 
                            type="text" 
                            placeholder="Search detections..." 
                            className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-10 pr-4 py-2 text-sm text-slate-200 focus:outline-none focus:border-green-500"
                        />
                    </div>
                    <button className="bg-slate-800 p-2 rounded-lg text-slate-400 hover:text-white border border-slate-800 hover:border-slate-600">
                        <Filter className="w-5 h-5" />
                    </button>
                </div>
            </div>

            <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                    <thead className="bg-slate-950 text-slate-400 uppercase text-xs font-bold">
                        <tr>
                            <th className="px-6 py-4">ID</th>
                            <th className="px-6 py-4">Date</th>
                            <th className="px-6 py-4">Severity</th>
                            <th className="px-6 py-4">Objects</th>
                            <th className="px-6 py-4">Confidence</th>
                            <th className="px-6 py-4 text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800">
                        {loading ? (
                            <tr><td colSpan={6} className="text-center py-10 text-slate-500">Loading records...</td></tr>
                        ) : items.length === 0 ? (
                            <tr><td colSpan={6} className="text-center py-10 text-slate-500">No history found.</td></tr>
                        ) : (
                            items.map((item) => (
                                <tr key={item.detection_id} className="hover:bg-slate-800/50 transition-colors group">
                                    <td className="px-6 py-4 font-mono text-slate-500">#{item.detection_id}</td>
                                    <td className="px-6 py-4 text-slate-300">
                                        {new Date(item.timestamp || Date.now()).toLocaleDateString()}
                                        <span className="block text-xs text-slate-500">{new Date(item.timestamp || Date.now()).toLocaleTimeString()}</span>
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className={`inline-block w-2 h-2 rounded-full mr-2 ${
                                            item.ai_analysis.severity === 'critical' ? 'bg-red-500' :
                                            item.ai_analysis.severity === 'high' ? 'bg-orange-500' :
                                            item.ai_analysis.severity === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                                        }`} />
                                        <span className="capitalize">{item.ai_analysis.severity}</span>
                                    </td>
                                    <td className="px-6 py-4 text-slate-300">{item.num_objects}</td>
                                    <td className="px-6 py-4">
                                        <div className="flex items-center gap-2">
                                            <div className="w-16 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                                                <div className="h-full bg-green-500" style={{ width: `${item.confidence_avg * 100}%` }} />
                                            </div>
                                            <span className="text-xs">{(item.confidence_avg * 100).toFixed(0)}%</span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-right">
                                        <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                            <button className="p-1.5 rounded-md hover:bg-blue-500/20 text-blue-400"><Eye className="w-4 h-4" /></button>
                                            <button onClick={() => handleDelete(item.detection_id)} className="p-1.5 rounded-md hover:bg-red-500/20 text-red-400"><Trash2 className="w-4 h-4" /></button>
                                        </div>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
            
            {/* Pagination Mock */}
            <div className="p-4 border-t border-slate-800 flex justify-between items-center text-xs text-slate-500">
                <span>Showing {items.length} records</span>
                <div className="flex gap-2">
                    <button disabled className="px-3 py-1 rounded bg-slate-800 opacity-50 cursor-not-allowed">Previous</button>
                    <button className="px-3 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300">Next</button>
                </div>
            </div>
        </div>
    );
};

export default HistoryPage;