import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  CircularProgress,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Card,
  CardContent,
  LinearProgress,
  Chip
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';

interface PDFData {
  rent?: number;
  management_fee?: number;
  repair?: number;
  deposit?: number;
  misc?: number;
  total?: number;
}

interface UploadResponse {
  success: boolean;
  data?: PDFData;
  confidence?: number;
  method?: string;
  field_confidences?: Record<string, number>;
  error?: string;
  message?: string;
}

export default function PDFUploadTest() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<UploadResponse | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [useAzure, setUseAzure] = useState(true);

  const API_ENDPOINTS = {
    local: 'http://127.0.0.1:5001/api/upload-pdf',
    azure: 'https://ocr-backend-app.azurewebsites.net/api/upload-pdf'
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type === 'application/pdf') {
        setSelectedFile(file);
      } else {
        alert('Please upload a PDF file');
      }
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      alert('Please select a PDF file');
      return;
    }

    setLoading(true);
    setResponse(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const endpoint = useAzure ? API_ENDPOINTS.azure : API_ENDPOINTS.local;
      const res = await fetch(endpoint, {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();
      setResponse(data);
    } catch (error) {
      setResponse({
        success: false,
        error: 'Network error',
        message: error instanceof Error ? error.message : 'Failed to upload file'
      });
    } finally {
      setLoading(false);
    }
  };

  const formatValue = (value: number | null | undefined) => {
    if (value === null || value === undefined) return '-';
    return `$${value.toFixed(2)}`;
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'success';
    if (confidence >= 0.6) return 'warning';
    return 'error';
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        PDF OCR Upload Test
      </Typography>

      {/* Endpoint Selection */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Select Endpoint
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant={useAzure ? 'contained' : 'outlined'}
              onClick={() => setUseAzure(true)}
              size="small"
            >
              Azure (Production)
            </Button>
            <Button
              variant={!useAzure ? 'contained' : 'outlined'}
              onClick={() => setUseAzure(false)}
              size="small"
            >
              Local (Port 5001)
            </Button>
          </Box>
          <Typography variant="caption" display="block" sx={{ mt: 1, color: 'text.secondary' }}>
            Current: {useAzure ? API_ENDPOINTS.azure : API_ENDPOINTS.local}
          </Typography>
        </CardContent>
      </Card>

      {/* File Upload Area */}
      <Paper
        sx={{
          p: 3,
          mb: 3,
          border: dragActive ? '2px dashed #1976d2' : '2px dashed #ccc',
          borderRadius: 2,
          backgroundColor: dragActive ? '#f0f8ff' : '#fafafa',
          cursor: 'pointer',
          transition: 'all 0.3s ease'
        }}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <Box textAlign="center">
          <CloudUploadIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            Drag & Drop PDF File Here
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            or
          </Typography>
          <Button
            variant="contained"
            component="label"
            startIcon={<CloudUploadIcon />}
            sx={{ mt: 1 }}
          >
            Choose File
            <input
              type="file"
              accept=".pdf"
              hidden
              onChange={handleFileSelect}
            />
          </Button>

          {selectedFile && (
            <Box sx={{ mt: 2 }}>
              <Chip
                icon={<CheckCircleIcon />}
                label={selectedFile.name}
                color="success"
                onDelete={() => setSelectedFile(null)}
              />
            </Box>
          )}
        </Box>
      </Paper>

      {/* Upload Button */}
      {selectedFile && (
        <Box textAlign="center" sx={{ mb: 3 }}>
          <Button
            variant="contained"
            size="large"
            onClick={handleUpload}
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : <CloudUploadIcon />}
          >
            {loading ? 'Processing...' : 'Upload & Process PDF'}
          </Button>
          {loading && (
            <Box sx={{ mt: 2 }}>
              <LinearProgress />
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
                Note: First request to Azure may take 30-60 seconds (cold start)
              </Typography>
            </Box>
          )}
        </Box>
      )}

      {/* Results */}
      {response && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            {response.success ? (
              <>
                <Alert severity="success" sx={{ mb: 2 }}>
                  PDF processed successfully!
                </Alert>

                {/* Overall Confidence */}
                <Box sx={{ mb: 3 }}>
                  <Typography variant="h6">
                    Overall Confidence: {' '}
                    <Chip
                      label={`${((response.confidence || 0) * 100).toFixed(0)}%`}
                      color={getConfidenceColor(response.confidence || 0) as any}
                      size="small"
                    />
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Method: {response.method}
                  </Typography>
                </Box>

                {/* Extracted Data Table */}
                <TableContainer component={Paper}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Field</TableCell>
                        <TableCell align="right">Value</TableCell>
                        <TableCell align="right">Confidence</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {response.data && Object.entries(response.data).map(([key, value]) => (
                        <TableRow key={key}>
                          <TableCell component="th" scope="row">
                            {key.charAt(0).toUpperCase() + key.slice(1).replace('_', ' ')}
                          </TableCell>
                          <TableCell align="right">
                            <strong>{formatValue(value)}</strong>
                          </TableCell>
                          <TableCell align="right">
                            {response.field_confidences?.[key] ? (
                              <Chip
                                label={`${(response.field_confidences[key] * 100).toFixed(0)}%`}
                                size="small"
                                color={getConfidenceColor(response.field_confidences[key]) as any}
                              />
                            ) : '-'}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>

                {/* Raw JSON Response */}
                <Box sx={{ mt: 3 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Raw Response:
                  </Typography>
                  <Paper sx={{ p: 2, backgroundColor: '#f5f5f5' }}>
                    <pre style={{ fontSize: '12px', overflow: 'auto' }}>
                      {JSON.stringify(response, null, 2)}
                    </pre>
                  </Paper>
                </Box>
              </>
            ) : (
              <Alert severity="error" icon={<ErrorIcon />}>
                <strong>Error:</strong> {response.error || 'Unknown error'}
                <br />
                {response.message}
              </Alert>
            )}
          </CardContent>
        </Card>
      )}
    </Box>
  );
}