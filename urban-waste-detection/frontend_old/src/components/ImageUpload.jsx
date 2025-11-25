/**
 * Composant Upload d'images avec webcam support.
 */

import React, { useState, useRef, useCallback } from 'react';
import { useDispatch } from 'react-redux';
import Webcam from 'react-webcam';
import { useDropzone } from 'react-dropzone';
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  Grid,
  CircularProgress,
  Alert,
  Switch,
  FormControlLabel,
  TextField,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  CameraAlt as CameraIcon,
  CheckCircle as CheckIcon,
  Map as MapIcon,
} from '@mui/icons-material';
import { uploadImage } from '../redux/detectionsSlice';

const ImageUpload = ({ onDetectionComplete }) => {
  const dispatch = useDispatch();
  const webcamRef = useRef(null);

  const [useWebcam, setUseWebcam] = useState(false);
  const [useRealtime, setUseRealtime] = useState(false);  // Mode temps réel
  const [image, setImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [isWebcamImage, setIsWebcamImage] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // GPS
  const [gpsLat, setGpsLat] = useState('');
  const [gpsLon, setGpsLon] = useState('');
  const [sendAlert, setSendAlert] = useState(false);

  // URL du stream temps réel
  const STREAM_URL = 'http://localhost:5001/api/stream';

  // Dropzone
  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      setImage(file);
      setImagePreview(URL.createObjectURL(file));
      setIsWebcamImage(false);
      setResult(null);
      setError(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpg', '.jpeg', '.png'],
    },
    multiple: false,
  });

  // Capturer depuis webcam et détecter automatiquement
  const captureImage = useCallback(async () => {
    const imageSrc = webcamRef.current.getScreenshot();
    if (imageSrc) {
      try {
        // Convertir base64 en File
        const res = await fetch(imageSrc);
        const blob = await res.blob();
        const file = new File([blob], 'webcam.jpg', { type: 'image/jpeg' });
        
        setImage(file);
        setImagePreview(imageSrc);
        setIsWebcamImage(true);
        setResult(null);
        setError(null);
        
        // Déclencher automatiquement la détection
        await handleDetectForFile(file);
      } catch (err) {
        setError('Erreur lors de la capture');
      }
    }
  }, [webcamRef]);

  // Obtenir localisation GPS
  const getLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setGpsLat(position.coords.latitude.toString());
          setGpsLon(position.coords.longitude.toString());
        },
        (error) => {
          console.error('Erreur GPS:', error);
        }
      );
    }
  };

  // Fonction de détection avec fichier en paramètre
  const handleDetectForFile = async (fileToDetect) => {
    if (!fileToDetect) {
      setError('Veuillez sélectionner une image');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('image', fileToDetect);

      if (gpsLat) formData.append('gps_lat', gpsLat);
      if (gpsLon) formData.append('gps_lon', gpsLon);
      formData.append('source', 'web');
      formData.append('send_alert', sendAlert.toString());

      const response = await dispatch(uploadImage(formData)).unwrap();

      setResult(response);
      // Ne pas appeler onDetectionComplete automatiquement
      // L'utilisateur doit voir le résultat d'abord
    } catch (err) {
      setError(err.message || 'Erreur lors de la détection');
    } finally {
      setLoading(false);
    }
  };

  // Upload et détection (utilise la fonction générique)
  const handleDetect = async () => {
    await handleDetectForFile(image);
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" gutterBottom>
          Détection de Déchets
        </Typography>

        {/* Toggle Webcam et Mode Temps Réel */}
        <Box sx={{ mb: 2, display: 'flex', gap: 3, flexWrap: 'wrap' }}>
          <FormControlLabel
            control={
              <Switch
                checked={useWebcam}
                onChange={(e) => {
                  setUseWebcam(e.target.checked);
                  if (!e.target.checked) setUseRealtime(false);
                }}
              />
            }
            label="Utiliser la webcam"
          />
          {useWebcam && (
            <FormControlLabel
              control={
                <Switch
                  checked={useRealtime}
                  onChange={(e) => setUseRealtime(e.target.checked)}
                  color="success"
                />
              }
              label="🔴 Détection TEMPS RÉEL"
            />
          )}
        </Box>

        <Grid container spacing={3}>
          <Grid item xs={12}>
            {useWebcam ? (
              <Box>
                {/* MODE TEMPS RÉEL */}
                {useRealtime ? (
                  <Box>
                    <Typography variant="subtitle2" gutterBottom sx={{ color: 'error.main', fontWeight: 'bold' }}>
                      🔴 DÉTECTION EN TEMPS RÉEL - Les déchets sont détectés automatiquement
                    </Typography>
                    <Box sx={{
                      position: 'relative',
                      border: '3px solid #f44336',
                      borderRadius: 2,
                      overflow: 'hidden'
                    }}>
                      <img
                        src={STREAM_URL}
                        alt="Flux vidéo temps réel avec détection"
                        style={{
                          width: '100%',
                          maxWidth: 800,
                          display: 'block',
                          margin: '0 auto'
                        }}
                      />
                    </Box>
                    <Alert severity="info" sx={{ mt: 2 }}>
                      <Typography variant="body2">
                        <strong>Classes détectées:</strong> Cigarette, Glass, Metal, Paper, Plastic, Other
                      </Typography>
                      <Typography variant="body2">
                        Les bounding boxes s'affichent automatiquement sur les déchets détectés.
                      </Typography>
                    </Alert>
                  </Box>
                ) : (
                  /* MODE CAPTURE MANUELLE */
                  <Grid container spacing={2}>
                    {/* Colonne Webcam */}
                    <Grid item xs={12} md={6}>
                      <Typography variant="subtitle2" gutterBottom>
                        Webcam en direct
                      </Typography>
                      <Box sx={{ position: 'relative' }}>
                        <Webcam
                          ref={webcamRef}
                          screenshotFormat="image/jpeg"
                          width="100%"
                          videoConstraints={{ facingMode: 'user' }}
                          style={{
                            transform: 'scaleX(-1)',
                            borderRadius: 8,
                            width: '100%',
                            display: 'block'
                          }}
                        />
                        {loading && (
                          <Box sx={{
                            position: 'absolute',
                            top: '50%',
                            left: '50%',
                            transform: 'translate(-50%, -50%)',
                            backgroundColor: 'rgba(0, 0, 0, 0.6)',
                            borderRadius: 2,
                            padding: 2
                          }}>
                            <CircularProgress color="primary" />
                          </Box>
                        )}
                      </Box>
                      <Button
                        fullWidth
                        variant="contained"
                        startIcon={<CameraIcon />}
                        onClick={captureImage}
                        disabled={loading}
                        sx={{ mt: 1 }}
                      >
                        {loading ? 'Détection en cours...' : 'Capturer & Détecter'}
                      </Button>
                    </Grid>

                    {/* Colonne Résultat */}
                    <Grid item xs={12} md={6}>
                      <Typography variant="subtitle2" gutterBottom>
                        {result ? (
                          <span style={{ color: '#4caf50' }}>
                            ✅ Résultat ({result.num_objects} objet{result.num_objects > 1 ? 's' : ''})
                          </span>
                        ) : (
                          'Résultat de la détection'
                        )}
                      </Typography>
                      <Box sx={{
                        minHeight: { xs: 240, md: 320 },
                        border: result ? '3px solid #4caf50' : '2px dashed #ccc',
                        borderRadius: 2,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        backgroundColor: result ? 'transparent' : '#f5f5f5',
                        overflow: 'hidden'
                      }}>
                        {result && result.annotated_url ? (
                          <img
                            src={`http://localhost:5001${result.annotated_url}`}
                            alt="Détection annotée"
                            style={{
                              width: '100%',
                              height: '100%',
                              objectFit: 'contain',
                              borderRadius: 6
                            }}
                          />
                        ) : (
                          <Typography color="text.secondary">
                            {loading ? 'Analyse en cours...' : 'En attente de capture'}
                          </Typography>
                        )}
                      </Box>
                      {result && (
                        <Box sx={{ mt: 1 }}>
                          <Box sx={{ p: 1, bgcolor: 'grey.100', borderRadius: 1 }}>
                            <Typography variant="body2">
                              Confiance: {(result.confidence_avg * 100).toFixed(1)}%
                            </Typography>
                            <Typography variant="body2">
                              Temps: {result.processing_time.toFixed(2)}s
                            </Typography>
                          </Box>
                          <Button
                            fullWidth
                            variant="contained"
                            color="success"
                            startIcon={<MapIcon />}
                            onClick={() => onDetectionComplete && onDetectionComplete(result)}
                            sx={{ mt: 1 }}
                          >
                            Voir sur la carte
                          </Button>
                        </Box>
                      )}
                    </Grid>
                  </Grid>
                )}
              </Box>
            ) : (
              // Mode upload de fichier
              <Box>
                {result && result.annotated_url ? (
                  // Afficher l'image annotée
                  <Box>
                    <Typography variant="subtitle2" gutterBottom color="success.main">
                      ✅ Résultat de la détection ({result.num_objects} objet(s))
                    </Typography>
                    <img
                      src={`http://localhost:5001${result.annotated_url}`}
                      alt="Détection annotée"
                      style={{
                        width: '100%',
                        maxWidth: 640,
                        borderRadius: 8,
                        border: '3px solid #4caf50',
                        display: 'block',
                        margin: '0 auto'
                      }}
                    />
                    <Grid container spacing={2} sx={{ mt: 1 }}>
                      <Grid item xs={12} sm={6}>
                        <Button
                          fullWidth
                          variant="contained"
                          color="success"
                          startIcon={<MapIcon />}
                          onClick={() => onDetectionComplete && onDetectionComplete(result)}
                        >
                          Voir sur la carte
                        </Button>
                      </Grid>
                      <Grid item xs={12} sm={6}>
                        <Button
                          fullWidth
                          variant="outlined"
                          onClick={() => {
                            setResult(null);
                            setImage(null);
                            setImagePreview(null);
                          }}
                        >
                          Nouvelle image
                        </Button>
                      </Grid>
                    </Grid>
                  </Box>
                ) : imagePreview ? (
                  // Prévisualisation avant détection
                  <Box>
                    <Typography variant="subtitle2" gutterBottom>
                      Prévisualisation
                    </Typography>
                    <img
                      src={imagePreview}
                      alt="Preview"
                      style={{
                        width: '100%',
                        maxWidth: 640,
                        borderRadius: 8,
                        display: 'block',
                        margin: '0 auto'
                      }}
                    />
                  </Box>
                ) : (
                  // Zone de drop
                  <Box
                    {...getRootProps()}
                    sx={{
                      border: '2px dashed',
                      borderColor: isDragActive ? 'primary.main' : 'grey.400',
                      borderRadius: 2,
                      p: 4,
                      textAlign: 'center',
                      cursor: 'pointer',
                      bgcolor: isDragActive ? 'action.hover' : 'transparent',
                    }}
                  >
                    <input {...getInputProps()} />
                    <UploadIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                    <Typography>
                      {isDragActive
                        ? 'Déposez l\'image ici'
                        : 'Glissez une image ou cliquez pour sélectionner'}
                    </Typography>
                  </Box>
                )}
              </Box>
            )}
          </Grid>
        </Grid>

        {/* Options GPS et Alerte */}
        <Box sx={{ mt: 3 }}>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="Latitude GPS"
                value={gpsLat}
                onChange={(e) => setGpsLat(e.target.value)}
                size="small"
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="Longitude GPS"
                value={gpsLon}
                onChange={(e) => setGpsLon(e.target.value)}
                size="small"
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <Button fullWidth variant="outlined" onClick={getLocation}>
                Obtenir ma position
              </Button>
            </Grid>
          </Grid>

          <FormControlLabel
            control={
              <Switch
                checked={sendAlert}
                onChange={(e) => setSendAlert(e.target.checked)}
              />
            }
            label="Envoyer alerte automatique"
            sx={{ mt: 2 }}
          />
        </Box>

        {/* Bouton Détection - Uniquement pour le mode upload de fichier */}
        {!useWebcam && (
          <Button
            fullWidth
            variant="contained"
            size="large"
            onClick={handleDetect}
            disabled={!image || loading}
            sx={{ mt: 3 }}
          >
            
            {loading ? <CircularProgress size={24} /> : 'Détecter les déchets'}
          </Button>
        )}

        {/* Erreur */}
        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}

        {/* Résultat */}
        {result && (
          <Alert
            severity="success"
            icon={<CheckIcon />}
            sx={{ mt: 2 }}
          >
            <Typography variant="h6">
              {result.num_objects} objet(s) détecté(s)
            </Typography>
            <Typography variant="body2">
              Confiance moyenne: {(result.confidence_avg * 100).toFixed(1)}%
            </Typography>
            <Typography variant="body2">
              Temps de traitement: {result.processing_time.toFixed(2)}s
            </Typography>
            {result.alert_sent && (
              <Typography variant="body2" color="warning.main">
                ⚠️ Alerte envoyée aux autorités
              </Typography>
            )}
          </Alert>
        )}
      </CardContent>
    </Card>
  );
};

export default ImageUpload;