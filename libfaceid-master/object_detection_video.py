import cv2
import argparse
import numpy as np
import os

parser = argparse.ArgumentParser()
parser.add_argument('--input', help='Path to input image')
parser.add_argument('--output', help='Path to save the output image')
args = parser.parse_args()

input_video_path = args.input
output_video_path = args.output

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
    cv2.rectangle(img, (x, y), (x_plus_w, y_plus_h), color, 2)
    cv2.putText(img, label, (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)


# Load input video
cap = cv2.VideoCapture(input_video_path)

# Define scale for the input image
scale = 1/255.0

Width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
Height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

# Create output video writer
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(output_video_path, fourcc, fps, (Width, Height))

# Load class names
classes = None
with open(class_names_path, 'r') as f:
    classes = [line.strip() for line in f.readlines()]

# Generate random colors for each class
COLORS = np.random.uniform(0, 255, size=(len(classes), 3))

# Load YOLO network
net = cv2.dnn.readNetFromDarknet(yolo_config_path, yolo_weights_path)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

# Initialize the video stream
video = cv2.VideoCapture(input_video_path)

# Get the video dimensions
frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Define the output video writer
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
output_video_path = "Output/output_video.mp4"
video_writer = cv2.VideoWriter(output_video_path, fourcc, 30, (frame_width, frame_height))

# Start processing the video frame by frame
while True:
    ret, frame = video.read()

    # If there are no more frames, break out of the loop
    if not ret:
        break

    # Get the current frame dimensions
    frame_height, frame_width, _ = frame.shape

    # Generate input blob for the YOLO network
    blob = cv2.dnn.blobFromImage(frame, scale, (416, 416), (0, 0, 0), True, crop=False)

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
            if confidence > conf_threshold:
                center_x = int(detection[0] * frame_width)
                center_y = int(detection[1] * frame_height)
                w = int(detection[2] * frame_width)
                h = int(detection[3] * frame_height)
                x = center_x - w / 2
                y = center_y - h / 2
                class_ids.append(class_id)
                confidences.append(float(confidence))
                boxes.append([x, y, w, h])

    # Apply non-maximum suppression to eliminate overlapping bounding boxes
    indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

    # Draw bounding boxes around detected objects
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
        draw_prediction(frame, class_ids[i], confidences[i], round(x), round(y), round(x + w), round(y + h))

    # Write the processed frame to the output video
    video_writer.write(frame)

    # Display the processed frame
    cv2.imshow("Object recognition (Video)", frame)

    key = cv2.waitKey(10)
    if key == 27:  # ASCII code for ESC
        break

# Release the video stream and video writer resources
video.release()
video_writer.release()
cv2.destroyAllWindows()

# Release the video stream and video writer resources
video.release()
video_writer.release()
cv2.destroyAllWindows()