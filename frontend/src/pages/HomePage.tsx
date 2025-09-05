import React from 'react';
import { Box, Typography, Paper, Button, Grid } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { AccountBalance, Assessment, Security } from '@mui/icons-material';

const HomePage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <Box>
      <Typography variant="h3" component="h1" gutterBottom align="center">
        Welcome to TheTally
      </Typography>
      
      <Typography variant="h6" component="p" gutterBottom align="center" color="text.secondary">
        Your personal financial tracking application
      </Typography>

      <Grid container spacing={3} sx={{ mt: 4 }}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <AccountBalance color="primary" sx={{ fontSize: 48, mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              Track Transactions
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Import and categorize your financial transactions from CSV, OFX, and QIF files.
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Assessment color="primary" sx={{ fontSize: 48, mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              Visualize Spending
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Get insights into your spending patterns with beautiful charts and reports.
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Security color="primary" sx={{ fontSize: 48, mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              Secure & Private
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Your financial data is encrypted and stored securely with 2FA protection.
            </Typography>
          </Paper>
        </Grid>
      </Grid>

      <Box sx={{ mt: 4, textAlign: 'center' }}>
        <Button
          variant="contained"
          size="large"
          onClick={() => navigate('/login')}
          sx={{ mr: 2 }}
          data-testid="login-button"
        >
          Login
        </Button>
        <Button
          variant="outlined"
          size="large"
          onClick={() => navigate('/register')}
          sx={{ mr: 2 }}
          data-testid="register-button"
        >
          Sign Up
        </Button>
        <Button
          variant="text"
          size="large"
          onClick={() => navigate('/health')}
          sx={{ mr: 2 }}
        >
          Check System Health
        </Button>
        <Button
          variant="text"
          size="large"
          onClick={() => window.open('/docs', '_blank')}
        >
          View API Docs
        </Button>
      </Box>
    </Box>
  );
};

export default HomePage;
