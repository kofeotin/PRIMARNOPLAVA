import unittest
from unittest.mock import patch, MagicMock
from server import app
import io

class TestServer(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('smtplib.SMTP')
    def test_submit_form_success(self, mock_smtp):
        # Mocking SMTP connection
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server

        # Set environment variables for testing (handled inside server.py, but we can patch os.environ if needed)
        # For now, let's assume default behavior which returns 500 because of missing password.
        # So we need to patch os.environ or modify server.py to allow testing.
        
        # Actually, server.py checks for 'YOUR_APP_PASSWORD_HERE'.
        # Let's patch os.environ inside the test context if possible, or patch the variable in server module.
        
        with patch('server.EMAIL_PASSWORD', 'test_password'):
            # Create a mock audio file
            audio_file = (io.BytesIO(b"fake audio data"), 'voice_memo.wav')
            
            data = {
                'nick': 'Test Nick',
                'odgovor': 'Test Answer',
                'consent': 'true',
                'audio': audio_file
            }

            response = self.app.post('/submit', data=data, content_type='multipart/form-data')

            # Verify response
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {'message': 'Email sent successfully'})

            # Verify SMTP calls
            mock_smtp.assert_called_with('smtp.gmail.com', 587)
            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_with('primarnoplava@gmail.com', 'test_password')
            mock_server.sendmail.assert_called()

    def test_submit_form_no_credentials(self):
        # Without patching password, it should fail
        data = {
            'nick': 'Test Nick',
            'odgovor': 'Test Answer',
            'consent': 'true'
        }
        
        response = self.app.post('/submit', data=data)
        self.assertEqual(response.status_code, 500)
        self.assertIn('Email password not configured', response.json['error'])

if __name__ == '__main__':
    unittest.main()
