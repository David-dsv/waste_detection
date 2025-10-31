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
} from '@mui/icons-material';
import { uploadImage } from '../redux/detectionsSlice';

const ImageUpload = ({ onDetectionComplete }) => {
  const dispatch = useDispatch();
  const webcamRef = useRef(null);

  const [useWebcam, setUseWebcam] = useState(false);
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

  // Capturer depuis webcam
  const captureImage = useCallback(() => {
    const imageSrc = webcamRef.current.getScreenshot();
    if (imageSrc) {
      // Convertir base64 en File
      fetch(imageSrc)
        .then((res) => res.blob())
        .then((blob) => {
          const file = new File([blob], 'webcam.jpg', { type: 'image/jpeg' });
          setImage(file);
          setImagePreview(imageSrc);
          setIsWebcamImage(true);
          setResult(null);
          setError(null);
        });
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

  // Upload et détection
  const handleDetect = async () => {
    if (!image) {
      setError('Veuillez sélectionner une image');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('image', image);

      if (gpsLat) formData.append('gps_lat', gpsLat);
      if (gpsLon) formData.append('gps_lon', gpsLon);
      formData.append('source', 'web');
      formData.append('send_alert', sendAlert.toString());

      const response = await dispatch(uploadImage(formData)).unwrap();

      setResult(response);
      if (onDetectionComplete) {
        onDetectionComplete(response);
      }
    } catch (err) {
      setError(err.message || 'Erreur lors de la détection');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" gutterBottom>
          Détection de Déchets
        </Typography>

        {/* Toggle Webcam */}
        <Box sx={{ mb: 2 }}>
          <FormControlLabel
            control={
              <Switch
                checked={useWebcam}
                onChange={(e) => setUseWebcam(e.target.checked)}
              />
            }
            label="Utiliser la webcam"
          />
        </Box>

        <Grid container spacing={3}>
          <Grid item xs={12}>
            {useWebcam ? (
              <Box>
                {result && result.annotated_url ? (
                  // Afficher l'image annotée après détection
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
                    <Button
                      fullWidth
                      variant="outlined"
                      startIcon={<CameraIcon />}
                      onClick={() => setResult(null)}
                      sx={{ mt: 2 }}
                    >
                      Nouvelle capture
                    </Button>
                  </Box>
                ) : (
                  // Afficher la webcam
                  <Box>
                    <Typography variant="subtitle2" gutterBottom>
                      Webcam
                    </Typography>
                    <Webcam
                      ref={webcamRef}
                      screenshotFormat="image/jpeg"
                      width="100%"
                      videoConstraints={{ facingMode: 'user' }}
                      style={{ transform: 'scaleX(-1)', borderRadius: 8, maxWidth: 640, display: 'block', margin: '0 auto' }}
                    />
                    <Button
                      fullWidth
                      variant="contained"
                      startIcon={<CameraIcon />}
                      onClick={captureImage}
                      sx={{ mt: 1 }}
                    >
                      Capturer
                    </Button>
                  </Box>
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
                    <Button
                      fullWidth
                      variant="outlined"
                      onClick={() => {
                        setResult(null);
                        setImage(null);
                        setImagePreview(null);
                      }}
                      sx={{ mt: 2 }}
                    >
                      Nouvelle image
                    </Button>
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

        {/* Bouton Détection */}
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
