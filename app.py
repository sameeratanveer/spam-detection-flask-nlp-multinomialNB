# Import necessary libraries
import os  # Used for file handling (path operations)
from flask import Flask, request, render_template, send_file  # Flask components for web framework
import pandas as pd  # Used for reading and processing CSV/XLSX files
from predictspam import PredictSpam  # Importing the PredictSpam class that performs the spam detection

# Initialize the Flask app
app = Flask(__name__)

# Define the folder where uploaded files will be stored temporarily
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # Configuring the upload folder in the app

# Route to serve the homepage
@app.route('/')
def index():
    # Renders the homepage HTML file (index.html)
    return render_template('index.html')

# Route for predicting whether the given message is spam or not
@app.route('/predict', methods=['POST'])
def predict():
    if 'message' in request.form:
        # Handle single message input via form (POST request)
        message = request.form['message']  # Get the message from the form

        # Create an instance of PredictSpam with the input message
        detector = PredictSpam(message)
        
        # Predict whether the message is spam or not
        result = detector.predict()
        
        # For debugging purposes, print out the message and the result
        print(f"Message: {message} | Prediction: {result}")
        
        # Render the result on a separate page (result.html), passing the message and prediction result
        return render_template('result.html', message=message, result=result)

    elif 'file' in request.files:
        # Handle file upload (either CSV or XLSX)
        file = request.files['file']  # Get the uploaded file
        filename = file.filename.lower()  # Get the file name in lowercase to check file type

        # Check if the file is in CSV format
        if filename.endswith('.csv'):
            # Save the CSV file to the 'uploads' folder
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

            # Read the CSV file into a pandas DataFrame
            df = pd.read_csv(file_path)

        # Check if the file is in XLSX format
        elif filename.endswith('.xlsx'):
            # Save the XLSX file to the 'uploads' folder
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

            # Read the XLSX file into a pandas DataFrame
            df = pd.read_excel(file_path)

        else:
            # Return an error message if the file is neither CSV nor XLSX
            return "Invalid file type. Please upload a .csv or .xlsx file."

        # Remove any leading or trailing spaces from column names to avoid issues
        df.columns = df.columns.str.strip()

        # Print the column names for debugging (useful to check if 'message' column exists)
        print("Columns in the uploaded file:", df.columns)

        # Check if the 'message' column exists in the uploaded file
        if 'message' not in df.columns:
            # Return an error message if 'message' column is missing
            return "The uploaded file does not contain a 'message' column."

        # Loop through the 'message' column and apply the PredictSpam class to predict spam status for each message
        df['prediction'] = df['message'].apply(lambda msg: PredictSpam(msg).predict())

        # Create a new DataFrame with only the 'message' and 'prediction' columns
        result_df = df[['message', 'prediction']]

        # Save the results as a new CSV file
        result_file = 'result_' + file.filename  # Creating a new filename for the result file
        result_path = os.path.join(app.config['UPLOAD_FOLDER'], result_file)
        result_df.to_csv(result_path, index=False)  # Save the result DataFrame to a CSV file

        # Convert the result DataFrame into an HTML table for rendering in the template
        result_html_table = result_df.to_html(classes='table table-bordered table-striped', index=False)

        # Render the result page (result.html), passing the HTML table and result file path for download
        return render_template('result.html', result_html_table=result_html_table, result_file=result_path)

    # Return an error message if neither 'message' nor 'file' is provided
    return "Invalid input"

# Route to handle downloading the result file
@app.route('/download/<filename>')
def download(filename):
    # Construct the full path to the result file stored in the 'uploads' folder
    result_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Send the result file to the client for downloading
    return send_file(result_path, as_attachment=True)

# Main entry point to run the Flask app
if __name__ == '__main__':
    # Ensure that the 'uploads' folder exists. If not, create it.
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    # Run the Flask app in debug mode for development purposes
    app.run(debug=True)
