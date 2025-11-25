/**
 * Application principale React.
 */

import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Container,
  Box,
  AppBar,
  Toolbar,
  Typography,
  Tabs,
  Tab,
  CssBaseline,
  ThemeProvider,
  createTheme,
} from '@mui/material';
import { Delete as WasteIcon } from '@mui/icons-material';

import ImageUpload from './components/ImageUpload';
import WasteMap from './components/WasteMap';
import Dashboard from './components/Dashboard';
import { fetchDetections } from './redux/detectionsSlice';

const theme = createTheme({
  palette: {
    primary: {
      main: '#2e7d32',
    },
    secondary: {
      main: '#ff6f00',
    },
  },
});

function TabPanel({ children, value, index }) {
  return (
    <div hidden={value !== index} style={{ paddingTop: 24 }}>
      {value === index && children}
    </div>
  );
}

function App() {
  const dispatch = useDispatch();
  const { list: detections } = useSelector((state) => state.detections);
  const [tabValue, setTabValue] = React.useState(0);

  useEffect(() => {
    dispatch(fetchDetections({ limit: 100 }));
  }, [dispatch]);

  const handleDetectionComplete = (result) => {
    // Rafraîchir la liste
    dispatch(fetchDetections({ limit: 100 }));
    // Basculer sur l'onglet carte
    setTabValue(1);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static">
          <Toolbar>
            <WasteIcon sx={{ mr: 2, fontSize: 32 }} />
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Urban Waste Detection System
            </Typography>
            <Typography variant="caption">
              Propulsé par RF-DETR + IA
            </Typography>
          </Toolbar>
        </AppBar>

        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
          <Tabs
            value={tabValue}
            onChange={(e, newValue) => setTabValue(newValue)}
            sx={{ mb: 3 }}
            variant="fullWidth"
          >
            <Tab label="Détection" />
            <Tab label="Carte" />
            <Tab label="Dashboard" />
          </Tabs>

          <TabPanel value={tabValue} index={0}>
            <ImageUpload onDetectionComplete={handleDetectionComplete} />
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            <WasteMap detections={detections} />
          </TabPanel>

          <TabPanel value={tabValue} index={2}>
            <Dashboard />
          </TabPanel>
        </Container>

        <Box
          component="footer"
          sx={{
            py: 3,
            px: 2,
            mt: 'auto',
            bgcolor: 'background.paper',
            textAlign: 'center',
          }}
        >
          <Typography variant="body2" color="text.secondary">
            © 2025 Urban Waste Detection - R&D Project
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Open Source (Apache 2.0) | Villes Propres + Durables
          </Typography>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;
