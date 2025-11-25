import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import { api } from '../services/api';
import { DetectionResponse } from '../types';

// Fix Leaflet Default Icon issue in Webpack/React
// @ts-ignore
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Custom Icons for severity
const createIcon = (color: string) => new L.DivIcon({
  className: 'custom-icon',
  html: `<div style="background-color: ${color}; width: 14px; height: 14px; border-radius: 50%; border: 2px solid white; box-shadow: 0 0 10px ${color};"></div>`,
  iconSize: [14, 14],
  iconAnchor: [7, 7]
});

const icons = {
    low: createIcon('#22c55e'),    // green
    medium: createIcon('#eab308'), // yellow
    high: createIcon('#f97316'),   // orange
    critical: createIcon('#ef4444') // red
};

const MapController = ({ center }: { center: [number, number] }) => {
    const map = useMap();
    useEffect(() => {
        map.flyTo(center, 13);
    }, [center, map]);
    return null;
};

const MapPage = () => {
    const [detections, setDetections] = useState<DetectionResponse[]>([]);
    const [center] = useState<[number, number]>([48.8566, 2.3522]); // Paris

    useEffect(() => {
        // Fetch detections with coords
        const loadMapData = async () => {
            try {
                // In a real app, you'd ask the backend for "all detections with geolocation"
                // Here we fetch list and filter or mock if empty
                const { items } = await api.getDetections('limit=50');
                
                // If API returns empty (no backend), lets add some mocks around Paris for demo
                if (items.length === 0) {
                    const mocks: any[] = [];
                    for(let i=0; i<10; i++) {
                        mocks.push({
                            detection_id: i,
                            gps_lat: 48.8566 + (Math.random() - 0.5) * 0.05,
                            gps_lon: 2.3522 + (Math.random() - 0.5) * 0.05,
                            ai_analysis: { 
                                severity: ['low', 'medium', 'high', 'critical'][Math.floor(Math.random()*4)],
                                summary: "Mock detection for visualization" 
                            },
                            num_objects: Math.floor(Math.random() * 20),
                            timestamp: new Date().toISOString()
                        });
                    }
                    setDetections(mocks);
                } else {
                    setDetections(items.filter(d => d.gps_lat && d.gps_lon));
                }
            } catch (e) {
                console.error(e);
            }
        };
        loadMapData();
    }, []);

    return (
        <div className="h-[calc(100vh-8rem)] rounded-2xl overflow-hidden border border-slate-800 relative z-0">
             <MapContainer center={center} zoom={13} scrollWheelZoom={true} style={{ height: '100%', width: '100%' }}>
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                />
                <MapController center={center} />
                
                {detections.map((d) => (
                    <Marker 
                        key={d.detection_id} 
                        position={[d.gps_lat || 0, d.gps_lon || 0]}
                        icon={icons[d.ai_analysis.severity] || icons.low}
                    >
                        <Popup className="custom-popup">
                            <div className="p-2">
                                <h3 className="font-bold text-sm">Detection #{d.detection_id}</h3>
                                <p className="text-xs text-gray-500 mb-2">{new Date(d.timestamp || Date.now()).toLocaleDateString()}</p>
                                <span className={`text-xs px-2 py-0.5 rounded text-white ${
                                    d.ai_analysis.severity === 'critical' ? 'bg-red-500' :
                                    d.ai_analysis.severity === 'high' ? 'bg-orange-500' :
                                    d.ai_analysis.severity === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                                } uppercase`}>
                                    {d.ai_analysis.severity}
                                </span>
                                <p className="text-xs mt-2"><b>{d.num_objects}</b> objects detected</p>
                            </div>
                        </Popup>
                    </Marker>
                ))}
             </MapContainer>

             {/* Legend Overlay */}
             <div className="absolute bottom-6 left-6 bg-slate-900/90 backdrop-blur border border-slate-700 p-4 rounded-xl z-[400]">
                 <h4 className="text-xs font-bold text-slate-400 uppercase mb-3">Severity Levels</h4>
                 <div className="space-y-2">
                     <div className="flex items-center gap-2">
                         <div className="w-3 h-3 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]"></div>
                         <span className="text-xs text-slate-200">Low (1-5 objects)</span>
                     </div>
                     <div className="flex items-center gap-2">
                         <div className="w-3 h-3 rounded-full bg-yellow-500 shadow-[0_0_8px_rgba(234,179,8,0.6)]"></div>
                         <span className="text-xs text-slate-200">Medium (6-10 objects)</span>
                     </div>
                     <div className="flex items-center gap-2">
                         <div className="w-3 h-3 rounded-full bg-orange-500 shadow-[0_0_8px_rgba(249,115,22,0.6)]"></div>
                         <span className="text-xs text-slate-200">High (11-20 objects)</span>
                     </div>
                     <div className="flex items-center gap-2">
                         <div className="w-3 h-3 rounded-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.6)]"></div>
                         <span className="text-xs text-slate-200">Critical ({`>20`} objects)</span>
                     </div>
                 </div>
             </div>
        </div>
    );
};

export default MapPage;