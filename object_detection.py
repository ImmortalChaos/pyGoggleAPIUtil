import io, os
import argparse
from google.cloud import vision

def localizeObjects(file_name):
    # Instantiates a client
    client = vision.ImageAnnotatorClient()

    # The name of the image file to annotate
    file_name = os.path.join(os.path.dirname(__file__), file_name)

    # Loads the image into memory
    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    # Performs label detection on the image file
    response = client.object_localization(image=image)
    objects = response.localized_object_annotations

    print('Number of objects found: {}'.format(len(objects)))
    for object_ in objects:
        print('\n{} (confidence: {})'.format(object_.name, object_.score))
        print('Normalized bounding polygon vertices: ')
        for vertex in object_.bounding_poly.normalized_vertices:
            print(' - ({}, {})'.format(vertex.x, vertex.y))

def check_valid_argument(arg_val):
    """
    check validation
    """
    if not os.path.exists(arg_val.source):
        print("Can't find", arg_val.source)
        return False
    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Localize objects int the Image')
    parser.add_argument('-source', type=str, required=True, default=os.getcwd(),
                        help='Appoint the source folder or file path')
    parser.add_argument('-lang', type=str, default='en-US',
                        help='Object Labels Lenguage Type')
    args = parser.parse_args()
    source_file = args.source

    if check_valid_argument(args):
        localizeObjects(source_file)
