"""
Tests for the AI Redactor system
"""

import unittest
from unittest.mock import patch, MagicMock

from redactor import (
    Redactor,
    RedactorConfig,
    RedactionTechnique,
    SophisticationLevel,
    DataTypeConfig,
    create_redactor,
    redact,
    redact_json,
)


class TestDataTypeConfig(unittest.TestCase):
    """Tests for DataTypeConfig"""
    
    def test_minimal_level(self):
        cfg = DataTypeConfig.for_level(SophisticationLevel.MINIMAL)
        self.assertTrue(cfg.names)
        self.assertTrue(cfg.ssn)
        self.assertFalse(cfg.physical_addresses)
        self.assertFalse(cfg.nicknames)
    
    def test_standard_level(self):
        cfg = DataTypeConfig.for_level(SophisticationLevel.STANDARD)
        self.assertTrue(cfg.names)
        self.assertTrue(cfg.physical_addresses)
        self.assertFalse(cfg.nicknames)
    
    def test_comprehensive_level(self):
        cfg = DataTypeConfig.for_level(SophisticationLevel.COMPREHENSIVE)
        self.assertTrue(cfg.nicknames)
        self.assertTrue(cfg.locations)
        self.assertTrue(cfg.employers)
        self.assertFalse(cfg.travel_history)
    
    def test_paranoid_level(self):
        cfg = DataTypeConfig.for_level(SophisticationLevel.PARANOID)
        self.assertTrue(cfg.nicknames)
        self.assertTrue(cfg.travel_history)
        self.assertTrue(cfg.vehicle_info)


class TestRedactorConfig(unittest.TestCase):
    """Tests for RedactorConfig"""
    
    def test_default_config(self):
        cfg = RedactorConfig()
        self.assertEqual(cfg.technique, RedactionTechnique.BOTH)
        self.assertEqual(cfg.sophistication, SophisticationLevel.STANDARD)
        self.assertIsNotNone(cfg.data_types)
        self.assertEqual(cfg.mask_char, "*")
        self.assertEqual(cfg.mask_length, 3)
    
    def test_custom_config(self):
        cfg = RedactorConfig(
            technique=RedactionTechnique.MASK,
            sophistication=SophisticationLevel.PARANOID,
            target_individuals=["John Doe"],
            mask_char="#",
            mask_length=5
        )
        self.assertEqual(cfg.technique, RedactionTechnique.MASK)
        self.assertEqual(cfg.sophistication, SophisticationLevel.PARANOID)
        self.assertEqual(cfg.target_individuals, ["John Doe"])
        self.assertEqual(cfg.mask_char, "#")
        self.assertEqual(cfg.mask_length, 5)


class TestCreateRedactor(unittest.TestCase):
    """Tests for create_redactor factory function"""
    
    def test_default_creation(self):
        r = create_redactor()
        self.assertIsInstance(r, Redactor)
        self.assertEqual(r.config.technique, RedactionTechnique.BOTH)
        self.assertEqual(r.config.sophistication, SophisticationLevel.STANDARD)
    
    def test_custom_creation(self):
        r = create_redactor(
            technique="mask",
            sophistication="paranoid",
            target_individuals=["Jane Smith"]
        )
        self.assertEqual(r.config.technique, RedactionTechnique.MASK)
        self.assertEqual(r.config.sophistication, SophisticationLevel.PARANOID)
        self.assertEqual(r.config.target_individuals, ["Jane Smith"])


class TestRedactorPrompts(unittest.TestCase):
    """Tests for prompt generation"""
    
    def test_mask_prompt_contains_document(self):
        r = create_redactor(technique="mask")
        prompt = r._build_mask_prompt("Test document with John", "***", False)
        self.assertIn("Test document with John", prompt)
        self.assertIn("***", prompt)
    
    def test_substitution_prompt_contains_document(self):
        r = create_redactor(technique="substitute")
        prompt = r._build_substitution_prompt("Test document with Jane")
        self.assertIn("Test document with Jane", prompt)
        self.assertIn("SUBSTITUTE", prompt)
    
    def test_individuals_in_prompt(self):
        r = create_redactor(target_individuals=["Mickey Mouse", "Donald Duck"])
        individuals_desc = r._get_individuals_description()
        self.assertIn("Mickey Mouse", individuals_desc)
        self.assertIn("Donald Duck", individuals_desc)
    
    def test_paranoid_includes_deduction_warning(self):
        r = create_redactor(sophistication="paranoid")
        system_msg = r._build_mask_system_message(False)
        self.assertIn("re-identification", system_msg)


class TestRedactorWithMockedLLM(unittest.TestCase):
    """Tests for redaction with mocked LLM calls"""
    
    @patch('redactor.requests.post')
    def test_mask_redaction(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Hello, ***!'}}]
        }
        mock_post.return_value = mock_response
        
        r = create_redactor(technique="mask")
        result = r.redact("Hello, John!")
        
        self.assertEqual(result, "Hello, ***!")
        mock_post.assert_called_once()
    
    @patch('redactor.requests.post')
    def test_substitute_redaction(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Hello, Robert!'}}]
        }
        mock_post.return_value = mock_response
        
        r = create_redactor(technique="substitute")
        result = r.redact("Hello, John!")
        
        self.assertEqual(result, "Hello, Robert!")
    
    @patch('redactor.requests.post')
    def test_both_technique_two_calls(self, mock_post):
        mock_response1 = MagicMock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = {
            'choices': [{'message': {'content': 'SSN: ***, Name: John'}}]
        }
        
        mock_response2 = MagicMock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            'choices': [{'message': {'content': 'SSN: ***, Name: Robert'}}]
        }
        
        mock_post.side_effect = [mock_response1, mock_response2]
        
        r = create_redactor(technique="both")
        result = r.redact("SSN: 123-45-6789, Name: John")
        
        self.assertEqual(result, "SSN: ***, Name: Robert")
        self.assertEqual(mock_post.call_count, 2)
    
    @patch('redactor.requests.post')
    def test_json_redaction(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{'message': {'content': '{"name": "***", "city": "Denver"}'}}]
        }
        mock_post.return_value = mock_response
        
        r = create_redactor(technique="mask")
        result = r.redact_json({"name": "John", "city": "Denver"})
        
        self.assertEqual(result, {"name": "***", "city": "Denver"})
    
    @patch('redactor.requests.post')
    def test_api_error_handling(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response
        
        r = create_redactor()
        with self.assertRaises(Exception) as context:
            r.redact("Test document")
        
        self.assertIn("LLM API error", str(context.exception))


class TestConvenienceFunctions(unittest.TestCase):
    """Tests for module-level convenience functions"""
    
    @patch('redactor.requests.post')
    def test_redact_function(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Hello, ***!'}}]
        }
        mock_post.return_value = mock_response
        
        result = redact("Hello, John!", technique="mask")
        self.assertEqual(result, "Hello, ***!")
    
    @patch('redactor.requests.post')
    def test_redact_json_function(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{'message': {'content': '{"name": "Robert"}'}}]
        }
        mock_post.return_value = mock_response
        
        result = redact_json({"name": "John"}, technique="substitute")
        self.assertEqual(result, {"name": "Robert"})


if __name__ == '__main__':
    unittest.main()
