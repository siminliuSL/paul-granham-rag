from gpt4all import GPT4All
import os

def initialize_model():
    # Initialize the model
    # This will download the model if it's not already present
    model = GPT4All("ggml-gpt4all-j-v1.3-groovy")
    return model

def chat_with_model(model, user_input):
    # Generate a response
    response = model.generate(
        prompt=user_input,
        max_tokens=200,
        temp=0.7,
        top_k=40,
        top_p=0.9,
        repeat_penalty=1.1
    )
    return response

def main():
    print("Initializing GPT4All model...")
    model = initialize_model()
    print("Model initialized! You can start chatting (type 'quit' to exit)")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'quit':
            break
            
        print("\nAssistant: ", end='')
        response = chat_with_model(model, user_input)
        print(response)

if __name__ == "__main__":
    main() 