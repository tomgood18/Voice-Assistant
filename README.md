# Voice Assistant
Voice Assistant is a simple Python application that uses the Google Cloud Text-to-Speech API and the OpenAI GPT-3 API to speak and generate text, respectively.

## Prerequisites
Before running the application, you will need to provide the following credentials:

1. A Google Cloud Platform account with the Text-to-Speech API enabled.

2. A service account key in JSON format, which you can create in the Google Cloud Console. You should place the JSON file in the project directory and name it "ServiceAccount.json".

3. An OpenAI API key, which you can obtain from the OpenAI website.
## Installation
1. Clone the repository to your local machine.

2. Install the required Python packages by running pip install -r requirements.txt.

3. Add your own "ServiceAccount.json" file to the project directory.

4. Set the environment variable OPENAI_API_KEY to your OpenAI API key.
## Usage
* Run the application by running the command ```python main.py``` in your terminal.

* Initialize the conversation by providing a system message. 
  E.g. "You are an intelligent assistant. Be concise in your answers."
  
* Press the spacebar and begin talking into your microphone
## Contributing
I welcome contributions to this project! If you have any suggestions or would like to report a bug, please open an issue on the GitHub repository.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
