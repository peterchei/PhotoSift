"""
Tests for Common UI Components
Tests shared UI components used across PhotoSift applications
"""

import unittest
import os
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from CommonUI import ModernColors, ModernButton, TrashManager, ToolTip, StatusBar


class TestCommonUI(unittest.TestCase):
    """Test cases for common UI components"""
    
    def test_modern_colors_exists(self):
        """Test that color scheme is defined"""
        colors = ModernColors.get_color_scheme()
        self.assertIsInstance(colors, dict)
        print("✓ Color scheme defined")
    
    def test_color_scheme_completeness(self):
        """Test that all required colors are defined"""
        colors = ModernColors.get_color_scheme()
        
        required_colors = [
            'bg_primary', 'bg_secondary', 'bg_card', 'bg_sidebar',
            'accent', 'accent_hover', 'text_primary', 'text_secondary',
            'success', 'warning', 'danger'
        ]
        
        for color in required_colors:
            self.assertIn(color, colors)
            self.assertIsInstance(colors[color], str)
            self.assertTrue(colors[color].startswith('#'))
        
        print(f"✓ All {len(required_colors)} required colors defined")
    
    def test_modern_button_factory_methods(self):
        """Test that ModernButton factory methods exist"""
        self.assertTrue(callable(ModernButton.create_primary_button))
        self.assertTrue(callable(ModernButton.create_danger_button))
        self.assertTrue(callable(ModernButton.create_secondary_button))
        print("✓ ModernButton factory methods exist")
    
    def test_trash_manager_initialization(self):
        """Test TrashManager class structure"""
        # Test that class exists and has required methods
        self.assertTrue(hasattr(TrashManager, '__init__'))
        self.assertTrue(hasattr(TrashManager, 'update_trash_count'))
        self.assertTrue(hasattr(TrashManager, 'open_trash_folder'))
        print("✓ TrashManager has required methods")
    
    def test_tooltip_class_exists(self):
        """Test that ToolTip class exists"""
        self.assertTrue(hasattr(ToolTip, '__init__'))
        self.assertTrue(hasattr(ToolTip, 'showtip'))
        self.assertTrue(hasattr(ToolTip, 'hidetip'))
        print("✓ ToolTip class properly defined")
    
    def test_status_bar_class_exists(self):
        """Test that StatusBar class exists"""
        self.assertTrue(hasattr(StatusBar, '__init__'))
        self.assertTrue(hasattr(StatusBar, 'set_text'))
        print("✓ StatusBar class properly defined")


class TestUIComponentIntegration(unittest.TestCase):
    """Integration tests for UI components"""
    
    def test_color_scheme_consistency(self):
        """Test that color scheme is consistent across calls"""
        colors1 = ModernColors.get_color_scheme()
        colors2 = ModernColors.get_color_scheme()
        
        self.assertEqual(colors1, colors2)
        print("✓ Color scheme is consistent")
    
    def test_color_values_valid_hex(self):
        """Test that all color values are valid hex codes"""
        colors = ModernColors.get_color_scheme()
        
        for color_name, color_value in colors.items():
            self.assertTrue(color_value.startswith('#'))
            self.assertIn(len(color_value), [4, 7])  # #RGB or #RRGGBB
            
            # Verify hex characters
            hex_chars = set('0123456789abcdefABCDEF')
            self.assertTrue(all(c in hex_chars for c in color_value[1:]))
        
        print("✓ All color values are valid hex codes")


if __name__ == '__main__':
    print("=" * 70)
    print("Running Common UI Tests")
    print("=" * 70)
    unittest.main(verbosity=2)
