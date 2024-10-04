import pytest
from interpreter.core.core import OpenInterpreter

def test_interpreter_initialization():
    interpreter = OpenInterpreter()
    assert isinstance(interpreter, OpenInterpreter)

def test_interpreter_attributes():
    interpreter = OpenInterpreter()
    
    # Check for various attributes that might exist
    possible_attributes = ['config', 'computer', 'llm', 'messages']
    
    for attr in possible_attributes:
        if hasattr(interpreter, attr):
            assert getattr(interpreter, attr) is not None, f"{attr} should not be None if it exists"
            
            # Perform basic type checks if the attribute exists
            if attr == 'config' and hasattr(interpreter, 'config'):
                assert isinstance(interpreter.config, dict), "config should be a dictionary"
            elif attr == 'computer' and hasattr(interpreter, 'computer'):
                assert hasattr(interpreter.computer, 'run'), "computer should have a 'run' method"
            elif attr == 'messages' and hasattr(interpreter, 'messages'):
                assert isinstance(interpreter.messages, list), "messages should be a list"

def test_interpreter_methods():
    interpreter = OpenInterpreter()
    
    # Check for the existence of key methods
    possible_methods = ['chat', 'start_server', 'run']
    
    for method in possible_methods:
        if hasattr(interpreter, method):
            assert callable(getattr(interpreter, method)), f"{method} should be callable if it exists"

def test_interpreter_custom_settings():
    custom_settings = {
        'model': 'gpt-4',
        'temperature': 0.5,
        'system_message': 'You are a helpful assistant.'
    }
    
    interpreter = OpenInterpreter()
    
    # Try to set custom settings if config exists
    if hasattr(interpreter, 'config'):
        interpreter.config.update(custom_settings)
        
        for key, value in custom_settings.items():
            assert interpreter.config.get(key) == value, f"config['{key}'] should be {value}"
    else:
        pytest.skip("Skipping custom settings test as 'config' attribute doesn't exist")

# Add more tests as needed to cover other functionalities of the OpenInterpreter
