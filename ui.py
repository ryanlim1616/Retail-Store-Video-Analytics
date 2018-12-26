import numpy as np
import cv2
import cvui
import json
import time
from picamera.array import PiRGBArray
from picamera import PiCamera


WINDOW_NAME	= 'GUI'
frame = np.zeros((800, 1000, 3), np.uint8)
cvui.init(WINDOW_NAME)



#cap = cv2.imread('test2.jpg')
#cap = cv2.VideoCapture('test.mp4')

current = (0, 0)
#zone:
points = []
new_points = []

#entry/exit:
epoints = []
new_epoints = []

fill_poligon = False

#parameters
video_size_x = 640
video_size_y = 480
layout_space_video = 10
draw_line_width = 2
draw_points_width = 4
camera_rotation = 180
camera_framerate = 20


#init variable
setZone = 0
setEntryExit = 0

#define labels
stringLabel=[]
new_stringLabel =[]

#final collection of points and labels
savedPointsCol = []
objects = []


#path to output file
path = 'config.txt'
data = {}
data['savedPoints'] = []
triggerSave = 0


#read from picamera
camera = PiCamera()
camera.resolution = (video_size_x, video_size_y)
camera.rotation = camera_rotation
camera.framerate = camera_framerate
rawCapture = PiRGBArray(camera, size = (video_size_x, video_size_y))

time.sleep(0.1)



def mouse_click():
    if(cvui.mouse(cvui.LEFT_BUTTON, cvui.CLICK)):
        if(cvui.mouse().x >= layout_space_video and cvui.mouse().x <= layout_space_video + video_size_x and cvui.mouse().y >= layout_space_video and cvui.mouse().y <= layout_space_video + video_size_y):
            print("Adding points ", (cvui.mouse().x - layout_space_video, cvui.mouse().y - layout_space_video))
            new_points.append((cvui.mouse().x - layout_space_video, cvui.mouse().y - layout_space_video))

    if(cvui.mouse(cvui.RIGHT_BUTTON, cvui.CLICK)):
        if(cvui.mouse().x >= layout_space_video and cvui.mouse().x <= layout_space_video + video_size_x and cvui.mouse().y >= layout_space_video and cvui.mouse().y <= layout_space_video + video_size_y and len(points) > 0):
            if(len(new_points) >= 1):
                print("Deleting points")
                del new_points[-1]
                fill_poligon = False
            if(new_stringLabel):
                # erase stringLabel
                new_stringLabel.clear()


def mouse_click_entryexit():
    if(cvui.mouse(cvui.LEFT_BUTTON, cvui.CLICK)):
        if(cvui.mouse().x >= layout_space_video and cvui.mouse().x <= layout_space_video + video_size_x and cvui.mouse().y >= layout_space_video and cvui.mouse().y <= layout_space_video + video_size_y):
            print("Adding entry/exit points ", (cvui.mouse().x - layout_space_video, cvui.mouse().y - layout_space_video))
            new_epoints.append((cvui.mouse().x - layout_space_video, cvui.mouse().y - layout_space_video))

    if(cvui.mouse(cvui.RIGHT_BUTTON, cvui.CLICK)):
        if(cvui.mouse().x >= layout_space_video and cvui.mouse().x <= layout_space_video + video_size_x and cvui.mouse().y >= layout_space_video and cvui.mouse().y <= layout_space_video + video_size_y and len(epoints) > 0):
            if(len(new_epoints) >= 1):
                print("Deleting entry/exit points")
                del new_epoints[-1]
                fill_poligon = False
            if(new_estringLabel):
                # erase stringLabel
                new_estringLabel.clear()

    #if(len(new_epoints)>2):
        #set direction
        #draw arrow

    #elif(len(new_epoints)>4):
    if(len(new_epoints)>4):
        setEntryExit = 0


#check if config file is empty, if not refill the zones.
with open('config.txt', 'r') as cfgfile:
    cfgfile.seek(0) #start of file
    first_char = cfgfile.read(1) #get the first character
    if not first_char:
         print ("Empty File") #first character is the empty string..
    else:
        cfgfile.seek(0) #first character wasn't empty, return to start of file.
        # refill the zones
        data = json.load(cfgfile)
        for p in data['savedPoints']:
            stringLabel = p['label']
            #print(stringLabel)
            for point in p['points']:
                points.append((int(point[0]*video_size_x),int(point[1]*video_size_y)))



