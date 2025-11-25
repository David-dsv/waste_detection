import React, { useState, useRef, useEffect } from 'react';
import { Camera, Upload, AlertTriangle, CheckCircle2, ShieldAlert, Loader2, MapPin, Send, RefreshCw, Video } from 'lucide-react';
import { api } from '../services/api';
import { DetectionResponse, SEVERITY_COLORS } from '../types';

const Detection = () => {
  const [mode, setMode] = useState<'upload' | 'camera'>('camera');
  const [isRealTime, setIsRealTime] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<DetectionResponse | null>(null);
  const [sendAlert, setSendAlert] = useState(false);
  const [location, setLocation] = useState<{lat: number, lon: number} | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  // Geolocation initialization
  useEffect(() => {
    getLocation();
  }, []);

  // Camera initialization
  useEffect(() => {
    if (mode === 'camera' && !isRealTime) {
      startCamera();
    } else {
      stopCamera();
    }
    return () => {
      stopCamera();
    };
  }, [mode, isRealTime]);

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
  };

  const getLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLocation({
            lat: position.coords.latitude,
            lon: position.coords.longitude
          });
        },
        (error) => console.error("Geo error:", error)
      );
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) {
      setFile(selected);
      setPreviewUrl(URL.createObjectURL(selected));
      setResult(null);
    }
  };

  const startCamera = async () => {
    setResult(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (err) {
      console.error("Camera error:", err);
      // Fallback to upload if camera fails
      // Only switch if we are strictly in client camera mode and not trying to do something else
      if (mode === 'camera' && !isRealTime) {
         alert("Cannot access camera. Switching to upload mode.");
         setMode('upload');
      }
    }
  };

  const captureImage = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext('2d');
      ctx?.drawImage(video, 0, 0);
      
      canvas.toBlob((blob) => {
        if (blob) {
          const capturedFile = new File([blob], "capture.jpg", { type: "image/jpeg" });
          setFile(capturedFile);
          setPreviewUrl(URL.createObjectURL(capturedFile));
          stopCamera(); 
        }
      }, 'image/jpeg');
    }
  };

  const resetCapture = () => {
    setFile(null);
    setPreviewUrl(null);
    setResult(null);
    if (mode === 'camera' && !isRealTime) {
      startCamera();
    }
  };

  const handleSubmit = async () => {
    if (!file) return;

    setIsProcessing(true);
    const formData = new FormData();
    formData.append('image', file);
    formData.append('source', mode === 'camera' ? 'webcam' : 'upload');
    if (location) {
        formData.append('gps_lat', location.lat.toString());
        formData.append('gps_lon', location.lon.toString());
    }
    if (sendAlert) {
        formData.append('send_alert', 'true');
    }

    try {
      const response = await api.detectImage(formData);
      setResult(response);
    } catch (error) {
      alert("Detection failed. Is the backend running?");
    } finally {
      setIsProcessing(false);
    }
  };

  const API_BASE = 'http://localhost:5001';
  const streamUrl = `${API_BASE}/api/stream`;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 h-[calc(100vh-8rem)]">
      
      {/* Left Column: Input */}
      <div className="flex flex-col gap-6">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex-1 flex flex-col">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold flex items-center gap-2 text-white">
              <Camera className="w-5 h-5 text-green-500" /> Live Scanner
            </h2>
            <div className="flex bg-slate-800 rounded-lg p-1">
              <button
                onClick={() => { 
                    setMode('camera'); 
                    resetCapture(); 
                }}
                className={`px-4 py-1.5 rounded-md text-sm transition-all ${mode === 'camera' ? 'bg-slate-700 text-white shadow' : 'text-slate-400 hover:text-white'}`}
              >
                Webcam
              </button>
              <button
                onClick={() => { 
                    setMode('upload'); 
                    setIsRealTime(false);
                    stopCamera(); 
                }}
                className={`px-4 py-1.5 rounded-md text-sm transition-all ${mode === 'upload' ? 'bg-slate-700 text-white shadow' : 'text-slate-400 hover:text-white'}`}
              >
                Upload
              </button>
            </div>
          </div>

          <div className="flex-1 bg-slate-950 rounded-xl border-2 border-dashed border-slate-800 relative overflow-hidden flex items-center justify-center group">
            {mode === 'camera' ? (
                isRealTime ? (
                    // Server-side MJPEG Stream
                    <div className="relative w-full h-full bg-black flex items-center justify-center">
                        <img 
                            src={streamUrl} 
                            alt="Real-time Detection Stream" 
                            className="w-full h-full object-contain"
                        />
                        <div className="absolute top-4 left-4 bg-red-600 text-white px-3 py-1 rounded-full animate-pulse font-bold text-sm shadow-lg z-10 flex items-center gap-2">
                             <div className="w-2 h-2 bg-white rounded-full" /> LIVE ANALYSIS
                        </div>
                    </div>
                ) : !previewUrl ? (
                    // Client-side Camera
                    <>
                        {/* Mirrored view for user comfort */}
                        <video ref={videoRef} autoPlay playsInline muted className="w-full h-full object-cover scale-x-[-1]" />
                        <canvas ref={canvasRef} className="hidden" />
                        <button 
                        onClick={captureImage}
                        className="absolute bottom-6 left-1/2 -translate-x-1/2 bg-white/20 backdrop-blur-sm border-4 border-white/50 rounded-full p-1 hover:scale-110 transition-transform cursor-pointer"
                        title="Capture Frame"
                        >
                        <div className="w-12 h-12 bg-red-500 rounded-full border-2 border-slate-900"></div>
                        </button>
                        <div className="absolute top-4 left-4 bg-green-500/80 text-white text-xs px-2 py-1 rounded flex items-center gap-2">
                            <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div> CAMERA READY
                        </div>
                    </>
                ) : (
                    // Preview of captured image
                    <div className="relative w-full h-full">
                        <img src={previewUrl} alt="Preview" className="w-full h-full object-contain" />
                        <button 
                            onClick={resetCapture}
                            className="absolute top-4 right-4 bg-slate-900/80 text-white p-2 rounded-full hover:bg-slate-800 transition-colors"
                            title="Retake"
                        >
                            <RefreshCw className="w-5 h-5" />
                        </button>
                    </div>
                )
            ) : (
              // Upload Mode
              previewUrl ? (
                <div className="relative w-full h-full">
                    <img src={previewUrl} alt="Preview" className="w-full h-full object-contain" />
                    <button 
                        onClick={resetCapture}
                        className="absolute top-4 right-4 bg-slate-900/80 text-white p-2 rounded-full hover:bg-slate-800 transition-colors"
                        title="Clear"
                    >
                        <RefreshCw className="w-5 h-5" />
                    </button>
                </div>
              ) : (
                <div 
                  className="text-center cursor-pointer p-10 w-full h-full flex flex-col items-center justify-center hover:bg-slate-900/50 transition-colors"
                  onClick={() => fileInputRef.current?.click()}
                >
                  <Upload className="w-16 h-16 text-slate-700 mb-4 group-hover:text-green-500 transition-colors" />
                  <p className="text-slate-400 font-medium text-lg">Drop image or click to upload</p>
                  <p className="text-slate-600 text-sm mt-2">Supports JPG, PNG</p>
                </div>
              )
            )}
            <input type="file" ref={fileInputRef} onChange={handleFileChange} className="hidden" accept="image/*" />
          </div>

          <div className="mt-6 flex flex-col gap-4">
             {/* Controls */}
             <div className="flex items-center justify-between bg-slate-800/50 p-4 rounded-xl border border-slate-800 flex-wrap gap-4">
                
                {mode === 'camera' && (
                     <button
                        onClick={() => setIsRealTime(!isRealTime)}
                        className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-xl font-bold transition-all shadow-lg ${
                            isRealTime 
                            ? 'bg-red-600 hover:bg-red-700 text-white shadow-red-900/20' 
                            : 'bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700'
                        }`}
                    >
                        <Video className="w-5 h-5" />
                        {isRealTime ? 'STOP REAL-TIME' : '🔴 Détection TEMPS RÉEL'}
                    </button>
                )}

                {!isRealTime && (
                    <div className="flex items-center gap-3 bg-slate-900 px-3 py-2 rounded-lg border border-slate-700">
                        <label className="flex items-center gap-2 cursor-pointer select-none">
                            <span className="text-sm text-slate-300">Auto-Alert</span>
                            <div 
                                className={`w-10 h-5 rounded-full p-0.5 transition-colors duration-200 ease-in-out ${sendAlert ? 'bg-green-600' : 'bg-slate-700'}`} 
                                onClick={() => setSendAlert(!sendAlert)}
                            >
                                <div className={`bg-white w-4 h-4 rounded-full shadow-md transform transition-transform duration-200 ${sendAlert ? 'translate-x-5' : 'translate-x-0'}`} />
                            </div>
                        </label>
                    </div>
                )}
             </div>

             {!isRealTime && (
                 <button 
                    onClick={handleSubmit} 
                    disabled={!file || isProcessing}
                    className="w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white font-bold py-4 px-6 rounded-xl shadow-lg shadow-green-900/20 transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none"
                 >
                    {isProcessing ? <Loader2 className="animate-spin w-5 h-5" /> : <Send className="w-5 h-5" />}
                    {isProcessing ? 'Analyzing Waste...' : 'Analyze Capture'}
                 </button>
             )}
          </div>
        </div>
      </div>

      {/* Right Column: Results */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl overflow-y-auto">
         {isRealTime ? (
             <div className="h-full flex flex-col items-center justify-center text-slate-500 animate-pulse">
                 <Video className="w-16 h-16 mb-4 text-red-500" />
                 <h3 className="text-xl font-bold text-white mb-2">Real-Time Analysis Active</h3>
                 <p className="text-center max-w-sm">
                     The system is processing the video stream in real-time. 
                     Detections and bounding boxes are displayed directly on the video feed.
                 </p>
                 <div className="mt-8 p-4 bg-slate-950 rounded-lg border border-slate-800 w-full max-w-xs">
                     <div className="flex justify-between text-sm mb-2">
                         <span className="text-slate-400">Status</span>
                         <span className="text-green-400 font-mono">RUNNING</span>
                     </div>
                     <div className="flex justify-between text-sm">
                         <span className="text-slate-400">Mode</span>
                         <span className="text-blue-400 font-mono">MJPEG STREAM</span>
                     </div>
                 </div>
             </div>
         ) : !result ? (
             <div className="h-full flex flex-col items-center justify-center text-slate-600 opacity-60">
                 <ShieldAlert className="w-20 h-20 mb-6 text-slate-700" />
                 <h3 className="text-lg font-medium text-slate-500 mb-2">Ready for Analysis</h3>
                 <p className="text-sm text-slate-600 text-center max-w-xs">Capture an image from the webcam or upload a file to detect waste and receive AI recommendations.</p>
             </div>
         ) : (
             <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                 
                 {/* Header Stats */}
                 <div className="grid grid-cols-2 gap-4">
                     <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                         <p className="text-slate-500 text-xs uppercase font-bold tracking-wider">Objects Detected</p>
                         <p className="text-3xl font-bold text-white mt-1">{result.num_objects}</p>
                     </div>
                     <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                         <p className="text-slate-500 text-xs uppercase font-bold tracking-wider">Avg Confidence</p>
                         <p className="text-3xl font-bold text-green-400 mt-1">{(result.confidence_avg * 100).toFixed(1)}%</p>
                     </div>
                 </div>

                 {/* AI Summary Card */}
                 <div className={`p-5 rounded-xl border ${SEVERITY_COLORS[result.ai_analysis.severity]} bg-opacity-10`}>
                    <div className="flex justify-between items-start mb-3">
                        <h3 className="font-bold text-lg flex items-center gap-2">
                           <AlertTriangle className="w-5 h-5" /> 
                           Assessment: <span className="uppercase tracking-wide">{result.ai_analysis.severity}</span>
                        </h3>
                        <span className="text-xs font-mono px-2 py-1 rounded bg-black/20">Score: {result.ai_analysis.urgency_score}/10</span>
                    </div>
                    <p className="text-sm opacity-90 leading-relaxed">{result.ai_analysis.summary}</p>
                 </div>

                 {/* Annotated Image */}
                 {result.annotated_url && (
                     <div className="rounded-xl overflow-hidden border border-slate-800 shadow-2xl relative group">
                         <img src={`${API_BASE}${result.annotated_url}`} alt="Annotated Result" className="w-full" />
                         <div className="absolute bottom-2 right-2 bg-black/70 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity">
                            Processed in {result.processing_time.toFixed(3)}s
                         </div>
                     </div>
                 )}

                 {/* Recommendations */}
                 <div>
                    <h4 className="text-slate-300 font-bold mb-4 flex items-center gap-2 text-sm uppercase tracking-wider">
                        <CheckCircle2 className="w-4 h-4 text-green-500" /> Action Plan
                    </h4>
                    <div className="space-y-3">
                        {result.ai_analysis.recommendations.map((rec, idx) => (
                            <div key={idx} className="bg-slate-950 p-4 rounded-lg border border-slate-800 text-sm flex items-start gap-4 hover:border-slate-700 transition-colors">
                                <div className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${rec.priority === 'high' || rec.priority === 'critical' ? 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.6)]' : 'bg-blue-500'}`} />
                                <div>
                                    <p className="text-slate-200 font-medium text-base">{rec.action}</p>
                                    <p className="text-slate-500 text-xs mt-1">{rec.reason}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                 </div>

                 {/* Object List */}
                 <div>
                    <h4 className="text-slate-300 font-bold mb-3 text-sm uppercase tracking-wider">Detected Items</h4>
                    <div className="flex flex-wrap gap-2">
                        {result.detections.map((det, idx) => (
                            <span key={idx} className="bg-slate-800 text-slate-300 px-3 py-1.5 rounded-lg text-xs border border-slate-700 flex items-center gap-2">
                                <span className="font-medium text-white capitalize">{det.class}</span>
                                <span className="text-slate-500 border-l border-slate-600 pl-2">{(det.confidence * 100).toFixed(0)}%</span>
                            </span>
                        ))}
                    </div>
                 </div>

             </div>
         )}
      </div>
    </div>
  );
};

export default Detection;