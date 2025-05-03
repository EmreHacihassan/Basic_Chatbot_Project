Hi this is the my Basic Chatbot Project.

This text explains how this project works and what its purpose is.

First of all you have make the virtual environment activated.

1)
cd Basic_Chatbot

Open the project folder.

2)
.\venv\Scripts\activate

Activate the virtual environment.

3)
pip install -r requirements.txt

Install the required libraries.

4)Then you have to take an API KEY from Huggingface.

https://huggingface.co/settings/tokens

It is totally free. All you have to do is create an account.

Next, paste your API key on line 33 of gui.py:



HF_TOKEN = os.getenv("HF_TOKEN", "1234")
Replace "1234" with your actual key.

Once that’s done, the project is ready to run—just click the Start button.

This project was built using Python 3.10 and the Mistral-7B model via the Hugging Face API.

When you’re finished, type:

deactivate
to exit the virtual environment.
