import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import cv2 as cv

def create_hsv_mask(img, min_area_threshold=200):
    """
    Filter warna HSV dengan threshold area minimum untuk reduce noise
    
    min_area_threshold: Area minimum (pixel) untuk objek yang lolos filtering
    - Nilai kecil (50-200): Deteksi objek kecil, lebih banyak noise
    - Nilai sedang (200-500): Balance antara deteksi dan noise reduction
    - Nilai besar (500+): Hanya objek besar, noise minimal
    """
    imgHSV = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    target_lower_hsv = np.array([0, 70, 6])
    target_upper_hsv = np.array([90, 255, 255])
    mask = cv.inRange(imgHSV, target_lower_hsv, target_upper_hsv)
    
    # Morphological operations untuk membersihkan noise
    kernel = np.ones((3,3), np.uint8)
    mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)
    mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel)
    
    # Area threshold filtering untuk reduce noise
    contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    filtered_mask = np.zeros_like(mask)
    
    for contour in contours:
        area = cv.contourArea(contour)
        if area >= min_area_threshold:
            cv.fillPoly(filtered_mask, [contour], 255)
    
    # Blur untuk deteksi lingkaran yang lebih smooth
    filtered_mask = cv.medianBlur(filtered_mask, 5)
    
    print(f"Area threshold: {min_area_threshold} pixels - Filtered {len(contours)} contours")
    return filtered_mask

def detect_circles(mask, param1=200, param2=14, minDist=1000, minRadius=15, maxRadius=100):
    """
    Deteksi lingkaran dengan parameter yang bisa disesuaikan
    
    Panduan tuning:
    - param2 (12): Threshold center detection. Turunkan jika tidak ada deteksi, naikkan jika terlalu banyak false positive
    - minRadius/maxRadius: Sesuaikan dengan ukuran objek target
    - minDist: Jarak minimum antar lingkaran
    - param1: Threshold edge detection
    
    Preset umum:
    - Objek kecil: param2=8-15, minRadius=3, maxRadius=20
    - Objek sedang: param2=12-20, minRadius=10, maxRadius=50  
    - Objek besar: param2=15-25, minRadius=20, maxRadius=100
    """
    circles = cv.HoughCircles(mask,
                               cv.HOUGH_GRADIENT,
                               dp=1,
                               minDist=minDist,
                               param1=param1,
                               param2=param2,
                               minRadius=minRadius,
                               maxRadius=maxRadius)
    return circles

def hough_transform(image_path):
    root = os.getcwd()
    image_path = os.path.join(root, image_path)
    img = cv.imread(image_path)
    if img is None:
        print(f"Error: Cannot load image {image_path}")
        return
    imgRGB = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    
    # Titik tengah foto
    h, w = imgRGB.shape[:2]
    center_x, center_y = w // 2, h // 2
    
    mask = create_hsv_mask(img, min_area_threshold=200)
    circles = detect_circles(mask)
    
    # Copy untuk plot dengan garis
    imgWithLines = imgRGB.copy()
    
    if circles is not None:
        circles = np.uint16(np.around(circles))
        print(f"Detected {len(circles[0])} small circles")
        print(f"Image center: ({center_x}, {center_y})")
        print("Circle centers (x, y, radius) and distances:")
        
        for i, circle in enumerate(circles[0, :]):
            x, y, r = circle[0], circle[1], circle[2]
            # Hitung jarak dari titik tengah foto
            distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
            print(f"  Circle {i+1}: center=({x}, {y}), radius={r}, distance={distance:.1f} pixels")
            
            # Gambar lingkaran
            cv.circle(imgRGB, (x, y), r, (0, 255, 0), 2)
            cv.circle(imgRGB, (x, y), 2, (255, 0, 0), 2)
            
            # Gambar garis dari center ke lingkaran
            cv.circle(imgWithLines, (x, y), r, (0, 255, 0), 2)
            cv.circle(imgWithLines, (x, y), 2, (255, 0, 0), 2)
            cv.line(imgWithLines, (center_x, center_y), (x, y), (255, 255, 0), 2)
        
        # Gambar titik tengah foto
        cv.circle(imgWithLines, (center_x, center_y), 5, (255, 0, 255), -1)
    else:
        print("No circles detected")
    
    # Tampilkan hasil
    plt.figure(figsize=(16, 4))
    plt.subplot(1, 4, 1)
    plt.imshow(imgRGB)
    plt.title('Original')
    plt.axis('off')
    
    plt.subplot(1, 4, 2)
    plt.imshow(mask, cmap='gray')
    plt.title('HSV Mask')
    plt.axis('off')
    
    plt.subplot(1, 4, 3)
    plt.imshow(imgRGB)
    plt.title('Detected Circles')
    plt.axis('off')
    
    plt.subplot(1, 4, 4)
    plt.imshow(imgWithLines)
    plt.title('Distance Lines')
    plt.axis('off')
    
    plt.tight_layout()
    plt.show()

