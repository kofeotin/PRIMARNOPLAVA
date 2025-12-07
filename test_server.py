import unittest
from unittest.mock import patch, MagicMock
from server import app
import io
import os

class TestServer(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('smtplib.SMTP')
    def test_submit_form_success(self, mock_smtp):
        # Mocking SMTP connection
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server

        with patch('server.EMAIL_PASSWORD', 'test_password'):
            # Create a mock audio file
            audio_file = (io.BytesIO(b"fake audio data"), 'voice_memo.wav')
            
            data = {
                'nick': 'Test Nick',
                'odgovor': 'Test Answer',
                'consent': 'true',
                'attachment': audio_file  # Matches script.js and server.py
            }

            response = self.app.post('/submit', data=data, content_type='multipart/form-data')

            # Verify response
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {'message': 'Email sent successfully', 'success': 'true'})

            # Verify SMTP calls
            mock_smtp.assert_called_with('smtp.gmail.com', 587)
            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_with('primarnoplava@gmail.com', 'test_password')
            mock_server.sendmail.assert_called()

    def test_submit_form_no_credentials(self):
        # Without patching password (and assuming env var is not set), it should fail
        # We need to ensure EMAIL_PASSWORD is None or empty in server module for this test
        with patch('server.EMAIL_PASSWORD', None):
            data = {
                'nick': 'Test Nick',
                'odgovor': 'Test Answer',
                'consent': 'true'
            }
            
            response = self.app.post('/submit', data=data)
            self.assertEqual(response.status_code, 500)
            self.assertIn('Email password not configured', response.json['error'])

    def test_serve_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'PRIMARNOPLAVA.COM', response.data)

    def test_serve_static_en(self):
        response = self.app.get('/en.html')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'PRIMARNOPLAVA.COM', response.data)

    def test_serve_static_js(self):
        response = self.app.get('/script.js')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'document.addEventListener', response.data)

if __name__ == '__main__':
    unittest.main()
