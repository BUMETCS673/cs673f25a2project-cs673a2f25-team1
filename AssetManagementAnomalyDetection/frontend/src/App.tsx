import React, { useState, useEffect } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { Container, Typography, Box, Paper, Grid, Button } from '@mui/material';
import { Line } from 'react-chartjs-2';
import axios from 'axios';
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
  detected_at: string;
}

function App() {
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
      setAnomalies(response.data);
    } catch (error) {
      console.error('Error fetching anomalies:', error);
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

  const chartData = {
    labels: anomalies.map(a => new Date(a.detected_at).toLocaleDateString()),
    datasets: [
      {
        label: 'Anomaly Score',
        data: anomalies.map(a => a.anomaly_score),
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
      },
    ],
  };

  return (
    <ThemeProvider theme={theme}>
      <Container maxWidth="lg">
        <Box sx={{ my: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Asset Management Anomaly Detection
          </Typography>

          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Portfolios
                </Typography>
                {portfolios.map((portfolio) => (
                  <Box key={portfolio.id} sx={{ mb: 1 }}>
                    <Button
                      variant={selectedPortfolio?.id === portfolio.id ? "contained" : "outlined"}
                      fullWidth
                      onClick={() => handlePortfolioSelect(portfolio)}
                    >
                      {portfolio.name}
                    </Button>
                  </Box>
                ))}
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
                        <Line data={chartData} />
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
}

export default App;
