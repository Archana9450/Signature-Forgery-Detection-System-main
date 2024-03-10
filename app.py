from flask import Flask, render_template, request, jsonify
import os
import tensorflow as tf
import pandas as pd

app = Flask(__name__)

# ... (previous code)

def evaluate(train_path, test_path, type2=False):   
    if not(type2):
        train_input, corr_train, test_input, corr_test = readCSV(train_path, test_path)
    else:
        train_input, corr_train, test_input = readCSV(train_path, test_path, type2)
    ans = 'Random'
    with tf.Session() as sess:
        sess.run(init)
        # Training cycle
        for epoch in range(training_epochs):
            # Run optimization op (backprop) and cost op (to get loss value)
            _, cost = sess.run([train_op, loss_op], feed_dict={X: train_input, Y: corr_train})
            if cost < 0.0001:
                break
        # Finding accuracies
        accuracy1 =  accuracy.eval({X: train_input, Y: corr_train})
        if type2 is False:
            accuracy2 =  accuracy.eval({X: test_input, Y: corr_test})
            return accuracy1, accuracy2
        else:
            prediction = pred.eval({X: test_input})
            if prediction[0][1] > prediction[0][0]:
                print('Genuine Image')
                return True
            else:
                print('Forged Image')
                return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file:
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)

        # Provide the correct paths for train and test
        train_person_id = request.form['person_id']
        train_path = f'Features/Training/training_{train_person_id}.csv'
        test_path = file_path

        result = evaluate_signature(train_path, test_path)

        return jsonify({'result': result})

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)
