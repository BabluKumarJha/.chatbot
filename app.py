## Due to lack of time many features is missing.
# 1. Chat history maintain.
# 2. Cache maintain.
# 3. User authentication is working but update and delete not working as expected.
# 4. Main issues is authentication. In future we will seperate password or user details in other files.
# 5. Context maintain.
# 6. Due to Lack of data so some time incorrect output.
# 7. This is version 1. So Have issue i am accepting and i will work on it.


import streamlit as st
import os
import json
import random
import nltk
import numpy as np
import torch
import torch.nn as nn

##--------------------- Download punkt-tab for NLP process------------------#
nltk.data.path.append(r"C:\Users\BKJST\Desktop\python\Project\Chatbot\first chatbot\.venv\nltk_data")
nltk.download('punkt_tab', download_dir=r"C:\Users\BKJST\Desktop\python\Project\Chatbot\first chatbot\.venv\nltk_data")

# -------------------- Chatbot Model------------------------###
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
        return x # we can also write this code in simple way.

##-----------------------Chatbot Assistant class-------------------##
class ChatbotAssitant:
    def __init__(self, intents_path, function_mappings=None):
        self.model = None
        self.intents_path = intents_path

        self.documents = []
        self.vocabulary = []
        self.intents = []
        self.intents_responses = {}

        self.function_mappings = function_mappings

        self.X = None
        self.y = None


####-------------------------define function for NLP process------------------###
    # word embedding, word_tokenization, lemmatization, bag of word. all function preprocess text into machine understable form.
    @staticmethod
    def tokenize_and_lemmatize(text):
        lemmatizer = nltk.WordNetLemmatizer()
        words = nltk.word_tokenize(text)

        words = [lemmatizer.lemmatize(word.lower()) for word in words]
        return words

    def bag_of_words(self, words):
        return [1 if word in words else 0 for word in self.vocabulary]

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


    def load_model(self, model_path, dimensions_path):
        with open(dimensions_path, 'r') as f:
            dimensions = json.load(f)

        self.model = ChatbotModel(dimensions['input_size'], dimensions['output_size'])
        self.model.load_state_dict(torch.load(model_path, weights_only=True))

    def process_message(self, input_message):
        words = self.tokenize_and_lemmatize(input_message)
        bag = self.bag_of_words(words)

        bag_tensor = torch.tensor([bag], dtype=torch.float32)

        self.model.eval()
        with torch.no_grad():
            predictions = self.model(bag_tensor)

        predicted_class_index = torch.argmax(predictions, dim=1).item()
        predicted_intent = self.intents[predicted_class_index]

        if self.function_mappings:
            if predicted_intent in self.function_mappings:
                self.function_mappings[predicted_intent]()

        if self.intents_responses[predicted_intent]:
            return random.choice(self.intents_responses[predicted_intent])
        else:
            return None


def get_stocks():
    stocks = ['APPL', 'META', 'NVDA', 'GS', 'MSFT']
    print(random.sample(stocks, 3))



# --- Session Initialization ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False


#######------------ user authentication----------------------#######
## We are creating login system. ##
# Store username and password in dictionary
# This is very bad way to store id password. or id in future i will update and use separate file for user authentication.
# Never use this method for authentication. After press f12 anyone can see all these code including id and password.
# This is my version 1 so i will deploying it as it. No Change.

users = {
        'admin': 'admin',
        'bablu':'bablu',
        'rahul':'rahul'
}


# -------------- Login Function --------------------#
def login(username, password):

    if username in users and password == users[username]:
        st.session_state.username = username
        return "Login successful", username


    else:
        return "Login failed", None

# User Login form for user credentials.
st.write('Note: For testing purpose you can use user id and password admin, admin')
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# ------------ Take username and Password from user.
if not st.session_state.logged_in:
    st.title("🔐 Login to ChatBot")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            status, user = login(username, password)
            if status == "Login successful":
                st.session_state.logged_in = True
                st.success(f"Welcome, {user}!")

            else:
                st.error("Invalid credentials. Try again.")
        st.stop()




# --- Logged In ChatBot UI ---
st.title("💬 ChatBot Assistant")
st.write("You're now logged in. Ask me anything!")


###-----------Start conversation with ai----------------------###
if __name__ == '__main__':
    assistant = ChatbotAssitant('intents.json', function_mappings={'stocks': get_stocks})
    assistant.parse_intents()
    assistant.prepare_data()
    assistant.load_model('chatbot_model.pth', 'dimensions.json')

    # Initialize state
    if 'message' not in st.session_state:
        st.session_state.message = ''

    # Text input box
    message = st.text_input('Enter your message:', value=st.session_state.message, key='chat_input')


    # Check for submitted message
    if message and message != '/quit':
        st.write(assistant.process_message(message))
        st.session_state.message = ''  # Clear after processing
    elif message == '/quit':
        st.stop()



##////////////////////////////////////////////////////////////////\\\\\\\\\\\\\\\\\\\\\\\\
############# -----------Sidebar----------------#######
if "username" in st.session_state:
    st.sidebar.header(f"Welcome {st.session_state.username}")
else:
    st.sidebar.subheader("Welcome, guest")
# --- Logout Button ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = True  # Simulate login for example



# Sidebar with logout option
st.sidebar.subheader("👤 Account")
st.sidebar.write("You're logged in!")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()




##----------------- Delete User Account--------------###
####### Convert username in lower case and all keys of dictionary in lower. so prevent from duplicate.
## Python is case sensitive language.

def del_user(username, password):
    username = username.lower()
    users_keys = {k.lower(): k for k in users}
    if username == 'admin':
        print(f"User {username} can not be deleted.")

    elif (

            "username" in st.session_state and

            st.session_state.username.lower() == username

    ):
        del st.session_state.username

        st.session_state.logged_in = False
        print(f"User {username} deleted successfuly.")

    else:
        print('User not found or invaild user id and password')





with st.sidebar.expander("🗑️ Delete Account"):
    user_del = st.text_input("Username for Deletion", key="del_user")
    pwd_del = st.text_input("Password", type="password", key="del_pwd")
    if st.sidebar.button("Delete"):
        st.sidebar.success(del_user(user_del, pwd_del))
        st.rerun()



###---------------- Change user password-------------------------####


def update_password(username, old_pass, new_pass, confirm_pass):
    username = username.lower()
    users_key = {k.lower(): k for k in users}

    if username not in users_key:
        return f"Invalid username '{username}'"

    original_key = users_key[username]
    if users[original_key] != old_pass:
        return "Incorrect old password."

    if new_pass != confirm_pass:
        return "New password and confirmation do not match."

    users[original_key] = new_pass
    return f"✅ Password updated successfully for '{original_key}'"





# Update Password, Sidebar User interface.
st.sidebar.subheader("🔐 Update Your Password")

with st.sidebar.expander("✏️ Change Password"):
    username_input = st.text_input("Username", key="up_user")
    old_password = st.text_input("Old Password", type="password", key="up_old")
    new_password = st.text_input("New Password", type="password", key="up_new")
    confirm_password = st.text_input("Confirm New Password", type="password", key="up_confirm")

    if st.sidebar.button("Update"):
        result = update_password(username_input, old_password, new_password, confirm_password)
        st.sidebar.success(result)
