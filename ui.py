import numpy as np
import cv2
import cvui
import json


WINDOW_NAME	= 'GUI'
frame = np.zeros((800, 1000, 3), np.uint8)
cvui.init(WINDOW_NAME)



#cap = cv2.imread('test2.jpg')
cap = cv2.VideoCapture('test.mp4')

current = (0, 0)
points = []
new_points = []
fill_poligon = False

#parameters
video_size_x = 640
video_size_y = 480
layout_space_video = 10
draw_line_width = 2
draw_points_width = 4

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



while (True):


    frame[:] = (49, 52, 49)
    ret, v_frame = cap.read()
    #v_frame = cap

    mouse_click()

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


            if(fill_poligon):
                cv2.line(v_frame, points[0], points[len(points) - 1], (0,255,0), draw_line_width)

            #draw stringlabel at the last point
            cv2.putText(v_frame, ''.join(stringLabel), points[-1], cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 255, 0))


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



    if cvui.button(frame, layout_space_video + video_size_x + 30, 50, 'Clear All'):
        data = {}
        data['savedPoints'] = []



    if cvui.button(frame, layout_space_video + video_size_x + 30, 10, 'Save'):
        if(len(new_points) > 2):
            cv2.fillPoly(v_frame, np.array([new_points]), (255, 255, 255))

        conv_points = []

        for point in new_points:
            conv_points.append((point[0]/video_size_x, point[1]/video_size_y))

        if(''.join(new_stringLabel) != '' or len(new_points) != 0):
            data['savedPoints'].append({
                'label': ''.join(new_stringLabel),
                'points': conv_points
                })
            objects = [new_stringLabel, new_points]
            savedPointsCol.append(objects)
            #clear points
            new_stringLabel = []
            new_points = []

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


    if key == 27:
        break
    elif key != -1:
        new_stringLabel.append(chr(key))
