import sys
import time
import os
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.framework.formats import landmark_pb2
from dataclasses import dataclass

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

@dataclass
class GestureResult:
    hand_gesture_name: str 
    score: float 

class HandGestureRecognition:
    def __init__(self, model: str = 'hand_gesture_model.task', num_hands: int = 1,
                 min_hand_detection_confidence: float = 0.5,
                 min_hand_presence_confidence: float = 0.5, min_tracking_confidence: float = 0.5,
                 camera_id: int = 0, width: int = 640, height: int = 480,
                 stop_on_gesture: bool = True, timeout: int = 20):
        """Initialize the gesture recognition with given parameters."""
        self.model = model
        self.num_hands = num_hands
        self.min_hand_detection_confidence = min_hand_detection_confidence
        self.min_hand_presence_confidence = min_hand_presence_confidence
        self.min_tracking_confidence = min_tracking_confidence
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.stop_on_gesture = stop_on_gesture
        self.timeout = timeout  # Timeout for the gesture recognition

        self.gesture_result = None
        self.recognition_result_list = []
        self.recognition_frame = None
        self.stop_flag = False  # Flag to stop the main loop
        self.counter = 0
        self.FPS = 0
        self.start_time = time.time()
        self.setup_model()

    def setup_model(self):
        """Setup the gesture recognizer model."""
        model_path = os.path.abspath(self.model)
        print("Model path:", model_path)
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}")

        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.GestureRecognizerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.LIVE_STREAM,
            num_hands=self.num_hands,
            min_hand_detection_confidence=self.min_hand_detection_confidence,
            min_hand_presence_confidence=self.min_hand_presence_confidence,
            min_tracking_confidence=self.min_tracking_confidence,
            result_callback=self.save_result
        )
        self.recognizer = vision.GestureRecognizer.create_from_options(options)

    def save_result(self, result: vision.GestureRecognizerResult,
                    unused_output_image: mp.Image, timestamp_ms: int):
        """Callback to save the recognition result."""
        if self.counter % 10 == 0:
            self.fps = 10 / (time.time() - self.start_time)
            self.start_time = time.time()

        self.recognition_result_list.append(result)
        self.counter += 1

    def run(self):
        """Continuously run inference on images acquired from the camera."""
        start_time = time.time()  # Start time for timeout
        cap = cv2.VideoCapture(self.camera_id)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        while cap.isOpened() and not self.stop_flag:
            if self.stop_on_gesture and (time.time() - start_time) > self.timeout:
                print("Timeout reached, no gesture detected.")
                self.gesture_result = GestureResult("timeout", None)
                break

            success, image = cap.read()
            if not success:
                sys.exit(
                    'ERROR: Unable to read from webcam. Please verify your webcam settings.'
                )

            image = cv2.flip(image, 1)
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
            self.recognizer.recognize_async(mp_image, time.time_ns() // 1_000_000)

            fps_text = f'FPS = {self.FPS:.1f}'
            timeout_text = f'Timeout: {self.timeout}s'
            elaped_text = f'Elapsed: {time.time() - start_time:.1f}s'
            cv2.putText(image, fps_text, (15, 50), cv2.FONT_HERSHEY_DUPLEX,
                        1, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(image, timeout_text, (15, 80), cv2.FONT_HERSHEY_DUPLEX,
                        1, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(image, elaped_text, (15, 110), cv2.FONT_HERSHEY_DUPLEX,
                        1, (0, 0, 0), 1, cv2.LINE_AA)
            

            if self.recognition_result_list:
                self.process_results(image)

            if self.recognition_frame is not None:
                cv2.imshow('gesture_recognition', self.recognition_frame)

            if cv2.waitKey(1) == 27:
                break

        self.recognizer.close()
        cap.release()
        cv2.destroyAllWindows()
        return self.gesture_result

    def process_results(self, current_frame):
        """Process the recognition results and draw landmarks and text."""
        hand_gesture_list = ['thumbs_up', 'one', 'two', 'three', 'four']

        for hand_index, hand_landmarks in enumerate(self.recognition_result_list[0].hand_landmarks):
            x_min = min([landmark.x for landmark in hand_landmarks])
            y_min = min([landmark.y for landmark in hand_landmarks])
            y_max = max([landmark.y for landmark in hand_landmarks])

            frame_height, frame_width = current_frame.shape[:2]
            x_min_px = int(x_min * frame_width)
            y_min_px = int(y_min * frame_height)
            y_max_px = int(y_max * frame_height)

            if self.recognition_result_list[0].gestures:
                gesture = self.recognition_result_list[0].gestures[hand_index]
                hand_gesture_name = gesture[0].category_name
                score = round(gesture[0].score, 2)
                result_text = f'{hand_gesture_name} ({score})'
                print(f'{hand_gesture_name}({score})')

                if self.stop_on_gesture and hand_gesture_name in hand_gesture_list:
                    self.stop_flag = True  # Set the flag to stop the main loop
                    self.gesture_result = GestureResult(hand_gesture_name, score)
                    break

                text_size = cv2.getTextSize(result_text, cv2.FONT_HERSHEY_DUPLEX, 1, 2)[0]
                text_width, text_height = text_size
                text_x = x_min_px
                text_y = y_min_px - 10

                if text_y < 0:
                    text_y = y_max_px + text_height

                cv2.putText(current_frame, result_text, (text_x, text_y),
                            cv2.FONT_HERSHEY_DUPLEX, 1,
                            (255, 255, 255), 2, cv2.LINE_AA)

            hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
            hand_landmarks_proto.landmark.extend([
                landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z)
                for landmark in hand_landmarks
            ])
            mp_drawing.draw_landmarks(
                current_frame,
                hand_landmarks_proto,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style()
            )

        self.recognition_frame = current_frame
        self.recognition_result_list.clear()

if __name__ == '__main__':
    gesture_recognition = HandGestureRecognition(stop_on_gesture=False)
    results = gesture_recognition.run()
    print("Results:", results)
