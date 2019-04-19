import io, os
import argparse
from google.cloud import vision
from google.cloud.vision import types

def labelDetection(file_name):
    # Instantiates a client
    client = vision.ImageAnnotatorClient()

    # The name of the image file to annotate
    file_name = os.path.join(os.path.dirname(__file__), file_name)

    # Loads the image into memory
    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)

    # Performs label detection on the image file
    response = client.label_detection(image=image)
    labels = response.label_annotations

    print('Labels:')
    for label in labels:
        print(label.description + " = " + str(int(label.score*100)) + "%")

def check_valid_argument(arg_val):
    """
    check validation
    """
    if not os.path.exists(arg_val.source):
        print("Can't find", arg_val.source)
        return False
    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Image Label Detection Program')
    parser.add_argument('-source', type=str, required=True, default=os.getcwd(),
                        help='Appoint the source folder or file path')
    parser.add_argument('-lang', type=str, default='en-US',
                        help='Label Lenguage Type')
    args = parser.parse_args()
    source_file = args.source

    if check_valid_argument(args):
        labelDetection(source_file)
