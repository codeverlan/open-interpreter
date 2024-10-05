Model Selection
Specifies which language model to use. Check out the models section for a list of available models. Open Interpreter uses LiteLLM under the hood to support over 100+ models.


Terminal

Python

Profile

interpreter --model "gpt-3.5-turbo"
​
Temperature
Sets the randomness level of the model’s output. The default temperature is 0, you can set it to any value between 0 and 1. The higher the temperature, the more random and creative the output will be.


Terminal

Python

Profile

interpreter --temperature 0.7
​
Context Window
Manually set the context window size in tokens for the model. For local models, using a smaller context window will use less RAM, which is more suitable for most devices.


Terminal

Python

Profile

interpreter --context_window 16000
​
Max Tokens
Sets the maximum number of tokens that the model can generate in a single response.


Terminal

Python

Profile

interpreter --max_tokens 100
​
Max Output
Set the maximum number of characters for code outputs.


Terminal

Python

Profile

interpreter --max_output 1000
​
API Base
If you are using a custom API, specify its base URL with this argument.


Terminal

Python

Profile

interpreter --api_base "https://api.example.com"
​
API Key
Set your API key for authentication when making API calls. For OpenAI models, you can get your API key here.


Terminal

Python

Profile

interpreter --api_key "your_api_key_here"
​
API Version
Optionally set the API version to use with your selected model. (This will override environment variables)


Terminal

Python

Profile

interpreter --api_version 2.0.2
​
LLM Supports Functions
Inform Open Interpreter that the language model you’re using supports function calling.


Terminal

Python

Profile

interpreter --llm_supports_functions
​
LLM Does Not Support Functions
Inform Open Interpreter that the language model you’re using does not support function calling.


Terminal

Python

Profile

interpreter --no-llm_supports_functions
​
Execution Instructions
If llm.supports_functions is False, this value will be added to the system message. This parameter tells language models how to execute code. This can be set to an empty string or to False if you don’t want to tell the LLM how to do this.


Python

Profile

interpreter.llm.execution_instructions = "To execute code on the user's machine, write a markdown code block. Specify the language after the ```. You will receive the output. Use any programming language."
​
LLM Supports Vision
Inform Open Interpreter that the language model you’re using supports vision. Defaults to False.


Terminal

Python

Profile

interpreter --llm_supports_vision
​
Interpreter
​
Vision Mode
Enables vision mode, which adds some special instructions to the prompt and switches to gpt-4o.


Terminal

Python

Profile

interpreter --vision
​
OS Mode
Enables OS mode for multimodal models. Currently not available in Python. Check out more information on OS mode here.


Terminal

Profile

interpreter --os
​
Version
Get the current installed version number of Open Interpreter.


Terminal

interpreter --version
​
Open Local Models Directory
Opens the models directory. All downloaded Llamafiles are saved here.


Terminal

interpreter --local_models
​
Open Profiles Directory
Opens the profiles directory. New yaml profile files can be added to this directory.


Terminal

interpreter --profiles
​
Select Profile
Select a profile to use. If no profile is specified, the default profile will be used.


Terminal

interpreter --profile local.yaml
​
Help
Display all available terminal arguments.


Terminal

interpreter --help
​
Loop (Force Task Completion)
Runs Open Interpreter in a loop, requiring it to admit to completing or failing every task.


Terminal

Python

Profile

interpreter --loop
​
Verbose
Run the interpreter in verbose mode. Debug information will be printed at each step to help diagnose issues.


Terminal

Python

Profile

interpreter --verbose
​
Safe Mode
Enable or disable experimental safety mechanisms like code scanning. Valid options are off, ask, and auto.


Terminal

Python

Profile

interpreter --safe_mode ask
​
Auto Run
Automatically run the interpreter without requiring user confirmation.


Terminal

Python

Profile

interpreter --auto_run
​
Max Budget
Sets the maximum budget limit for the session in USD.


Terminal

Python

Profile

interpreter --max_budget 0.01
​
Local Mode
Run the model locally. Check the models page for more information.


Terminal

Python

Profile

interpreter --local
​
Fast Mode
Sets the model to gpt-3.5-turbo and encourages it to only write code without confirmation.


Terminal

Profile

interpreter --fast
​
Custom Instructions
Appends custom instructions to the system message. This is useful for adding information about your system, preferred languages, etc.


Terminal

Python

Profile

interpreter --custom_instructions "This is a custom instruction."
​
System Message
We don’t recommend modifying the system message, as doing so opts you out of future updates to the core system message. Use --custom_instructions instead, to add relevant information to the system message. If you must modify the system message, you can do so by using this argument, or by changing a profile file.


Terminal

Python

Profile

interpreter --system_message "You are Open Interpreter..."
​
Disable Telemetry
Opt out of telemetry.


Terminal

Python

Profile

interpreter --disable_telemetry
​
Offline
This boolean flag determines whether to enable or disable some offline features like open procedures. Use this in conjunction with the model parameter to set your language model.


Python

Terminal

Profile

interpreter.offline = True