from interpreter import OpenInterpreter

def test_interpreter():
    interpreter = OpenInterpreter()
    
    print("Testing basic chat functionality:")
    response = interpreter.chat("Hello, can you explain what Open Interpreter is?", display=False)
    print("Response:", response)

    print("\nTesting code execution:")
    response = interpreter.chat("Can you write a Python function to calculate the factorial of a number?", display=False)
    print("Response:", response)

    print("\nTesting system message modification:")
    interpreter.system_message = "You are a helpful AI assistant specialized in Python programming."
    response = interpreter.chat("What's your primary focus?", display=False)
    print("Response:", response)

    print("\nTesting reset functionality:")
    interpreter.reset()
    response = interpreter.chat("Do you remember our previous conversation?", display=False)
    print("Response:", response)

if __name__ == "__main__":
    test_interpreter()