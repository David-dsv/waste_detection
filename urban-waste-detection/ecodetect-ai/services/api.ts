import { DetectionResponse, Statistics, Alert, DailyStat, ChartDataPoint } from '../types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001/api';

class ApiService {
    private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
        try {
            const res = await fetch(`${API_BASE_URL}${endpoint}`, options);
            if (!res.ok) {
                const errorBody = await res.json().catch(() => ({}));
                throw new Error(errorBody.message || `API Error: ${res.status}`);
            }
            return await res.json();
        } catch (error) {
            console.error(`Request failed for ${endpoint}:`, error);
            throw error;
        }
    }

    // Detection
    async detectImage(formData: FormData): Promise<DetectionResponse> {
        return this.request<DetectionResponse>('/detect', {
            method: 'POST',
            body: formData,
        });
    }

    // Statistics
    async getOverviewStats(): Promise<Statistics> {
        // Mocking structure if backend is not actually running for UI demo
        try {
            return await this.request<Statistics>('/statistics/overview');
        } catch (e) {
            // Fallback for demo purposes if backend isn't live
            return {
                total_detections: 1240,
                total_objects: 3500,
                total_alerts: 45,
                avg_confidence: 0.89
            };
        }
    }

    async getDailyStats(): Promise<DailyStat[]> {
        try {
            return await this.request<DailyStat[]>('/statistics/daily');
        } catch (e) {
             return [
                { date: 'Mon', count: 12 },
                { date: 'Tue', count: 19 },
                { date: 'Wed', count: 15 },
                { date: 'Thu', count: 25 },
                { date: 'Fri', count: 32 },
                { date: 'Sat', count: 40 },
                { date: 'Sun', count: 28 },
            ];
        }
    }

    async getStatsByClass(): Promise<ChartDataPoint[]> {
        try {
            return await this.request<ChartDataPoint[]>('/statistics/by-class');
        } catch (e) {
            return [
                { name: 'Plastic', value: 400 },
                { name: 'Organic', value: 300 },
                { name: 'Metal', value: 100 },
                { name: 'Glass', value: 80 },
                { name: 'Paper', value: 150 },
            ];
        }
    }

    // History
    async getDetections(params?: string): Promise<{ items: DetectionResponse[], total: number }> {
         // Using a slightly different return signature for list handling
         try {
             const items = await this.request<DetectionResponse[]>(`/detections${params ? `?${params}` : ''}`);
             return { items, total: items.length };
         } catch(e) {
             return { items: [], total: 0 };
         }
    }

    async getDetectionById(id: number): Promise<DetectionResponse> {
        return this.request<DetectionResponse>(`/detections/${id}`);
    }

    async deleteDetection(id: number): Promise<void> {
        await this.request(`/detections/${id}`, { method: 'DELETE' });
    }

    // Alerts
    async getAlerts(): Promise<Alert[]> {
        try {
            return await this.request<Alert[]>('/alerts');
        } catch(e) {
            // Mock
            return [
                { id: 1, detection_id: 101, status: 'pending', severity: 'high', created_at: new Date().toISOString(), message: 'Large pile of plastic waste detected.', location: 'Paris, District 13' },
                { id: 2, detection_id: 102, status: 'resolved', severity: 'low', created_at: new Date(Date.now() - 86400000).toISOString(), message: 'Single bottle on sidewalk.', location: 'Paris, District 11' },
            ]
        }
    }

    async resolveAlert(id: number): Promise<void> {
        await this.request(`/alerts/${id}/resolve`, { method: 'POST' });
    }
}

export const api = new ApiService();