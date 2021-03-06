import tensorflow as tf
import cv2 as cv

# Read the graph.
with tf.gfile.FastGFile('models/frozen_inference_graph.pb', 'rb') as f:
    graph_def = tf.GraphDef()
    graph_def.ParseFromString(f.read())

with tf.Session() as sess:
    # Restore session
    sess.graph.as_default()
    tf.import_graph_def(graph_def, name='')

    cap = cv.VideoCapture('http://192.168.2.200:8080/stream/video.mjpeg')

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        if ret:
            # Read and preprocess an image.
            rows = frame.shape[0]
            cols = frame.shape[1]
            inp = cv.resize(frame, (300, 300))
            inp = inp[:, :, [2, 1, 0]]  # BGR2RGB

            # Run the model
            out = sess.run([sess.graph.get_tensor_by_name('num_detections:0'),
                            sess.graph.get_tensor_by_name('detection_scores:0'),
                            sess.graph.get_tensor_by_name('detection_boxes:0'),
                            sess.graph.get_tensor_by_name('detection_classes:0')],
                           feed_dict={'image_tensor:0': inp.reshape(1, inp.shape[0], inp.shape[1], 3)})

            # Visualize detected bounding boxes.
            num_detections = int(out[0][0])
            for i in range(num_detections):
                classId = int(out[3][0][i])
                score = float(out[1][0][i])
                bbox = [float(v) for v in out[2][0][i]]
                if score > 0.5:
                    x = bbox[1] * cols
                    y = bbox[0] * rows
                    right = bbox[3] * cols
                    bottom = bbox[2] * rows
                    cv.rectangle(frame, (int(x), int(y)), (int(right), int(bottom)), (125, 255, 51), thickness=3)

                    if classId == 1:
                        middle_point_X = x + (right - x) / 2
                        middle_point_Y = y + (bottom - y) / 2
                        # print center point of ball
                        # print('Middle point: X:{}, Y{}'.format(middle_point_X, middle_point_Y))
                        if middle_point_X < cols / 2 and middle_point_Y < rows / 2:
                            print('Upper Left')
                        elif middle_point_X >= cols / 2 and middle_point_Y < rows / 2:
                            print('Upper Right')
                        elif middle_point_X < cols / 2 and middle_point_Y >= rows / 2:
                            print('Lower Left')
                        elif middle_point_X >= cols / 2 and middle_point_Y >= rows / 2:
                            print('Lower Right')

            cv.imshow('frame', frame)
            if cv.waitKey(1) & 0xFF == ord('q'):
                break

# When everything done, release the capture
cap.release()
cv.destroyAllWindows()