def hough_camera_stream(camera_id=0):
    """Deteksi lingkaran real-time dari camera
    Camera 0,1,3,4... akan di-flip horizontal
    Camera 2 tidak di-flip
    """
    cap = cv.VideoCapture(camera_id)
    
    if not cap.isOpened():
        print(f"Error: Cannot open camera {camera_id}")
        return
    
    cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
    
    print("Camera stream started. Press 'q' to quit, 's' to save screenshot")
    print("HSV range: [5,70,20] to [30,255,255] (orange/yellow objects)")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Cannot read frame")
            break
        
        # Flip horizontal untuk memperbaiki camera yang kebalik (kecuali camera 2)
        if camera_id != 2:
            frame = cv.flip(frame, 1)
        
        h, w = frame.shape[:2]
        center_x, center_y = w // 2, h // 2
        
        mask = create_hsv_mask(frame, min_area_threshold=150)
        circles = detect_circles(mask)
        
        result_frame = frame.copy()
        cv.circle(result_frame, (center_x, center_y), 5, (255, 0, 255), -1)
        cv.putText(result_frame, "CENTER", (center_x-30, center_y-10), 
                  cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)
        
        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i, circle in enumerate(circles[0, :]):
                x, y, r = circle[0], circle[1], circle[2]
                distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
                
                cv.circle(result_frame, (x, y), r, (0, 255, 0), 2)
                cv.circle(result_frame, (x, y), 2, (255, 0, 0), 3)
                cv.line(result_frame, (center_x, center_y), (x, y), (255, 255, 0), 2)
                
                cv.putText(result_frame, f"({x},{y})", (x+10, y-10), 
                          cv.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
                cv.putText(result_frame, f"d:{distance:.0f}", (x+10, y+5), 
                          cv.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
                
                print(f"Circle {i+1}: center=({x}, {y}), radius={r}, distance={distance:.1f}")
        
        cv.putText(result_frame, f"Circles: {len(circles[0]) if circles is not None else 0}", 
                  (10, 30), cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv.putText(result_frame, "Press 'q' to quit, 's' to save", 
                  (10, h-20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        cv.imshow('Hough Circle Detection - Camera Stream', result_frame)
        cv.imshow('HSV Mask', mask)
        
        key = cv.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            cv.imwrite('hough_detection_screenshot.jpg', result_frame)
            print("Screenshot saved as 'hough_detection_screenshot.jpg'")
    
    cap.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python hough.py <image_filename>     # Process image file")
        print("  python hough.py camera [camera_id]   # Use camera stream")
        print("")
        print("Examples:")
        print("  python hough.py image.jpg            # Process image")
        print("  python hough.py camera               # Use laptop camera (0)")
        print("  python hough.py camera 1             # Use USB camera (1)")
        print("")
        print("HSV range: [5,70,20] to [30,255,255] (orange/yellow objects)")
        sys.exit(1)
    
    if sys.argv[1].lower() == "camera":
        camera_id = 0
        if len(sys.argv) > 2:
            try:
                camera_id = int(sys.argv[2])
            except ValueError:
                print("Invalid camera ID. Using default camera (0)")
        
        print(f"Starting camera stream with camera {camera_id}")
        hough_camera_stream(camera_id)
    else:
        image_filename = sys.argv[1]
        print(f"Processing image: {image_filename}")
        hough_transform(image_filename)