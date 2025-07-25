# Work flow.
# Import necessary Library.
# Create model or model class.
# then create class inside this class
        # text preprocessing (Apply nlp model)
        # data extraction or load.
        # Model training
        # save model
        # load model
# finally main chat block and in this laod all for process user input.
    # finally run a loop so we can chat continuously.




import os
import json
import random
import nltk
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from nltk.lm import vocabulary
from torch.utils.data import DataLoader, TensorDataset



nltk.data.path.append(r"C:\Users\BKJST\Desktop\python\Project\Chatbot\first chatbot\.venv\nltk_data")
nltk.download('punkt_tab', download_dir=r"C:\Users\BKJST\Desktop\python\Project\Chatbot\first chatbot\.venv\nltk_data")

#-----------------Create Model------------------##
class ChatbotModel(nn.Module):
    def __init__(self, input_size, output_size):
        super(ChatbotModel, self).__init__()

        self.fc1 = nn.Linear(input_size, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, output_size)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.5)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.fc2(x)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.fc3(x)
        return x

# -----------------Train assistant with data ---------------##
#####--- This part including Data preprocessing-> NLP-> BoW, tokenize/vectorization-> Text to Machine understandale language.
class ChatbotAssitant:
    def __init__(self, intents_path, function_mappings= None):
        self.model = None
        self.intents_path = intents_path

        self.documents = []
        self.vocabulary = []
        self.intents = []
        self.intents_responses = {}

        self.function_mappings = function_mappings

        self.X = None
        self.y = None

    # ------Tokenize word----#
    # -- breakdown into single word.---#
    #----convert into Verb1 form or its original form---##
    @staticmethod
    def tokenize_and_lemmatize(text):
        lemmatizer = nltk.WordNetLemmatizer()
        words = nltk.word_tokenize(text)

        words = [lemmatizer.lemmatize(word.lower()) for word in words]
        return words


    #----------Text Classification----------#
    def bag_of_words(self, words):
        return [1 if word in words else 0 for word in self.vocabulary]



# -----Load training data in json format---------#
    def parse_intents(self):
        lemmatizer = nltk.WordNetLemmatizer()

        if os.path.exists(self.intents_path):
            with open(self.intents_path, 'r') as f:
                intents_data = json.load(f)


            for intent in intents_data['intents']:
                if intent['tag'] not in self.intents:
                    self.intents.append(intent['tag'])
                    self.intents_responses[intent['tag']] = intent['responses']


                for pattern in intent['patterns']:
                    pattern_words = self.tokenize_and_lemmatize(pattern)
                    self.vocabulary.extend(pattern_words)
                    self.documents.append((pattern_words, intent['tag']))

                vocabulary = sorted(set(self.vocabulary))



##----------- on loaded data apply function and preprocess--------###
    def prepare_data(self):
        bags = []
        indices = []
        for document in self.documents:
            words = document[0]
            bag = self.bag_of_words(words)


            intent_index = self.intents.index(document[1])

            bags.append(bag)
            indices.append(intent_index)

        self.X = np.array(bags)
        self.y = np.array(indices)



    # _______ Model Training__________#
    def train_model(self, batch_size, lr, epochs):
        X_tensor = torch.tensor(self.X, dtype=torch.float32)
        y_tensor = torch.tensor(self.y, dtype= torch.long)

        dataset = TensorDataset(X_tensor, y_tensor)
        loader = DataLoader(dataset, batch_size = batch_size)

        self.model = ChatbotModel(self.X.shape[1], len(self.intents))
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(self.model.parameters(), lr = lr)

        for epoch in range(epochs):
            running_loss = 0.0


            for X_batch, y_batch in loader:
                optimizer.zero_grad()
                outputs = self.model(X_batch)
                loss = criterion(outputs, y_batch)
                loss.backward()
                optimizer.step()
                print(f'Epoch: {epoch+1}, Loss: {running_loss/ len(loader):.4f}')



## --------------Save and load trained model-------------------###
    def save_model(self, model_path, dimensions_path):
        torch.save(self.model.state_dict(), model_path)

        with open(dimensions_path, 'w') as f:
            json.dump({'input_size': self.X.shape[1], 'output_size': len(self.intents)},f)




    def load_model(self, model_path, dimensions_path):
        with open(dimensions_path, 'r') as f:
            dimensions = json.load(f)

        self.model = ChatbotModel(dimensions['input_size'], dimensions['output_size'])
        self.model.load_state_dict(torch.load(model_path, weights_only = True))



#-------Lets process user input message-----------------##
    def process_message(self, input_message):
        words = self.tokenize_and_lemmatize(input_message)
        bag = self.bag_of_words(words)

        bag_tensor = torch.tensor([bag], dtype =torch.float32)

        self.model.eval()
        with torch.no_grad():
            predictions = self.model(bag_tensor)

        predicted_class_index  = torch.argmax(predictions,dim=1).item()
        predicted_intent = self.intents[predicted_class_index]

        if self.function_mappings:
            if predicted_intent in self.function_mappings:
                self.function_mappings[predicted_intent]()

        if self.intents_responses[predicted_intent]:
            return random.choice(self.intents_responses[predicted_intent])
        else:
            return None

#----------return any 3 stock randomly without repeat--------#
#-----Later i will update price etc---------#
def get_stocks():
    stocks = ['APPL', 'META', 'NVDA', 'GS', 'MSFT']
    print(random.sample(stocks, 3))


# put all together to create main block. chatbot.------------#
if __name__ == '__main__':
    assistant = ChatbotAssitant('intents.json', function_mappings = {'stocks':get_stocks})
    assistant.parse_intents()
    assistant.prepare_data()
    assistant.train_model(batch_size = 8, lr = 0.001, epochs = 100)

    assistant.save_model('chatbot_model.pth', 'dimensions.json')


    # Run a loop. but in streamlit we will use rerun function.
    while True:
        message = input('Enter your message: ')
        if message =='/quit':
            break
        print(assistant.process_message(message))


        