for i_frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    v_frame = i_frame.array
    frame[:] = (49, 52, 49)


    if setZone:
        mouse_click()

    if setEntryExit:
        mouse_click_entryexit()


    #for existing points
    if(data):
        for p in data['savedPoints']:
            stringLabel = p['label']
            points = []
            for point in p['points']:
                points.append((int(point[0]*video_size_x),int(point[1]*video_size_y)))

                if(len(points) > 1):
                    for i in range (len(points) - 1):
                        cv2.line(v_frame, points[i], points[i + 1], (0,255,0), draw_line_width)

                for point in points:
                    cv2.circle(v_frame, tuple(point), draw_points_width, (0,0,255))

                if(len(points) > 2):
                    fill_poligon = True


            if(fill_poligon and len(points) != 0):
                cv2.line(v_frame, points[0], points[len(points) - 1], (0,255,0), draw_line_width)

                #draw stringlabel at the last point
                cv2.putText(v_frame, ''.join(stringLabel), points[-1], cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 255, 0))

            epoints = []
            for epoint in p['epoints']:
                epoints.append((int(epoint[0]*video_size_x),int(epoint[1]*video_size_y)))

            if(len(epoints)>=2):
                cv2.rectangle(v_frame, epoints[0], epoints[1], (0,0,255), draw_line_width)


            if(len(epoints) >= 4):
                cv2.line(v_frame, epoints[2], epoints[3], (0,0,255), draw_line_width)
                p = epoints[2]
                q = epoints[3]

                color = (0,0,255)
                thickness = draw_line_width
                line_type = 8
                shift = 0
                arrow_magnitude = 9
                image = v_frame

                # draw arrow tail
                cv2.line(v_frame, p, q, color, thickness, line_type, shift)
                # calc angle of the arrow
                angle = np.arctan2(p[1]-q[1], p[0]-q[0])
                # starting point of first line of arrow head
                p = (int(q[0] + arrow_magnitude * np.cos(angle + np.pi/4)),
                int(q[1] + arrow_magnitude * np.sin(angle + np.pi/4)))
                # draw first half of arrow head
                cv2.line(image, p, q, color, thickness, line_type, shift)
                # starting point of second line of arrow head
                p = (int(q[0] + arrow_magnitude * np.cos(angle - np.pi/4)),
                int(q[1] + arrow_magnitude * np.sin(angle - np.pi/4)))
                # draw second half of arrow head
                cv2.line(image, p, q, color, thickness, line_type, shift)


            if(len(epoints) > 2):
                fill_poligon = True


    #for new points
    if(len(new_points) > 1):
        for i in range (len(new_points) - 1):
            cv2.line(v_frame, new_points[i], new_points[i + 1], (0,255,0), draw_line_width)

        if(fill_poligon):
            cv2.line(v_frame, new_points[0], new_points[len(new_points) - 1], (0,255,0), draw_line_width)

        #draw stringlabel at the last point
        cv2.putText(v_frame, ''.join(new_stringLabel), new_points[-1], cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 255, 0))

    for point in new_points:
        cv2.circle(v_frame, tuple(point), draw_points_width, (0,0,255))

    if(len(new_points) > 2):
        fill_poligon = True



    #for new epoints
    if(len(new_epoints) >= 2):
        cv2.rectangle(v_frame, new_epoints[0], new_epoints[1], (0,0,255), draw_line_width)
        #draw stringlabel at the last point
        #cv2.putText(v_frame, ''.join(new_estringLabel), new_epoints[1], cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 255, 0))


    if(len(new_epoints) >= 4):
        cv2.line(v_frame, new_epoints[2], new_epoints[3], (0,0,255), draw_line_width)
        p = new_epoints[2]
        q = new_epoints[3]

        color = (0,0,255)
        thickness = draw_line_width
        line_type = 8
        shift = 0
        arrow_magnitude = 9
        image = v_frame

        # draw arrow tail
        cv2.line(v_frame, p, q, color, thickness, line_type, shift)
        # calc angle of the arrow
        angle = np.arctan2(p[1]-q[1], p[0]-q[0])
        # starting point of first line of arrow head
        p = (int(q[0] + arrow_magnitude * np.cos(angle + np.pi/4)),
        int(q[1] + arrow_magnitude * np.sin(angle + np.pi/4)))
        # draw first half of arrow head
        cv2.line(image, p, q, color, thickness, line_type, shift)
        # starting point of second line of arrow head
        p = (int(q[0] + arrow_magnitude * np.cos(angle - np.pi/4)),
        int(q[1] + arrow_magnitude * np.sin(angle - np.pi/4)))
        # draw second half of arrow head
        cv2.line(image, p, q, color, thickness, line_type, shift)


    if(len(new_epoints) > 2):
        fill_poligon = True


    # define button functions:
    if cvui.button(frame, layout_space_video + video_size_x + 30, 50, 'Clear All'):
        data = {}
        data['savedPoints'] = []
        setZone = 0
        setEntryExit = 0

    if cvui.button(frame, layout_space_video + video_size_x + 30, 90, 'Set Zone'):
        setZone = 1
        setEntryExit = 0
        triggerSave = 1

    if cvui.button(frame, layout_space_video + video_size_x + 30, 130, 'Set Entry/Exit'):
        setZone = 0
        setEntryExit = 1


    if cvui.button(frame, layout_space_video + video_size_x + 30, 10, 'Save'):
        setZone = 0
        setEntryExit = 0
        if(len(new_points) > 2):
            cv2.fillPoly(v_frame, np.array([new_points]), (255, 255, 255))

        #normal zones:
        conv_points = []

        for point in new_points:
            conv_points.append((point[0]/video_size_x, point[1]/video_size_y))

        #entry/exit:
        conv_epoints = []
        for point in new_epoints:
            conv_epoints.append((point[0]/video_size_x, point[1]/video_size_y))





        if(''.join(new_stringLabel) != '' or len(new_points) != 0 or len(new_epoints) != 0):
            data['savedPoints'].append({
                'label': ''.join(new_stringLabel),
                'points': conv_points,
                'epoints': conv_epoints
                })
            objects = [new_stringLabel, new_points, new_epoints]
            savedPointsCol.append(objects)
            #clear points
            new_stringLabel = []
            new_points = []
            new_epoints = []

            #print(objects)
            # redraw points and label using objects
            for savedPoints in savedPointsCol:
                #print(len(savedPoints[1]) - 1)
                for i in range (len(savedPoints[1]) - 1):
                    cv2.line(v_frame, (savedPoints[1][i][0]*video_size_x, savedPoints[1][i][1]*video_size_y), (savedPoints[1][i + 1][0]*video_size_x, savedPoints[1][i +1][1]*video_size_y), (0,255,0), draw_line_width)


            #save data into config file
            with open('config.txt', 'w') as outfile:
                json.dump(data, outfile)




    cvui.image(frame, 10, 10, v_frame)
    cvui.update()

    cv2.imshow(WINDOW_NAME, frame)

    key = cv2.waitKey(20)

    rawCapture.truncate(0)
    if key == 27:
        break
    elif key != -1:
        new_stringLabel.append(chr(key))
