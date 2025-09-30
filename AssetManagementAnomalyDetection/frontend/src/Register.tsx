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
import { PersonAdd } from '@mui/icons-material';
import axios from 'axios';

interface RegisterProps {
  onRegister: () => void;
  onSwitchToLogin: () => void;
}

interface RegisterData {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
  confirmPassword: string;
}

const Register: React.FC<RegisterProps> = ({ onRegister, onSwitchToLogin }) => {
  const [formData, setFormData] = useState<RegisterData>({
    first_name: '',
    last_name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError('');

    // Validate password match
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    // Prepare data for API
    const { confirmPassword, ...registerData } = formData;

    try {
      const response = await axios.post('/api/auth/register', registerData);
      if (response.status === 201) {
        onRegister();
        onSwitchToLogin();
      }
    } catch (err: any) {
      setError(err.response?.data?.message || 'Registration failed');
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
          <PersonAdd />
        </Avatar>
        <Typography component="h1" variant="h5">
          Sign Up
        </Typography>

        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1, width: '100%' }}>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Box sx={{ display: 'flex', gap: 2 }}>
            <TextField
              margin="normal"
              required
              fullWidth
              id="first_name"
              label="First Name"
              name="first_name"
              autoComplete="given-name"
              autoFocus
              value={formData.first_name}
              onChange={handleChange}
              disabled={loading}
            />

            <TextField
              margin="normal"
              required
              fullWidth
              id="last_name"
              label="Last Name"
              name="last_name"
              autoComplete="family-name"
              value={formData.last_name}
              onChange={handleChange}
              disabled={loading}
            />
          </Box>

          <TextField
            margin="normal"
            required
            fullWidth
            id="email"
            label="Email Address"
            name="email"
            autoComplete="email"
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
            autoComplete="new-password"
            value={formData.password}
            onChange={handleChange}
            disabled={loading}
          />

          <TextField
            margin="normal"
            required
            fullWidth
            name="confirmPassword"
            label="Confirm Password"
            type="password"
            id="confirmPassword"
            autoComplete="new-password"
            value={formData.confirmPassword}
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
            {loading ? 'Creating Account...' : 'Sign Up'}
          </Button>

          <Box sx={{ textAlign: 'center' }}>
            <Link
              component="button"
              variant="body2"
              onClick={onSwitchToLogin}
              sx={{ cursor: 'pointer' }}
            >
              Already have an account? Sign In
            </Link>
          </Box>
        </Box>
      </Paper>
    </Container>
  );
};

export default Register;
