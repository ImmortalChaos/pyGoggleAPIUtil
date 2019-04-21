import io, os
import argparse
from google.cloud import vision
from PIL import Image, ImageDraw

def face_detection(file_name):
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
    print(faces)
    print('Faces:')
    for face in faces:
        print('anger: {}'.format(likelihood_name[face.anger_likelihood]))
        print('joy: {}'.format(likelihood_name[face.joy_likelihood]))
        print('surprise: {}'.format(likelihood_name[face.surprise_likelihood]))

        vertices = (['({},{})'.format(vertex.x, vertex.y)
                    for vertex in face.bounding_poly.vertices])

        print('face bounds: {}'.format(','.join(vertices)))

    return faces

def get_filename(img_path):
    """
    get filename from image path
    """
    filename = os.path.splitext(img_path)
    return os.path.basename(filename[0])

def getLandmark(face, tid):
	for landmark in face.landmarks:
		if landmark.type == tid :
			return landmark.position
	return None

def drawFaceLine(draw, face, pt1, pt2):
	pt1Info = getLandmark(face, pt1)
	pt2Info = getLandmark(face, pt2)
	if pt1Info is None or pt2Info is None:
		return

	draw.line([(pt1Info.x, pt1Info.y), (pt2Info.x, pt2Info.y)], fill='#00ff00', width=2)


def drawFacePoint(draw, face):
	'''
	Reference : https://cloud.google.com/vision/docs/reference/rest/v1/images/annotate
	enumStr = ["UNKNOWN", "LEFT_EYE", "RIGHT_EYE", "LEFT_OF_LEFT_EYEBROW", "RIGHT_OF_LEFT_EYEBROW", "LEFT_OF_RIGHT_EYEBROW",
	           "RIGHT_OF_RIGHT_EYEBROW", "MIDPOINT_BETWEEN_EYES", "NOSE_TIP", "UPPER_LIP", "LOWER_LIP",
	           "MOUTH_LEFT", "MOUTH_RIGHT", "MOUTH_CENTER", "NOSE_BOTTOM_RIGHT", "NOSE_BOTTOM_LEFT",
	           "NOSE_BOTTOM_CENTER", "LEFT_EYE_TOP_BOUNDARY", "LEFT_EYE_RIGHT_CORNER", "LEFT_EYE_BOTTOM_BOUNDARY", "LEFT_EYE_LEFT_CORNER",
	           "RIGHT_EYE_TOP_BOUNDARY", "RIGHT_EYE_RIGHT_CORNER", "RIGHT_EYE_BOTTOM_BOUNDARY", "RIGHT_EYE_LEFT_CORNER", "LEFT_EYEBROW_UPPER_MIDPOINT",
	           "RIGHT_EYEBROW_UPPER_MIDPOINT", "LEFT_EAR_TRAGION", "RIGHT_EAR_TRAGION", "LEFT_EYE_PUPIL", "RIGHT_EYE_PUPIL",
	           "FOREHEAD_GLABELLA", "CHIN_GNATHION", "CHIN_LEFT_GONION", "CHIN_RIGHT_GONION",
	           "X", "X", "X", "X", "X", "X", "X"]
	'''
	colStr = ["#ff0000", "#00ff00", "#0000ff", "#ffff00", "#00ffff", "#000000"]
	lineInfos = [(32, 33), (27, 33), (27, 3), (3, 25), (25, 4), (4, 31), (31, 5), (4, 7), (5, 7), (5, 26), (26, 6), (6, 28),
	             (28, 34), (34, 32), (7, 8), (15, 8), (14, 8), (15, 16), (14, 16), (8, 16), (7, 15), (7, 14),
	             (11, 9), (9, 12), (11, 13), (13, 12), (11, 10), (10, 12),
	             (20, 17), (17, 18), (20, 19), (19, 18), (24, 21), (21, 22), (24, 23), (23, 22)]
	index = 0
	for landmark in face.landmarks:
		draw.point([landmark.position.x, landmark.position.y], fill='#ff0000')
		draw.text((landmark.position.x, landmark.position.y-16), str(landmark.type), fill=colStr[index%6])
		index+=1
	print("Total landmark :" + str(index))
	for ln in lineInfos:
		drawFaceLine(draw, face, ln[0], ln[1])

def drawFaceMark(draw, face):
	box = [(vertex. x, vertex.y)
	       for vertex in face.bounding_poly.vertices]
	draw.line(box + [box[0]], width=3, fill='#00ff00')

	draw.text(((face.bounding_poly.vertices)[0].x,
		       (face.bounding_poly.vertices)[0].y - 30),
	           str(format(face.detection_confidence, '.3f')) + '%',
	           fill='#FF0000')

	box = [(vertex. x, vertex.y)
	       for vertex in face.fd_bounding_poly.vertices]
	draw.line(box + [box[0]], width=2, fill='#33ff33')

	drawFacePoint(draw, face)

def cropFace(img, face, file_name, target_path, index_face):
    filename = get_filename(file_name)
    target_filepath = os.path.join(target_path, filename+"_"+str(index_face)+".png")
    print(target_filepath)
    area = (face.bounding_poly.vertices[0].x, face.bounding_poly.vertices[0].y, face.bounding_poly.vertices[2].x, face.bounding_poly.vertices[2].y)
    cropped_img = img.crop(area)
    cropped_img.save(target_filepath)

def save_image(file_name, faces, target_path, show_marking, crop_face):
    img = Image.open(file_name)
    draw = ImageDraw.Draw(img)
    index_face = 0

    for face in faces:
        if show_marking is True:
            drawFaceMark(draw, face)
        if crop_face is True:
            index_face += 1
            cropFace(img, face, file_name, target_path, index_face)

    if show_marking is True and crop_face is False:
        img.save(target_path)

def detect_images(folder_path, show_marking, crop_face, target_path):
    """
    detection from sub-folders
    """
    for (paths, dirs, files) in os.walk(folder_path):
        for filename in files:
            ext = os.path.splitext(filename)[-1]
            if ext in ('.png', '.jpg'):
                detect_path = os.path.join(paths, filename)
                faces = face_detection(detect_path, show_marking, crop_face, target_path)
                save_image(detect_path, faces, target_path, show_marking, crop_face)
                if len(faces)== 0:
                    print(detect_path + "(detection fail!)")

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
    parser.add_argument('-target', type=str, default=None, help='Appoint the target folder')
    parser.add_argument('-show_marking', default=False, action='store_true',
                        help='Displays the found area.')
    parser.add_argument('-crop_face', default=False, action='store_true',
                        help='Saves the detected face area as an image.')
    args = parser.parse_args()
    source_file = args.source

    if check_valid_argument(args):
        if os.path.isdir(source_file):
            detect_images(source_file, args.show_marking, args.crop_face, args.target)
        else:
            faces = face_detection(source_file)
            save_image(source_file, faces, args.target, args.show_marking, args.crop_face)
