import io, os
import argparse
from google.cloud import vision

def faceDetection(file_name):
    # Instantiates a client
    client = vision.ImageAnnotatorClient()

    # Loads the image into memory
    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    # Performs face detection on the image file
    response = client.face_detection(image=image)
    faces = response.face_annotations

    # Names of likelihood from google.cloud.vision.enums
    likelihood_name = ('UNKNOWN', 'VERY_UNLIKELY', 'UNLIKELY', 'POSSIBLE',
                       'LIKELY', 'VERY_LIKELY')
    print('Faces:')
    for face in faces:
        print('anger: {}'.format(likelihood_name[face.anger_likelihood]))
        print('joy: {}'.format(likelihood_name[face.joy_likelihood]))
        print('surprise: {}'.format(likelihood_name[face.surprise_likelihood]))

        vertices = (['({},{})'.format(vertex.x, vertex.y)
                    for vertex in face.bounding_poly.vertices])

        print('face bounds: {}'.format(','.join(vertices)))

def check_valid_argument(arg_val):
    """
    check validation
    """
    if not os.path.exists(arg_val.source):
        print("Can't find", arg_val.source)
        return False
    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Face Detection Program')
    parser.add_argument('-source', type=str, required=True, default=os.getcwd(),
                        help='Appoint the source folder or file path')
    args = parser.parse_args()
    source_file = args.source

    if check_valid_argument(args):
        faceDetection(source_file)
