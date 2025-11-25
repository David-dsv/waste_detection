export interface BBox {
    x1: number;
    y1: number;
    x2: number;
    y2: number;
}

export interface DetectedObject {
    class: string;
    category: string;
    confidence: number;
    bbox: number[]; // [x1, y1, x2, y2]
}

export interface Recommendation {
    action: string;
    priority: 'low' | 'medium' | 'high' | 'critical';
    reason: string;
}

export interface AIAnalysis {
    summary: string;
    severity: 'low' | 'medium' | 'high' | 'critical';
    severity_score: number;
    environmental_risks: string[];
    health_risks: string[];
    recommendations: Recommendation[];
    urgency_score: number;
}

export interface DetectionResponse {
    success: boolean;
    detection_id: number;
    detections: DetectedObject[];
    num_objects: number;
    confidence_avg: number;
    processing_time: number;
    annotated_url: string;
    alert_sent: boolean;
    ai_analysis: AIAnalysis;
    source?: string;
    timestamp?: string; // added for frontend display
    gps_lat?: number;
    gps_lon?: number;
}

export interface Alert {
    id: number;
    detection_id: number;
    status: 'pending' | 'sent' | 'resolved';
    severity: 'low' | 'medium' | 'high' | 'critical';
    created_at: string;
    message: string;
    location: string;
}

export interface Statistics {
    total_detections: number;
    total_objects: number;
    total_alerts: number;
    avg_confidence: number;
}

export interface ChartDataPoint {
    name: string;
    value: number;
}

export interface DailyStat {
    date: string;
    count: number;
}

export const SEVERITY_COLORS = {
    low: 'bg-green-500/20 text-green-400 border-green-500/50',
    medium: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50',
    high: 'bg-orange-500/20 text-orange-400 border-orange-500/50',
    critical: 'bg-red-500/20 text-red-400 border-red-500/50',
};