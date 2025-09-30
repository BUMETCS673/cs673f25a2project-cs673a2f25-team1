import React, { useState } from 'react';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  Link,
  Avatar,
  CssBaseline
} from '@mui/material';
import { LockOutlined } from '@mui/icons-material';
import axios from 'axios';

interface LoginProps {
  onLogin: (token: string, user: any) => void;
  onSwitchToRegister: () => void;
}

interface LoginData {
  email: string;
  password: string;
}

const Login: React.FC<LoginProps> = ({ onLogin, onSwitchToRegister }) => {
  const [formData, setFormData] = useState<LoginData>({
    email: '',
    password: ''
  });
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post('/api/auth/login', formData);
      const { access_token, user } = response.data;
      localStorage.setItem('token', access_token);
      onLogin(access_token, user);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [event.target.name]: event.target.value
    });
  };

  return (
    <Container component="main" maxWidth="sm">
      <CssBaseline />
      <Paper
        elevation={3}
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          padding: 4,
        }}
      >
        <Avatar sx={{ m: 1, bgcolor: 'secondary.main' }}>
          <LockOutlined />
        </Avatar>
        <Typography component="h1" variant="h5">
          Sign In
        </Typography>

        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1, width: '100%' }}>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <TextField
            margin="normal"
            required
            fullWidth
            id="email"
            label="Email Address"
            name="email"
            autoComplete="email"
            autoFocus
            value={formData.email}
            onChange={handleChange}
            disabled={loading}
          />

          <TextField
            margin="normal"
            required
            fullWidth
            name="password"
            label="Password"
            type="password"
            id="password"
            autoComplete="current-password"
            value={formData.password}
            onChange={handleChange}
            disabled={loading}
          />

          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
            disabled={loading}
          >
            {loading ? 'Signing In...' : 'Sign In'}
          </Button>

          <Box sx={{ textAlign: 'center' }}>
            <Link
              component="button"
              variant="body2"
              onClick={onSwitchToRegister}
              sx={{ cursor: 'pointer' }}
            >
              Don't have an account? Sign Up
            </Link>
          </Box>
        </Box>
      </Paper>
    </Container>
  );
};

export default Login;
