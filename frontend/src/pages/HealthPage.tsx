import React, { useState, useEffect } from 'react';
import { Box, Typography, Paper, Button, Alert, CircularProgress } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { HealthCheck, SystemUpdate } from '@mui/icons-material';
import axios from 'axios';

interface HealthData {
  status: string;
  timestamp: string;
  version: string;
  environment: string;
}

const HealthPage: React.FC = () => {
  const navigate = useNavigate();
  const [healthData, setHealthData] = useState<HealthData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchHealthData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.get('http://localhost:8000/api/v1/health');
      setHealthData(response.data);
    } catch (err) {
      setError('Failed to connect to backend API. Make sure the backend is running.');
      console.error('Health check failed:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealthData();
  }, []);

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        System Health
      </Typography>

      <Paper sx={{ p: 3, mt: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <HealthCheck color="primary" sx={{ mr: 1 }} />
          <Typography variant="h6">
            Backend API Status
          </Typography>
        </Box>

        {loading && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <CircularProgress size={20} />
            <Typography>Checking backend connection...</Typography>
          </Box>
        )}

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {healthData && (
          <Box>
            <Alert 
              severity={healthData.status === 'healthy' ? 'success' : 'error'}
              sx={{ mb: 2 }}
            >
              Status: {healthData.status.toUpperCase()}
            </Alert>

            <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 2 }}>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">
                  Version
                </Typography>
                <Typography variant="body1">
                  {healthData.version}
                </Typography>
              </Box>

              <Box>
                <Typography variant="subtitle2" color="text.secondary">
                  Environment
                </Typography>
                <Typography variant="body1">
                  {healthData.environment}
                </Typography>
              </Box>

              <Box>
                <Typography variant="subtitle2" color="text.secondary">
                  Last Checked
                </Typography>
                <Typography variant="body1">
                  {new Date(healthData.timestamp).toLocaleString()}
                </Typography>
              </Box>
            </Box>
          </Box>
        )}

        <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            startIcon={<SystemUpdate />}
            onClick={fetchHealthData}
            disabled={loading}
          >
            Refresh
          </Button>
          
          <Button
            variant="outlined"
            onClick={() => navigate('/')}
          >
            Back to Home
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};

export default HealthPage;
