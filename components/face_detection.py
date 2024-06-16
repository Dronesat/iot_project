import sys
import cv2
from cvzone import FaceDetectionModule
import time
import warnings
from .oled_display import OLEDDisplay

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

class FaceDetection:
    def __init__(self, confidence_threshold=90, timeout=20, width=320, height=240, fps=10):
        """
        Initialise the FaceDetection object with given parameters.
        
        :param confidence_threshold: Confidence threshold for face detection %.
        :param timeout: Timeout for the face detection process (seconds).
        :param width: Width of the video frame.
        :param height: Height of the video frame.
        :param fps: Frames per second for the video capture.
        """
        self.confidence_threshold = confidence_threshold
        self.timeout = timeout
        self.width = width
        self.height = height
        self.fps = fps
        self.detector = FaceDetectionModule.FaceDetector()
        self.oled_display = OLEDDisplay()

    def run_detection(self):
        """
        Run the face detection process.
        
        :return: Tuple containing face detection result ('yes' or 'no') and confidence %.
        """
        cap = cv2.VideoCapture(0)  # Initialize the camera
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        cap.set(cv2.CAP_PROP_FPS, self.fps)

        if not cap.isOpened():
            print("Error: Could not open USB camera")
            return None, 0.0

        start_time = time.time()
        is_face = None
        confidence = 0.0

        try:
            while time.time() - start_time < self.timeout:
                success, frame = cap.read()
                if not success:
                    print("Error: Could not read frame from USB camera")
                    continue

                frame, faces = self.detector.findFaces(frame, draw=True)

                if faces:
                    confidence = round(faces[0]['score'][0] * 100, 1)
                    if confidence >= self.confidence_threshold:
                        is_face = 'yes'
                        break
                    else:
                        is_face = 'no'
                else:
                    is_face = 'no'

                # Update display and print status every second
                elapsed_time = time.time() - start_time
                if int(elapsed_time) % 1 == 0:
                    self.dynamic_print(f"Detecting time elapsed: {elapsed_time:.1f} seconds")
                    self.oled_display.update_display(f"Detecting Faces", f"Timeout: {self.timeout}s", f"Elapsed: {elapsed_time:.1f}s")

                cv2.imshow("Face Detection", frame)
                if cv2.waitKey(1) == ord('q'):
                    break

        finally:
            cap.release()  # Release the camera
            cv2.destroyAllWindows() # Close program

        return is_face, confidence

    @staticmethod
    def dynamic_print(message):
        output_text = f"{message}   "
        sys.stdout.write("\r" + output_text)
        sys.stdout.flush()

if __name__ == "__main__":
    face_detection = FaceDetection()
    result, confidence = face_detection.run_detection()
    if result is not None:
        print(f"\nFinal result: Face detected: {result}")
        if confidence is not None:
            print(f"Confidence: {confidence:.1f}%")
