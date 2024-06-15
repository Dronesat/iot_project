import sys
import cv2
from cvzone import FaceDetectionModule
import time
import warnings

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

def run_face_detection(confidence_threadshold = 91):
    detector = FaceDetectionModule.FaceDetector()
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    cap.set(cv2.CAP_PROP_FPS, 10)

    if not cap.isOpened():
        print("Error: Could not open USB camera")
        return

    timeout = 20
    start_time = time.time()
    isFace = None
    confidence = None  

    while time.time() - start_time < timeout:
        success, frame = cap.read()
        if not success:
            print("Error: Could not read frame from USB camera")
            continue

        frame, faces = detector.findFaces(frame, draw=True)

        if faces:
            confidence = round(faces[0]['score'][0] * 100, 1)
            if confidence >= confidence_threadshold:
                isFace = 'yes'
                break
            else: isFace = 'no'
            
        else:
            isFace = 'no'

        dynamic_print(f"Face detected: {isFace} (Time elapsed: {time.time() - start_time:.1f} seconds)")
        cv2.imshow("Face Detection", frame)
        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return isFace, confidence

def dynamic_print(input):
    output_text = f"{input}   "
    sys.stdout.write("\r" + output_text)
    sys.stdout.flush()

if __name__ == "__main__":
    result, confidence = run_face_detection()
    if result is not None:
        print(f"\nFinal result: Face detected: {result}")
        if confidence is not None:
            print(f"Confidence: {confidence:.1f}%")
