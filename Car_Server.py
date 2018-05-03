import tensorflow as tf
import cv2 as cv
import paho.mqtt.publish as publish

# Create MQTT client for communication with car
rabitmq_ip = '192.168.2.88'     # ip address of mqtt server
user_auth = {'username': 'client', 'password': '1234'}  # Add user authentication for publish function

# Read the graph.
with tf.gfile.FastGFile('models/frozen_inference_graph_tb.pb', 'rb') as f:
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

            best_match_id = -1
            best_match_prob = 0

            for i in range(num_detections):
                # classId = int(out[3][0][i])
                score = float(out[1][0][i])
                # bbox = [float(v) for v in out[2][0][i]]

                if score > best_match_prob:
                    best_match_id = i
                    best_match_prob = score

                # if score > 0.4:
                #     x = bbox[1] * cols
                #     y = bbox[0] * rows
                #     right = bbox[3] * cols
                #     bottom = bbox[2] * rows
                #     cv.rectangle(frame, (int(x), int(y)), (int(right), int(bottom)), (125, 255, 51), thickness=3)
                #
                #     if classId == 1:
                #         middle_point_X = x + (right - x)/2
                #         print('Mid point: {} center: {}'.format(middle_point_X, cols/2))
                #         if middle_point_X < (cols/2):
                #             offset = -1 * (1 - abs((middle_point_X - cols/2)/(cols/2)))
                #         elif middle_point_X > (cols/2):
                #             offset = abs((middle_point_X - cols) / (cols / 2))
                #         else:
                #             offset = 1
                #         middle_point_Y = y + (bottom - y)/2
                #         # Calculate offset of item center in percents actual point - center (half range) / center
                #         msgs = [{'topic': "demo.key", 'payload': 'x:{}'.format(offset)},
                #                 {'topic': 'demo.key', 'payload': 'y:{}'.format(1-(middle_point_Y - rows/2)/(rows/2))}]
                #         # print center point of ball
                #         # print('Middle point: X:{}, Y{}'.format(middle_point_X, middle_point_Y))
                #         print('Msgs: {}'.format(msgs))
                #         publish.multiple(msgs, rabitmq_ip, auth=user_auth)

            if best_match_id > -1:
                # if we find object in frame get its coordinates and send it to car
                bbox = [float(v) for v in out[2][0][best_match_id]]
                x = bbox[1] * cols
                y = bbox[0] * rows
                right = bbox[3] * cols
                bottom = bbox[2] * rows

                cv.rectangle(frame, (int(x), int(y)), (int(right), int(bottom)), (125, 255, 51), thickness=3)

                middle_point_X = x + (right - x) / 2
                print('Mid point: {} center: {}'.format(middle_point_X, cols / 2))
                if middle_point_X < (cols / 2):
                    offset = -1 * (1 - abs((middle_point_X - cols / 2) / (cols / 2)))
                elif middle_point_X > (cols / 2):
                    offset = abs((middle_point_X - cols) / (cols / 2))
                else:
                    offset = 1
                middle_point_Y = y + (bottom - y) / 2
                # Calculate offset of item center in percents actual point - center (half range) / center
                msgs = [{'topic': "demo.key", 'payload': 'x:{}'.format(offset)},
                        {'topic': 'demo.key', 'payload': 'y:{}'.format(1 - (middle_point_Y - rows / 2) / (rows / 2))}]
                print('Msgs: {}'.format(msgs))
                publish.multiple(msgs, rabitmq_ip, auth=user_auth)
            else:
                # if we don't find and interesting object send -10, -10 to car
                msgs = [{'topic': "demo.key", 'payload': 'x:{}'.format(-10)},
                        {'topic': 'demo.key', 'payload': 'y:{}'.format(-10)}]
                print('Msgs: {}'.format(msgs))
                publish.multiple(msgs, rabitmq_ip, auth=user_auth)

            cv.imshow('frame', frame)
            if cv.waitKey(1) & 0xFF == ord('q'):
                break

# When everything done, release the capture
cap.release()
cv.destroyAllWindows()
