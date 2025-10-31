/**
 * Carte interactive avec Leaflet pour visualiser les détections.
 */

import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import { Box, Card, CardContent, Typography, Chip } from '@mui/material';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix des icônes Leaflet avec React
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

// Icônes customisées par sévérité
const createCustomIcon = (severity) => {
  const colors = {
    critical: '#d32f2f',
    high: '#f57c00',
    medium: '#fbc02d',
    low: '#388e3c',
  };

  const color = colors[severity] || colors.low;

  return L.divIcon({
    className: 'custom-marker',
    html: `<div style="background-color: ${color}; width: 30px; height: 30px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 5px rgba(0,0,0,0.3);"></div>`,
    iconSize: [30, 30],
    iconAnchor: [15, 15],
  });
};

const WasteMap = ({ detections = [] }) => {
  const [center, setCenter] = useState([
    parseFloat(process.env.REACT_APP_MAP_CENTER_LAT) || 48.8566,
    parseFloat(process.env.REACT_APP_MAP_CENTER_LON) || 2.3522,
  ]);
  const [zoom] = useState(parseInt(process.env.REACT_APP_MAP_ZOOM) || 12);

  // Filtrer détections avec localisation
  const locatedDetections = detections.filter(
    (det) => det.location && det.location.latitude && det.location.longitude
  );

  // Centrer sur la première détection si disponible
  useEffect(() => {
    if (locatedDetections.length > 0) {
      const firstDet = locatedDetections[0];
      setCenter([firstDet.location.latitude, firstDet.location.longitude]);
    }
  }, [locatedDetections]);

  const getSeverity = (numObjects) => {
    if (numObjects > 20) return 'critical';
    if (numObjects > 10) return 'high';
    if (numObjects > 5) return 'medium';
    return 'low';
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" gutterBottom>
          Carte des Détections
        </Typography>

        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          {locatedDetections.length} détection(s) géolocalisée(s)
        </Typography>

        <Box sx={{ height: 500, borderRadius: 2, overflow: 'hidden' }}>
          <MapContainer
            center={center}
            zoom={zoom}
            style={{ height: '100%', width: '100%' }}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            {locatedDetections.map((detection, idx) => {
              const severity = getSeverity(detection.num_objects);

              return (
                <Marker
                  key={idx}
                  position={[
                    detection.location.latitude,
                    detection.location.longitude,
                  ]}
                  icon={createCustomIcon(severity)}
                >
                  <Popup>
                    <Box sx={{ minWidth: 200 }}>
                      <Typography variant="subtitle1" fontWeight="bold">
                        Détection #{detection.id}
                      </Typography>

                      <Chip
                        label={severity.toUpperCase()}
                        color={
                          severity === 'critical'
                            ? 'error'
                            : severity === 'high'
                            ? 'warning'
                            : 'success'
                        }
                        size="small"
                        sx={{ my: 1 }}
                      />

                      <Typography variant="body2">
                        Objets: {detection.num_objects}
                      </Typography>

                      <Typography variant="body2">
                        Confiance: {(detection.confidence_avg * 100).toFixed(1)}%
                      </Typography>

                      <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                        {new Date(detection.detected_at).toLocaleString()}
                      </Typography>

                      {detection.objects_detected && Array.isArray(detection.objects_detected) && (
                        <Box sx={{ mt: 1 }}>
                          <Typography variant="caption" fontWeight="bold">
                            Types détectés:
                          </Typography>
                          {Object.entries(
                            detection.objects_detected.reduce((acc, obj) => {
                              const className = obj.class || obj.class_name || 'unknown';
                              acc[className] = (acc[className] || 0) + 1;
                              return acc;
                            }, {})
                          ).map(([className, count]) => (
                            <Typography key={className} variant="caption" display="block">
                              - {className}: {count}
                            </Typography>
                          ))}
                        </Box>
                      )}
                    </Box>
                  </Popup>
                </Marker>
              );
            })}
          </MapContainer>
        </Box>

        {/* Légende */}
        <Box sx={{ mt: 2, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box
              sx={{
                width: 16,
                height: 16,
                borderRadius: '50%',
                bgcolor: '#388e3c',
              }}
            />
            <Typography variant="caption">Faible (1-5)</Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box
              sx={{
                width: 16,
                height: 16,
                borderRadius: '50%',
                bgcolor: '#fbc02d',
              }}
            />
            <Typography variant="caption">Moyen (6-10)</Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box
              sx={{
                width: 16,
                height: 16,
                borderRadius: '50%',
                bgcolor: '#f57c00',
              }}
            />
            <Typography variant="caption">Élevé (11-20)</Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box
              sx={{
                width: 16,
                height: 16,
                borderRadius: '50%',
                bgcolor: '#d32f2f',
              }}
            />
            <Typography variant="caption">Critique (&gt;20)</Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default WasteMap;
