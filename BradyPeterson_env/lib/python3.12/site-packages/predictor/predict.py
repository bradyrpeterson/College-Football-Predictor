"""
Flask API serving as UI backend or standalone API endpoint serving
scikit-learn models up for prediction.  
"""

import argparse
import boto3
import pickle
import traceback

from flask import Flask, request, jsonify

app = Flask(__name__)

def _split_path(loc):
    """ Split S3 path into bucket and prefix strings """
    bucket = loc.split("s3://")[1].split("/")[0]
    prefix = "/".join(loc.split("s3://")[1].split("/")[1:])
    return bucket, prefix

def load_model(loc):
    """ 
    Load and return pickled model object from S3 or local

    Args:
        loc (str): location of pickled model object file
    Returns:
        unpickled model object
    """
    if "s3" in loc:
        bucket, prefix = _split_path(loc)
        s3 = boto3.resource('s3')
        obj = s3.Object(bucket, prefix)
        body = obj.get()['Body'].read()
        model = pickle.loads(body)
    else:
        with open(loc, "rb") as f:
            model = pickle.load(f)
    return model

# Predictor endpoint
@app.route('/predict', methods = ['GET', 'POST'])
def predict():
    """ Make prediction according to posted data input """

    # parse input data
    if request.method == "POST":
        input = request.get_json(force=True)
    elif request.method == "GET":
        input = request.args
    input = input.to_dict()

    # get prediction method
    if input["method"] == "predict":
        method = model.predict
    elif input["method"] == "predict_proba":
        method = model.predict_proba
    else:
        raise ValueError("Unknown prediction method")   

    # assemble input features
    features = [input[x] for x in model.features] 

    # attempt prediction
    try:
        prediction = method([features])
        status = "SUCCESS"
        tb = None
    except Exception as e:
        prediction = None
        status = "FAILURE"
        tb = traceback.format_exc()

    output = [
        {
         'input': input, 
         'prediction': [list(x) for x in prediction],
         'status': status,
         'traceback': tb
        }
    ]
    return jsonify(results=output)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-loc',
                        dest='model_loc',
                        default=None, 
                        help='location of pickled model object')
    parser.add_argument('--port',
                        dest='port',
                        default='8080',
                        help='port to serve application')
    parser.add_argument('--host',
                        dest='host',
                        default='0.0.0.0',
                        help='host to serve application')
    args = parser.parse_args()
    if not args.model_loc:
        raise Exception("Please supply valid model location argument")
    model = load_model(args.model_loc)
    if not hasattr(model, "features"):
        raise Exception("Model object requires 'features' attribute")
    app.run(
        host=args.host,
        port=int(args.port)
    )

