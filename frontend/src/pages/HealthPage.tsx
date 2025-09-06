import React, { useState, useEffect } from 'react';
import { Box, Typography, Paper, Button, Alert, CircularProgress, Chip } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { HealthAndSafety, SystemUpdate, Storage, Memory, MemoryOutlined } from '@mui/icons-material';
import axios from 'axios';

interface DatabaseStatus {
  status: string;
  error?: string;
}

interface SystemMetrics {
  cpu_percent: number;
  memory_percent: number;
  disk_percent: number;
}

interface HealthData {
  status: string;
  timestamp: string;
  version: string;
  environment: string;
  app_name: string;
  database: DatabaseStatus;
  system: SystemMetrics;
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
      
      const response = await axios.get('http://localhost:8000/api/v1/health/detailed');
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

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy':
      case 'connected':
        return 'success';
      case 'unhealthy':
      case 'disconnected':
        return 'error';
      default:
        return 'warning';
    }
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        System Health
      </Typography>

      <Paper sx={{ p: 3, mt: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <HealthAndSafety color="primary" sx={{ mr: 1 }} />
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

            <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 2, mb: 3 }}>
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

            {/* Database Status Section */}
            <Paper sx={{ p: 2, mb: 3, bgcolor: 'grey.50' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Storage color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">
                  Database Status
                </Typography>
                <Chip 
                  label={healthData.database.status.toUpperCase()}
                  color={getStatusColor(healthData.database.status)}
                  size="small"
                  sx={{ ml: 2 }}
                />
              </Box>

              {healthData.database.error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  Database Error: {healthData.database.error}
                </Alert>
              )}

              <Typography variant="body2" color="text.secondary">
                {healthData.database.status === 'connected' 
                  ? 'Database connection is active and responsive'
                  : 'Database connection is unavailable'
                }
              </Typography>
            </Paper>

            {/* System Metrics Section */}
            <Paper sx={{ p: 2, mb: 3, bgcolor: 'grey.50' }}>
              <Typography variant="h6" sx={{ mb: 2 }}>
                System Metrics
              </Typography>
              
              <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <MemoryOutlined color="action" />
                  <Box>
                    <Typography variant="subtitle2" color="text.secondary">
                      CPU Usage
                    </Typography>
                    <Typography variant="h6">
                      {healthData.system.cpu_percent.toFixed(1)}%
                    </Typography>
                  </Box>
                </Box>

                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Memory color="action" />
                  <Box>
                    <Typography variant="subtitle2" color="text.secondary">
                      Memory Usage
                    </Typography>
                    <Typography variant="h6">
                      {healthData.system.memory_percent.toFixed(1)}%
                    </Typography>
                  </Box>
                </Box>

                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Storage color="action" />
                  <Box>
                    <Typography variant="subtitle2" color="text.secondary">
                      Disk Usage
                    </Typography>
                    <Typography variant="h6">
                      {healthData.system.disk_percent.toFixed(1)}%
                    </Typography>
                  </Box>
                </Box>
              </Box>
            </Paper>
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
