import cv2
import argparse
import numpy as np
import os

# Define the argument parser
parser = argparse.ArgumentParser()
parser.add_argument('--input', help='Path to input image')
parser.add_argument('--output', help='Path to save the output image')
args = parser.parse_args()

input_image_path = args.input
output_image_path = args.output


yolo_config_path = 'models/yolo/yolov3.cfg'
yolo_weights_path = 'models/yolo/yolov3.weights'
class_names_path = 'models/yolo/yolov3.txt'



# Define a function to get the output layer names of the YOLO network
def get_output_layers(net):
     layer_names = net.getLayerNames()
     try:
         output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
     except:
         output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

     return output_layers

# Define a function to draw bounding boxes around detected objects
def draw_prediction(img, class_id, confidence, x, y, x_plus_w, y_plus_h):
     label = str(classes[class_id])
     color = COLORS[class_id]
     cv2.rectangle(img, (x,y), (x_plus_w,y_plus_h), color, 2)
     cv2.putText(img, label, (x-10,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

# Load input image
image = cv2.imread(input_image_path)

Width = image.shape[1]
Height = image.shape[0]
scale = 0.00392

# Load class names
classes = None
with open(class_names_path, 'r') as f:
     classes = [line.strip() for line in f.readlines()]

# Generate random colors for each class
COLORS = np.random.uniform(0, 255, size=(len(classes), 3))

# Load YOLO network
net = cv2.dnn.readNet(yolo_weights_path, yolo_config_path)

# Generate input blob for the YOLO network
blob = cv2.dnn.blobFromImage(image, scale, (416,416), (0,0,0), True, crop=False)

# Set input blob for the YOLO network and run forward pass
net.setInput(blob)
outs = net.forward(get_output_layers(net))

# Initialize lists to store detected object information
class_ids = []
confidences = []
boxes = []

conf_threshold = 0.5
nms_threshold = 0.4

# Extract information about detected objects from the output of the YOLO network
for out in outs:
     for detection in out:
         scores = detection[5:]
         class_id = np.argmax(scores)
         confidence = scores[class_id]
         if confidence > 0.5:
             center_x = int(detection[0] * Width)
             center_y = int(detection[1] * Height)
             w = int(detection[2] * Width)
             h = int(detection[3] * Height)
             x = center_x - w/2
             y = center_y - h/2
             class_ids.append(class_id)
             confidences.append(float(confidence))
             boxes.append([x, y, w, h])

# Apply non-maximum suppression to eliminate overlapping bounding boxes
indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

# Draw bounding boxes on the image
for i in indices:
    try:
        box = boxes[i]
    except:
        i = i[0]
        box = boxes[i]

    x = box[0]
    y = box[1]
    w = box[2]
    h = box[3]
    draw_prediction(image, class_ids[i], confidences[i], round(x), round(y), round(x+w), round(y+h))

# Display the image and save it
cv2.imshow("Object recognition", image)
cv2.imwrite("Output/Object recognition.jpg", image)

# Wait for 'esc' key or window close to break the loop
while True:
    if cv2.waitKey(1) & 0xFF == 27 or cv2.getWindowProperty("Object recognition", cv2.WND_PROP_VISIBLE) < 1:
        break

cv2.destroyAllWindows()
