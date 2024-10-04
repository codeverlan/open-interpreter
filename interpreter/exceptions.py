class InterpreterError(Exception):
    """Base class for interpreter errors"""
    pass

class ConfigurationError(InterpreterError):
    """Raised when there's an issue with configuration"""
    pass

class FileOperationError(InterpreterError):
    """Raised when there's an issue with file operations"""
    pass

class ExecutionError(InterpreterError):
    """Raised when there's an issue with code execution"""
    pass