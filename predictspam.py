# Import required libraries
import re  # Regular expressions for pattern matching and text manipulation
import joblib  # To load pre-trained models and vectorizers
from nltk.corpus import stopwords  # To filter out common stopwords
from nltk.stem import WordNetLemmatizer  # For lemmatization to reduce words to their base form
from contractions import fix  # To handle contractions like "don't" -> "do not"

class PredictSpam:
    """
    A class to predict if a given message is Spam or Not Spam using NLP preprocessing 
    and a pre-trained spam detection model.

    Attributes:
        message (str): The message input by the user for prediction.
        lemmatizer (WordNetLemmatizer): Lemmatizer object to reduce words to their base form.
        stop_words (set): A set of common English stopwords to be removed during preprocessing.
        spam_words (list): A list of words commonly associated with spam (used for additional feature extraction).
    """
    
    def __init__(self, message):
        """
        Initializes the PredictSpam object with the message input.
        
        Args:
            message (str): The message that needs to be classified as spam or not.
        """
        self.message = message  # Store the message for later processing
        self.lemmatizer = WordNetLemmatizer()  # Initialize the lemmatizer
        self.stop_words = set(stopwords.words('english'))  # Load English stopwords
        self.spam_words = ['winner', 'free', 'claim', 'valid', 'click']  # Words typically associated with spam
    
    def preprocess_message(self):
        """
        Preprocesses the input message by performing several text cleaning operations.
        
        - Converts to lowercase
        - Expands contractions (e.g., "don't" -> "do not")
        - Replaces certain patterns like email addresses, phone numbers, and URLs with placeholders
        - Removes unwanted characters and extra spaces
        - Filters out stopwords and performs lemmatization
        
        Returns:
            str: The preprocessed message ready for model prediction.
        """
        # Convert message to lowercase
        msg = self.message.lower()

        # Fix contractions (e.g., "don't" -> "do not")
        msg = fix(msg)

        # Replace email addresses with a placeholder 'emailaddr'
        msg = re.sub(r'\b[\w\-.]+?@\w+?\.\w{2,4}\b', 'emailaddr', msg)

        # Replace URLs and domain names with placeholder 'httpaddr'
        msg = re.sub(r'(http[s]?\S+)|(\w+\.[A-Za-z]{2,4}\S*)', 'httpaddr', msg)

        # Replace currency symbols (£, $) with a placeholder 'moneysymb'
        msg = re.sub(r'£|\$', 'moneysymb', msg)

        # Replace phone numbers with a placeholder 'phonenumbr'
        msg = re.sub(r'\b(\+\d{1,2}\s)?\d?[\-(.]?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b', 'phonenumbr', msg)

        # Replace numeric values with the placeholder 'numbr'
        msg = re.sub(r'\d+(\.\d+)?', 'numbr', msg)

        # Replace common spam words with the placeholder 'spamword'
        for word in self.spam_words:
            msg = re.sub(fr'\b{word}\b', 'spamword', msg, flags=re.IGNORECASE)

        # Remove any non-alphanumeric characters (e.g., punctuation)
        msg = re.sub(r'[^\w\d\s]', ' ', msg)

        # Replace multiple spaces with a single space and strip leading/trailing spaces
        msg = re.sub(r' +', ' ', msg).strip()

        # Remove stopwords (e.g., 'the', 'and', 'is') from the message
        msg = ' '.join([word for word in msg.split() if word not in self.stop_words])

        # Lemmatize each word in the message (e.g., 'running' -> 'run')
        msg = ' '.join([self.lemmatizer.lemmatize(word) for word in msg.split()])

        return msg  # Return the preprocessed message

    def predict(self):
        """
        Predicts whether the input message is 'Spam' or 'Not Spam'.
        
        The method:
        - Preprocesses the input message
        - Loads the pre-trained spam classification model
        - Loads the pre-trained vectorizer to convert the text into feature vectors
        - Predicts the class ('Spam' or 'Not Spam') based on the model
        
        Returns:
            str: The classification result: either "Spam" or "Not Spam"
        """
        # Preprocess the message
        msg = self.preprocess_message()

        # Load the pre-trained spam detection model (saved as a pickle file)
        model = joblib.load('models/spam_model.pkl')

        # Load the pre-trained vectorizer (saved as a pickle file)
        cv = joblib.load('models/vectorizer.pkl')

        # Transform the preprocessed message into a feature vector
        vector = cv.transform([msg]).toarray()

        # Use the model to predict if the message is spam or not
        prediction = model.predict(vector)

        # Return the prediction result: "Spam" if 1, otherwise "Not Spam"
        return "Spam" if prediction[0] == 1 else "Not Spam"


# Example usage:
# Create an instance of PredictSpam with a sample message
detector = PredictSpam("Hi. I hope you are doing well.. Barre, click this link and get some cash as reward!")

# Predict if the message is spam or not
print(detector.predict())  # Output: "Spam"
