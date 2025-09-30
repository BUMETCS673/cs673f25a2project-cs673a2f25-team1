import React from 'react';
import { Box } from '@mui/material';

export default function PDFUploadTestSimple() {
  return (
    <Box sx={{ p: 3 }}>
      <iframe
        title="PDF Upload Test"
        src="/pdf-test.html"
        style={{ width: '100%', height: '600px', border: 'none' }}
      />
    </Box>
  );
}