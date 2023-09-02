import torch
from transformers import AutoModelForQuestionAnswering, AutoTokenizer
import pandas as pd
import os

def get_predictions(file_path):
    # Path to the directory where you saved the model and tokenizer
    model_path ='models/name_extractor_model'


    # Load the pretrained model and tokenizer
    model = AutoModelForQuestionAnswering.from_pretrained(model_path)
    tokenizer = AutoTokenizer.from_pretrained(model_path)

    # Move the model to the appropriate device
    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
    model.to(device)

    # Set the model to evaluation mode
    model.eval()

    # Initialize empty lists for storing predictions and ground truths
    start_pred_list = []
    end_pred_list = []
    start_true_list = []
    end_true_list = []
    predicted_answers = []

    model.eval()
    print("Model Loaded")

    # Print the predicted answers along with the true labels
    predicted_answers = []
    input_contexts= list(pd.read_excel(file_path, sheet_name = "raw").loc[:,"full name"])
    questions = ["How do I address him?" for x in range(len(input_contexts))]
    number_of_entries = len(input_contexts)
    # Iterate through input contexts and questions
    print(f"Processing {number_of_entries} entries")

    # Progress
    interval = int(number_of_entries/100) + 1
    


    for index,(context, question) in enumerate(zip(input_contexts, questions)):
        # Encode the input context and question
        inputs = tokenizer(context, question, return_tensors='pt', truncation=True, padding=True)
        inputs.to(device)

        # Make predictions
        with torch.no_grad():
            outputs = model(**inputs)
            start_logits = outputs.start_logits
            end_logits = outputs.end_logits

        # Get the predicted answer span
        start_pos = torch.argmax(start_logits)
        end_pos = torch.argmax(end_logits) + 1  # Adding 1 to include the end position

        # Decode the predicted answer span using the tokenizer
        predicted_answer = tokenizer.decode(inputs['input_ids'][0][start_pos:end_pos], skip_special_tokens=True)
        predicted_answer = predicted_answer.title().strip()
        predicted_answers.append(predicted_answer)
        if index %interval == 0 and index!= 0:
            print(f"Progress is at {int(index/number_of_entries*100)}%")

    print("Processing done, saving to excel")
    temp_df = pd.DataFrame(zip(input_contexts,predicted_answers) , columns=["Full Name" , "Name"])
    parent_directory = os.path.dirname(file_path)  # Get the parent directory of the uploaded file
    output_filename = "predicted.xlsx"  # Output filename
    output_path = os.path.join(parent_directory, "..", "temp", output_filename)  # Construct the output path
    temp_df.to_excel( output_path, index=False)
    return output_path