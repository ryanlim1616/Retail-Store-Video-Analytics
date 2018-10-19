import numpy as np
import cv2
import cvui


WINDOW_NAME	= 'GUI'
frame = np.zeros((800, 1000, 3), np.uint8)
cvui.init(WINDOW_NAME)

cap = cv2.VideoCapture('')

current = (0, 0)
points = []
fill_poligon = False

#parameters
video_size_x = 640
video_size_y = 480
layout_space_video = 10
draw_line_width = 2
draw_points_width = 4

def mouse_click():
    if(cvui.mouse(cvui.LEFT_BUTTON, cvui.CLICK)):
        if(cvui.mouse().x >= layout_space_video and cvui.mouse().x <= layout_space_video + video_size_x and cvui.mouse().y >= layout_space_video and cvui.mouse().y <= layout_space_video + video_size_y):
            print("Adding points ", (cvui.mouse().x - layout_space_video, cvui.mouse().y - layout_space_video))
            points.append((cvui.mouse().x - layout_space_video, cvui.mouse().y - layout_space_video))

    if(cvui.mouse(cvui.RIGHT_BUTTON, cvui.CLICK)):
        if(cvui.mouse().x >= layout_space_video and cvui.mouse().x <= layout_space_video + video_size_x and cvui.mouse().y >= layout_space_video and cvui.mouse().y <= layout_space_video + video_size_y and len(points) > 0):
            print("Deleting points")
            del points[-1]
            fill_poligon = False

while (True):
    
    frame[:] = (49, 52, 49)
    ret, v_frame = cap.read()
   
    mouse_click()
        
    if(len(points) > 1):
        for i in range (len(points) - 1):
            cv2.line(v_frame, points[i], points[i + 1], (0,255,0), draw_line_width)
        
        if(fill_poligon):
            cv2.line(v_frame, points[0], points[len(points) - 1], (0,255,0), draw_line_width)

    for point in points:
        cv2.circle(v_frame, tuple(point), draw_points_width, (0,0,255))

    if(len(points) > 2):
        fill_poligon = True

    if cvui.button(frame, layout_space_video + video_size_x + 30, 10, 'Done'):
        if(len(points) > 2):
            cv2.fillPoly(v_frame, np.array([points]), (255, 255, 255))

        

    cvui.image(frame, 10, 10, v_frame)
    cvui.update()

    cv2.imshow(WINDOW_NAME, frame)

    if cv2.waitKey(20) == 27:
        break
