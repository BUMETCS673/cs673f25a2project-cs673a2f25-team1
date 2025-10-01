import React, { useState, useEffect } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { Container, Typography, Box, Paper, Grid, Button, FormControl, InputLabel, Select, MenuItem, SelectChangeEvent } from '@mui/material';
import { Line } from 'react-chartjs-2';
import axios from 'axios';
import { AuthProvider, useAuth } from './AuthContext.tsx';
import Login from './Login.tsx';
import Register from './Register.tsx';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

// Configure axios defaults
axios.defaults.baseURL = 'http://127.0.0.1:5000';

// Add token to all requests
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    } else if (config.headers && config.headers.Authorization) {
      // Remove any empty Authorization header
      delete config.headers.Authorization;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle unauthorized responses
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token');
      window.location.reload(); // Force reload to show login
    }
    return Promise.reject(error);
  }
);

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const theme = createTheme();

// Dashboard Component
const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [selectedPortfolio, setSelectedPortfolio] = useState<Portfolio | null>(null);
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchPortfolios();
  }, []);

  const fetchPortfolios = async () => {
    try {
      const response = await axios.get('/api/portfolios');
      setPortfolios(response.data);
    } catch (error) {
      console.error('Error fetching portfolios:', error);
    }
  };

  const fetchAnomalies = async (portfolioId: number) => {
    try {
      const response = await axios.get(`/api/anomalies/${portfolioId}`);
      setAnomalies(response.data.filter(anomaly => anomaly.fee_date)); // Filter out any without dates
    } catch (error) {
      console.error('Error fetching anomalies:', error);
      setAnomalies([]); // Clear anomalies on error
    }
  };

  const runAnomalyDetection = async (portfolioId: number) => {
    setLoading(true);
    try {
      await axios.post(`/api/detect-anomalies/${portfolioId}`);
      await fetchAnomalies(portfolioId);
    } catch (error) {
      console.error('Error running anomaly detection:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePortfolioSelect = (portfolio: Portfolio) => {
    setSelectedPortfolio(portfolio);
    fetchAnomalies(portfolio.id);
  };

  interface Portfolio {
    id: number;
    name: string;
    manager: string;
    total_assets: number;
  }

  interface Anomaly {
    id: number;
    fee_id: number;
    anomaly_score: number;
    detected_at?: string;
    fee_date?: string;
    fee_amount?: number;
  }

  // Generate current dates for each anomaly
  const generateCurrentDates = () => {
    const now = new Date();
    const currentMonth = now.getMonth();
    const currentYear = now.getFullYear();

    return anomalies.map((_, index) => {
      const date = new Date(currentYear, currentMonth, index + 1);
      return date.toLocaleDateString();
    });
  };

  const chartData = {
    labels: generateCurrentDates(),
    datasets: [
      {
        label: 'Anomaly Score',
        data: anomalies.map(a => a.anomaly_score),
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      title: {
        display: true,
        text: 'Anomaly Detection Results',
      },
    },
    scales: {
      y: {
        min: 0.01,
        max: 0.11,
        title: {
          display: true,
          text: 'Anomaly Score',
        },
      },
      x: {
        title: {
          display: true,
          text: 'Date',
        },
      },
    },
  };

  return (
    <ThemeProvider theme={theme}>
      <Container maxWidth="lg">
        <Box sx={{ my: 4 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h4" component="h1">
              Asset Management Anomaly Detection
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Typography>Welcome, {user?.first_name}!</Typography>
              <Button variant="outlined" onClick={logout}>Logout</Button>
            </Box>
          </Box>

          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Select Portfolio
                </Typography>
                <FormControl fullWidth variant="outlined" sx={{ mb: 2 }}>
                  <InputLabel id="portfolio-select-label">Available Portfolios</InputLabel>
                  <Select
                    labelId="portfolio-select-label"
                    id="portfolio-select"
                    value={selectedPortfolio?.id ? String(selectedPortfolio.id) : ''}
                    label="Available Portfolios"
                    onChange={(event: SelectChangeEvent<string>) => {
                      const portfolioId = parseInt(event.target.value, 10);
                      const portfolio = portfolios.find(p => p.id === portfolioId);
                      if (portfolio) {
                        handlePortfolioSelect(portfolio);
                      }
                    }}
                  >
                    {portfolios.map((portfolio) => (
                      <MenuItem key={portfolio.id} value={portfolio.id}>
                        {portfolio.name} - {portfolio.manager}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Paper>
            </Grid>

            <Grid item xs={12} md={8}>
              {selectedPortfolio && (
                <Paper sx={{ p: 2 }}>
                  <Typography variant="h6" gutterBottom>
                    {selectedPortfolio.name}
                  </Typography>
                  <Typography>Manager: {selectedPortfolio.manager}</Typography>
                  <Typography>Total Assets: ${selectedPortfolio.total_assets.toLocaleString()}</Typography>

                  <Box sx={{ mt: 2 }}>
                    <Button
                      variant="contained"
                      onClick={() => runAnomalyDetection(selectedPortfolio.id)}
                      disabled={loading}
                    >
                      {loading ? 'Detecting...' : 'Run Anomaly Detection'}
                    </Button>
                  </Box>

                  {anomalies.length > 0 && (
                    <Box sx={{ mt: 3 }}>
                      <Typography variant="h6" gutterBottom>
                        Detected Anomalies ({anomalies.length})
                      </Typography>
                      <Box sx={{ height: 300 }}>
                        <Line data={chartData} options={chartOptions} />
                      </Box>
                    </Box>
                  )}
                </Paper>
              )}
            </Grid>
          </Grid>
        </Box>
      </Container>
    </ThemeProvider>
  );
};

// Main App Component with Authentication
function App() {
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');

  const switchToRegister = () => setAuthMode('register');
  const switchToLogin = () => setAuthMode('login');

  return (
    <AuthProvider>
      <AppContent
        authMode={authMode}
        onSwitchToRegister={switchToRegister}
        onSwitchToLogin={switchToLogin}
      />
    </AuthProvider>
  );
}

interface AppContentProps {
  authMode: 'login' | 'register';
  onSwitchToRegister: () => void;
  onSwitchToLogin: () => void;
}

const AppContent: React.FC<AppContentProps> = ({ authMode, onSwitchToRegister, onSwitchToLogin }) => {
  const { isAuthenticated, login } = useAuth();

  const handleRegister = () => {
    onSwitchToLogin();
  };

  if (isAuthenticated) {
    return <Dashboard />;
  }

  return (
    <ThemeProvider theme={theme}>
      {authMode === 'login' ? (
        <Login onLogin={login} onSwitchToRegister={onSwitchToRegister} />
      ) : (
        <Register
          onRegister={handleRegister}
          onSwitchToLogin={onSwitchToLogin}
        />
      )}
    </ThemeProvider>
  );
};

export default App;
