"""Unit tests for device fingerprinting functionality.

FASE 3: Tests for parse_device_name() function and device info capture.
"""

import pytest
from robbot.core.security import parse_device_name


class TestParseDeviceName:
    """Test device name parsing from user-agent strings."""
    
    def test_chrome_on_windows(self):
        """Should parse Chrome on Windows correctly."""
        user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
        result = parse_device_name(user_agent)
        assert result == "Chrome on Windows"
    
    def test_firefox_on_linux(self):
        """Should parse Firefox on Linux correctly."""
        user_agent = (
            "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) "
            "Gecko/20100101 Firefox/121.0"
        )
        result = parse_device_name(user_agent)
        assert result == "Firefox on Linux"
    
    def test_safari_on_iphone(self):
        """Should parse Safari on iPhone correctly."""
        user_agent = (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/17.0 Mobile/15E148 Safari/604.1"
        )
        result = parse_device_name(user_agent)
        assert result == "Safari on iPhone"
    
    def test_safari_on_macos(self):
        """Should parse Safari on macOS correctly."""
        user_agent = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/17.1 Safari/605.1.15"
        )
        result = parse_device_name(user_agent)
        assert result == "Safari on macOS"
    
    def test_edge_on_windows(self):
        """Should parse Edge on Windows correctly."""
        user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
        )
        result = parse_device_name(user_agent)
        assert result == "Edge on Windows"
    
    def test_chrome_on_android(self):
        """Should parse Chrome on Android correctly."""
        user_agent = (
            "Mozilla/5.0 (Linux; Android 13; SM-S901B) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Mobile Safari/537.36"
        )
        result = parse_device_name(user_agent)
        assert result == "Chrome on Android"
    
    def test_safari_on_ipad(self):
        """Should parse Safari on iPad correctly."""
        user_agent = (
            "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/17.0 Mobile/15E148 Safari/604.1"
        )
        result = parse_device_name(user_agent)
        assert result == "Safari on iPad"
    
    def test_empty_user_agent(self):
        """Should handle empty user agent gracefully."""
        result = parse_device_name("")
        assert result == "Unknown Device"
    
    def test_none_user_agent(self):
        """Should handle None user agent gracefully."""
        result = parse_device_name(None)
        assert result == "Unknown Device"
    
    def test_unknown_browser_and_os(self):
        """Should handle unknown browser/OS gracefully."""
        user_agent = "CustomBot/1.0"
        result = parse_device_name(user_agent)
        assert "Unknown" in result
