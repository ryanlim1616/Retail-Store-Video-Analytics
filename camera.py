import numpy as np
import cv2
import time
import math
from picamera.array import PiRGBArray
from picamera import PiCamera
import json
import datetime

class Person:

    def __init__(self, buffer, x, y, w, h):

        self.name = 0
        self.previous_x = []
        self.previous_y = []
        self.enter = False
        self.exit = False
        self.delete_buffer = 0
        self.get_added = False
        self.predict_x = 0
        self.predict_y = 0


        self.curr_area = 0
        self.plan_to_enter_area = 0
        self.plan_to_enter_area_count = 0


        self.buffer = buffer
        self.curr_x = x
        self.curr_y = y
        self.curr_w = w
        self.curr_h = h
        self.curr_centroid_x = x + (w / 2)
        self.curr_centroid_y = y + (h / 2)

        self.previous_x.append( x + (w / 2) )
        self.previous_y.append( y + (h / 2) )

        self.cal_next_pos()

        #colors
        self.colorterm = {'Black':0, 'White':0, 'Gray':0, 'Red':0 , 'Green':0 , 'Blue':0 , 'Yellow':0 , 'Orange':0 , 'Pink':0 , 'Purple':0 , 'Brown':0}
        self.colors = []
        self.meanColor =(999,999,999)
        self.highestColorTermTop = ""
        self.highestColorTermBot = ""



    def set_name(self, name):
        self.name = name

    def add_current_person(self, x, y, w, h):
        self.curr_x = x
        self.curr_y = y
        self.curr_w = w
        self.curr_h = h
        self.curr_centroid_x = x + (w / 2)
        self.curr_centroid_y = y + (h / 2)

        self.previous_x.append( x + (w / 2) )
        self.previous_y.append( y + (h / 2) )

        #print(len(self.previous_x))

        if(len(self.previous_x) > self.buffer):
            #print('pop jor')
            self.previous_x.pop(0)
            self.previous_y.pop(0)

        #print(len(self.previous_x))
        self.cal_next_pos()

    def cal_next_pos(self):
        if(len(self.previous_x) == 1):
            self.predict_x = self.previous_x[0]
            self.predict_y = self.previous_y[0]
        else:
            counter = 1

            delta_x = 0
            delta_y = 0

            total_x = 0
            total_y = 0

            to_divide_x = 0
            to_divide_y = 0

            while(counter < len(self.previous_x)):
                total_x = total_x + ( (self.previous_x[counter] -
                                      self.previous_x[counter - 1]) * counter)

                to_divide_x = to_divide_x + counter

                total_y = total_y + ( (self.previous_y[counter] -
                                      self.previous_y[counter - 1]) * counter)

                to_divide_y = to_divide_y + counter

                counter = counter + 1


            delta_x = total_x / to_divide_x
            delta_y = total_y / to_divide_y

            self.predict_x = self.previous_x[-1] + delta_x
            self.predict_y = self.previous_y[-1] + delta_y


class BackGroundSubtractor:
    # When constructing background subtractor, we
    # take in two arguments:
    # 1) alpha: The background learning factor, its value should
    # be between 0 and 1. The higher the value, the more quickly
    # your program learns the changes in the background. Therefore,
    # for a static background use a lower value, like 0.001. But if
    # your background has moving trees and stuff, use a higher value,
    # maybe start with 0.01.
    # 2) firstFrame: This is the first frame from the video/webcam.
    def __init__(self,alpha,firstFrame):
        self.alpha  = alpha
        self.backGroundModel = firstFrame

    def getForeground(self,frame):
        # apply the background averaging formula:
        # NEW_BACKGROUND = CURRENT_FRAME * ALPHA + OLD_BACKGROUND * (1 - APLHA)
        self.backGroundModel =  frame * self.alpha + self.backGroundModel * (1 - self.alpha)

        # after the previous operation, the dtype of
        # self.backGroundModel will be changed to a float type
        # therefore we do not pass it to cv2.absdiff directly,
        # instead we acquire a copy of it in the uint8 dtype
        # and pass that to absdiff.

        return cv2.absdiff(self.backGroundModel.astype(np.uint8),frame)

def denoise(frame):
    frame = cv2.medianBlur(frame, 3)
    frame = cv2.GaussianBlur(frame,(3,3),0)

    return frame

def mousePosition(event, x, y, flags,param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print("(", x, ", ", y, ")")

camera = PiCamera()
camera.resolution = (640, 480)
camera.rotation = 180
camera.framerate = 20
rawCapture = PiRGBArray(camera, size = (640, 480))


time.sleep(0.1)

#parameters
dilation_size = 5
closing_kernel = 10

min_width = 30
min_height = 50
store_buffer = 10
distance_thres = 80
to_delete_buffer = 10
video_size_x = 640
video_size_y = 480

draw_line_width = 2
draw_points_width = 4


#entrence detection
# 1 = top->bottom, 2 = bottom->top, 3 = left->right, 4 = right->left
e_direction = 0
e_min_x = 0
e_max_x = 0
e_min_y = 0
e_max_y = 0

temp_save_start_x = 0
temp_save_start_y = 0
temp_save_end_x = 0
temp_save_end_y = 0

#zones detection
all_zones = []
all_zones_label = []
all_canvas = []


#zones
points=[]
new_points = []

#entry/exit:
epoints = []
new_epoints = []

#read config file
with open('config.txt', 'r') as cfgfile:
    cfgfile.seek(0) #start of file
    first_char = cfgfile.read(1) #get the first character
    if not first_char:
        print ("Empty File") #first character is the empty string..
    else:
        cfgfile.seek(0) #first character wasn't empty, return to start of file.
        # refill the zones
        data = json.load(cfgfile)

if(data):

    for p in data['savedPoints']:
        stringLabel = p['label']
        points_temp = []
        for point in p['points']:
            points_temp.append((int(point[0]*video_size_x),int(point[1]*video_size_y)))

        if(len(points_temp) > 1):
            all_zones.append(points_temp)
            all_zones_label.append(stringLabel)

            canvas = np.zeros((640, 480), np.uint8)
            cv2.fillPoly(canvas, np.array([points_temp]), (255, 255, 255))
            all_canvas.append(canvas)


    for p in data['savedPoints']:
        e_points_counter = 1
        for epoint in p['epoints']:
            if(e_points_counter == 1):
                e_min_x = int(epoint[0]*video_size_x)
                e_min_y = int(epoint[1]*video_size_y)


            elif(e_points_counter == 2):
                e_max_x = int(epoint[0]*video_size_x)
                e_max_y = int(epoint[1]*video_size_y)

            elif(e_points_counter == 3):
                temp_save_start_x = int(epoint[0]*video_size_x)
                temp_save_start_y = int(epoint[1]*video_size_y)

            elif(e_points_counter == 4):
                temp_save_end_x = int(epoint[0]*video_size_x)
                temp_save_end_y = int(epoint[1]*video_size_y)

                if(temp_save_start_x >= e_min_x and temp_save_start_x <= e_max_x and
                   temp_save_end_x >= e_min_x and temp_save_end_x <= e_max_x):
                    if(temp_save_start_y > temp_save_end_y):
                        e_direction = 2

                    else:
                        e_direction = 1

                else:
                    if(temp_save_start_x > temp_save_end_x):
                        e_direction = 4
                    else:
                        e_direction = 3


            e_points_counter = e_points_counter + 1




#testing
all_person = []
count_num = 0
first_time = False
backSubtractor = None
region = []

test_point1 = (391, 329)
test_point2 = (452, 326)
test_point3 = (470, 359)
test_point4 = (400, 358)

region.append(test_point1)
region.append(test_point2)
region.append(test_point3)
region.append(test_point4)

canvas = np.zeros((640, 480), np.uint8)
cv2.fillPoly(canvas, np.array([region]), (255, 255, 255))



#BGS = cv2.bgsegm.createBackgroundSubtractorMOG()
#BGS = cv2.bgsegm.createBackgroundSubtractorGMG()
BGS = cv2.createBackgroundSubtractorMOG2(detectShadows=True)

kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(dilation_size, dilation_size))
closing_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(closing_kernel, closing_kernel))

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    image = frame.array
    if(first_time == True):
        first_time = False
        backSubtractor = BackGroundSubtractor(0.001,denoise(image))



    else:
        start = time.time()
        templist = []


        if(data):
            for p in data['savedPoints']:
                stringLabel = p['label']
                points = []
                for point in p['points']:
                    points.append((int(point[0]*video_size_x),int(point[1]*video_size_y)))

                    if(len(points) > 1):
                        for i in range (len(points) - 1):
                            cv2.line(image, points[i], points[i + 1], (0,255,0), draw_line_width)

                    for point in points:
                        cv2.circle(image, tuple(point), draw_points_width, (0,0,255))

                    if(len(points) > 2):
                        fill_poligon = True


                if(fill_poligon and len(points) != 0):
                    cv2.line(image, points[0], points[len(points) - 1], (0,255,0), draw_line_width)

                    #draw stringlabel at the last point
                    cv2.putText(image, ''.join(stringLabel), points[-1], cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 255, 0))

                epoints = []
                for epoint in p['epoints']:
                    epoints.append((int(epoint[0]*video_size_x),int(epoint[1]*video_size_y)))

                if(len(epoints)>=2):
                    cv2.rectangle(image, epoints[0], epoints[1], (0,0,255), draw_line_width)


                if(len(epoints) >= 4):
                    cv2.line(image, epoints[2], epoints[3], (0,0,255), draw_line_width)
                    p = epoints[2]
                    q = epoints[3]

                    t_color = (0,0,255)
                    thickness = draw_line_width
                    line_type = 8
                    shift = 0
                    arrow_magnitude = 9

                    # draw arrow tail
                    cv2.line(image, p, q, t_color, thickness, line_type, shift)
                    # calc angle of the arrow
                    angle = np.arctan2(p[1]-q[1], p[0]-q[0])
                    # starting point of first line of arrow head
                    p = (int(q[0] + arrow_magnitude * np.cos(angle + np.pi/4)),
                    int(q[1] + arrow_magnitude * np.sin(angle + np.pi/4)))
                    # draw first half of arrow head
                    cv2.line(image, p, q, t_color, thickness, line_type, shift)
                    # starting point of second line of arrow head
                    p = (int(q[0] + arrow_magnitude * np.cos(angle - np.pi/4)),
                    int(q[1] + arrow_magnitude * np.sin(angle - np.pi/4)))
                    # draw second half of arrow head
                    cv2.line(image, p, q, t_color, thickness, line_type, shift)


                if(len(epoints) > 2):
                    fill_poligon = True
        #mask = backSubtractor.getForeground(denoise(image))
        #ret, mask = cv2.threshold(mask, 15, 255, cv2.THRESH_BINARY)
        #mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY);

        mask = BGS.apply(denoise(image))
        mask[mask == 127] = 0
        #mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        #mask = cv2.dilate(mask, kernel, iterations = 1)
        im2, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(mask, contours, -1, (0,255,0))





        cv2.imshow("frame", mask)

        if len(contours) > 0:
            for count in contours:
                x,y,w,h = cv2.boundingRect(count)

                if(w >= min_width and h >= min_height):
                    #cv2.rectangle(frame, (x,y), (x+w,y+h), (255, 0, 0), 2)
                    p1 = Person(store_buffer, x, y, w, h)

                    templist.append(p1)



        if(len(all_person) == 0):
            for p in templist:
                p.set_name(count_num)
                p.get_added = True
                all_person.append(p)
                count_num = count_num + 1

                #print("added new, 00")
                #print('add new: ', all_person[-1].name)
        else:
            later_add = []
            for p in templist:
                added = False
                for ap in all_person:
                    dis = math.sqrt( ( (p.curr_centroid_x - ap.curr_centroid_x) *
                                       (p.curr_centroid_x - ap.curr_centroid_x)) +
                                     ( (p.curr_centroid_y - ap.curr_centroid_y) *
                                       (p.curr_centroid_y - ap.curr_centroid_y)) )

                    if(dis < distance_thres):
                        ap.add_current_person(p.curr_x, p.curr_y, p.curr_w, p.curr_h)
                        ap.get_added = True
                        #print("added existing: ", str(ap.name))
                        #print(len(ap.previous_x), ", ", len(ap.previous_y))
                        #print(ap.previous_x)
                        #print(ap.previous_y)
                        added = True
                        #print('add old')
                        break

                if(added == False):
                    later_add.append(p)

            for aa in later_add:

                aa.set_name(count_num)
                aa.get_added = True
                count_num = count_num + 1
                all_person.append(aa)
                #print("added new, not 00")
                #print('add new: ', all_person[-1].name)
            later_add = []

        for ap in all_person:
            if(ap.get_added == False):
                ap.delete_buffer = ap.delete_buffer + 1
            else:
                ap.delete_buffer = 0
                ap.get_added = False

        #delete_lol = 0
        #while(delete_lol < len(all_person)):
            #if(all_person[delete_lol].delete_buffer > to_delete_buffer):
           #     all_person.pop(delete_lol)
           # else:
             #   delete_lol = delete_lol + 1
        for i, o in enumerate(all_person):
            if(o.delete_buffer > to_delete_buffer):
                del all_person[i]
                break

        #dump data to TXT
        data_to_save = {}
        data_to_save['timeStamp'] = str(datetime.datetime.now())
        data_to_save['person'] = []



        for ap in all_person:

            data_to_save['person'].append({
                'id': ap.name,
                'x': ap.curr_x,
                'y': ap.curr_y,
                'w': ap.curr_w,
                'h': ap.curr_h,
                'activity': '',
                'c_top':ap.highestColorTermTop,
                'c_bot':ap.highestColorTermBot,
                'c_Term': ap.colorterm
                })

            person_canvas = np.zeros((640, 480), np.uint8)
            cv2.rectangle(person_canvas, (ap.curr_x, ap.curr_y),
                          (ap.curr_x + ap.curr_w, ap.curr_y + ap.curr_h), (255, 255, 255), -1)

            highest_count = 0
            highest_index = 0
            for c in range (0, len(all_canvas)):
                bitwise_different = cv2.bitwise_and(all_canvas[c], person_canvas)
            #gray = cv2.cvtColor(bitwise_different, cv2.COLOR_BGR2GRAY)

                nzCount = cv2.countNonZero(bitwise_different)
                if(nzCount > highest_count):
                    highest_index = c + 1


            if(highest_index > 0):
                if(ap.curr_area != highest_index and ap.plan_to_enter_area != highest_index):
                    ap.plan_to_enter_area = highest_index
                    ap.plan_to_enter_area_count = 1

                elif(ap.curr_area == highest_index):
                    ap.plan_to_enter_area = 0
                    ap.plan_to_enter_area_count = 0

                if(ap.plan_to_enter_area == highest_index):
                    #print("testing")
                    ap.plan_to_enter_area_count = ap.plan_to_enter_area_count + 1
                    if(ap.plan_to_enter_area_count > 5):
                        print(ap.name, " Enter area ", all_zones_label[highest_index - 1])

                        data_to_save['person'][-1]['activity'] = 'Area ' + all_zones_label[highest_index - 1]

                        ap.curr_area = highest_index
                        ap.plan_to_enter_area = 0
                        ap.plan_to_enter_area_count = 0

            else:
                if(ap.curr_area != 0):
                    ap.plan_to_enter_area_count = ap.plan_to_enter_area_count + 1
                    if(ap.plan_to_enter_area_count > 5):
                        print(ap.name, " Enter area 0")

                        data_to_save['person'][-1]['activity'] = 'Area main'

                        ap.curr_area = 0
                        ap.plan_to_enter_area = 0
                        ap.plan_to_enter_area_count = 0

                if(ap.plan_to_enter_area != 0):
                    ap.plan_to_enter_area = 0
                    ap.plan_to_enter_area_count = 0


            if(len(ap.previous_x) >= 4 and ap.previous_x[-1] >= e_min_x and ap.previous_x[-1] <= e_max_x and
                   ap.previous_y[-1] >= e_min_y and ap.previous_y[-1] <= e_max_y):
                #print("(", str(ap.previous_x[-1]), ", ", ap.previous_y[-1], ")")
                if(e_direction == 1):
                    if( ap.previous_y[-1] < ap.previous_y[-2] and
                        ap.previous_y[-2] < ap.previous_y[-3] and
                        ap.previous_y[-3] < ap.previous_y[-4] and ap.exit == False):

                        data_to_save['person'][-1]['activity'] = 'Exit Shop'

                        print('byebye')
                        ap.exit = True
                    elif( ap.previous_y[-1] > ap.previous_y[-2] and
                          ap.previous_y[-2] > ap.previous_y[-3] and
                          ap.previous_y[-3] > ap.previous_y[-4] and ap.enter == False ):
                        print('enter to shop, welcome ')
                        data_to_save['person'][-1]['activity'] = 'Enter Shop'
                        ap.enter = True

                elif(e_direction == 2):
                    if( ap.previous_y[-1] > ap.previous_y[-2] and
                        ap.previous_y[-2] > ap.previous_y[-3] and
                        ap.previous_y[-3] > ap.previous_y[-4] and ap.exit == False):
                        print('byebye')

                        data_to_save['person'][-1]['activity'] = 'Exit Shop'
                        ap.exit = True
                    elif( ap.previous_y[-1] < ap.previous_y[-2] and
                          ap.previous_y[-2] < ap.previous_y[-3] and
                          ap.previous_y[-3] < ap.previous_y[-4] and ap.enter == False ):
                        print('enter to shop, welcome ')
                        data_to_save['person'][-1]['activity'] = 'Enter Shop'
                        ap.enter = True

                elif(e_direction == 3):
                    if( ap.previous_x[-1] < ap.previous_x[-2] and
                        ap.previous_x[-2] < ap.previous_x[-3] and
                        ap.previous_x[-3] < ap.previous_x[-4] and ap.exit == False):
                        print('byebye')
                        data_to_save['person'][-1]['activity'] = 'Exit Shop'
                        ap.exit = True
                    elif( ap.previous_x[-1] > ap.previous_x[-2] and
                          ap.previous_x[-2] > ap.previous_x[-3] and
                          ap.previous_x[-3] > ap.previous_x[-4] and ap.enter == False ):
                        print('enter to shop, welcome ')
                        data_to_save['person'][-1]['activity'] = 'Enter Shop'
                        ap.enter = True

                elif(e_direction == 4):
                    if( ap.previous_x[-1] > ap.previous_x[-2] and
                        ap.previous_x[-2] > ap.previous_x[-3] and
                        ap.previous_x[-3] > ap.previous_x[-4] and ap.exit == False):
                        print('byebye')
                        data_to_save['person'][-1]['activity'] = 'Exit Shop'
                        ap.exit = True
                    elif( ap.previous_x[-1] < ap.previous_x[-2] and
                          ap.previous_x[-2] < ap.previous_x[-3] and
                          ap.previous_x[-3] < ap.previous_x[-4] and ap.enter == False ):
                        print('enter to shop, welcome ')
                        data_to_save['person'][-1]['activity'] = 'Enter Shop'
                        ap.enter = True





            crop_img = image[ap.curr_y:ap.curr_y + ap.curr_h, ap.curr_x:ap.curr_x + ap.curr_w]
            cv2.imshow("cropped", crop_img)

            # ------ START OF COLORS -----------

            # divide mat into top half and bottom half

            cropped_top = image[ap.curr_y:int(ap.curr_y + (ap.curr_h)/2), ap.curr_x:ap.curr_x + ap.curr_w]
            cropped_bot = image[int(ap.curr_y + (ap.curr_h)/2):ap.curr_y + ap.curr_h, ap.curr_x:ap.curr_x + ap.curr_w]

            crop_img_all =[cropped_top, cropped_bot]

            for idx, crops in enumerate(crop_img_all):
                #cv2.imshow("top", cropped_top)
                #cv2.imshow("bot", cropped_bot)


                crop_img_hsv = cv2.cvtColor(crops, cv2.COLOR_BGR2HSV)
                hbins = 15
                sbins = 8
                vbins = 8

                histSize = [ hbins, sbins, vbins ]

                hranges = [ 0, 180 ]
                sranges = [ 0, 256 ]
                vranges = [ 0, 256 ]

                ranges = [ hranges, sranges, vranges ]

                channels = [ 0, 1, 2 ]

                #hist = cv2.calcHist([crop_img], channels, None, histSize, ranges)
                hist_h = cv2.calcHist([crop_img_hsv], [0], None, [hbins], [0,180])
                hist_s = cv2.calcHist([crop_img_hsv], [1], None, [sbins], [0,256])
                hist_v = cv2.calcHist([crop_img_hsv], [2], None, [vbins], [0,256])

                #get top 1 color
                _, _, _, max_loc_h = cv2.minMaxLoc(hist_h)
                _, _, _, max_loc_s = cv2.minMaxLoc(hist_s)
                _, _, _, max_loc_v = cv2.minMaxLoc(hist_v)

                #print(max_loc_h[1],max_loc_s[1],max_loc_v[1])

                #artifically increase the saturation of the colors (s+40)
                scalar_color = (max_loc_h[1]*12, max_loc_s[1]*32+40, max_loc_v[1]*32)

                crop_img_hsv[:] =(scalar_color)
                crop_img_hsv = cv2.cvtColor(crop_img_hsv, cv2.COLOR_HSV2BGR)

                #in BGR color space:
                meanCurr = cv2.mean(crop_img_hsv)

                if(ap.meanColor == (999,999,999)):
                    ap.meanColor = meanCurr
                else:
                    ap.meanColor = ((ap.meanColor[0]+meanCurr[0])/2,(ap.meanColor[1]+meanCurr[1])/2,(ap.meanColor[2]+meanCurr[2])/2)
                    scalar_color = ap.meanColor
                    #print(ap.name, meanCurr, ap.meanColor)

                #cv2.imshow("color", crop_img_hsv)

                #ground truth colors
                SBlack = (0.0, 0.0, 0.0)
                SWhite = (255.0, 255.0, 255.0)
                #ori: SGray = (145.0, 149.0, 146.0)
                SGray = (125.0, 129.0, 126.0)
                SRed = (0.0, 0.0, 229.0)
                #ori: SGreen = (26.0, 176.0, 21.0)
                SGreen = (26.0, 216.0, 21.0)
                SBlue = (223.0, 67.0, 3.0)
                SYellow = (20.0, 255.0, 255.0)
                SOrange = (6.0, 115.0, 249.0)
                #ori: SPink = (192.0, 129.0, 255.0)
                SPink = (182.0, 129.0, 255.0)
                SPurple = (156.0, 30.0, 126.0)
                SBrown = (0.0, 55.0, 101.0)

                all_colors = [SBlack, SWhite, SGray, SRed, SGreen, SBlue, SYellow, SOrange, SPink, SPurple, SBrown]

                colorTermPercentage =[]
                max_distance = math.sqrt(((512 + 127/256)*65025) + (260100) + ((512 + (255-127)/256)*65025))

                for gtcolor in all_colors:
                    rmean = (gtcolor[2] + scalar_color[2]) / 2
                    r = gtcolor[2] - scalar_color[2]
                    g = gtcolor[1] - scalar_color[1]
                    b = gtcolor[0] - scalar_color[0]
                    c_diff = math.sqrt(((512 + rmean/256)*r*r) + (4*g*g) + ((512 + (255-rmean)/256)*b*b))
                    colorTermPercentage.append((max_distance - c_diff)/max_distance)
                    #print (gtcolor, scalar_color, c_diff)


                #set colors
                #cant use for loop as the dictionary does not loop according to idx
                #for idx, terms in enumerate(ap.colorterm):
                #    print (terms)
                #    ap.colorterm[terms] = colorTermPercentage[idx]

                #print(colorTermPercentage)

                ap.colorterm['Black'] = colorTermPercentage[0]
                ap.colorterm['White'] = colorTermPercentage[1]
                ap.colorterm['Gray'] = colorTermPercentage[2]
                ap.colorterm['Red'] = colorTermPercentage[3]
                ap.colorterm['Green'] = colorTermPercentage[4]
                ap.colorterm['Blue'] = colorTermPercentage[5]
                ap.colorterm['Yellow'] = colorTermPercentage[6]
                ap.colorterm['Orange'] = colorTermPercentage[7]
                ap.colorterm['Pink'] = colorTermPercentage[8]
                ap.colorterm['Purple'] = colorTermPercentage[9]
                ap.colorterm['Brown'] = colorTermPercentage[10]

                sorted_by_value = sorted(ap.colorterm.items(), key=lambda kv: kv[1])
                sorted_by_value.reverse()

                #print(ap.name, sorted_by_value)
                #print(max(ap.colorterm, key=ap.colorterm.get))

                finalTerm = max(ap.colorterm, key=ap.colorterm.get)

                if(idx == 0):
                    ap.highestColorTermTop = finalTerm
                    #print(ap.name, "top: ", finalTerm, sorted_by_value)
                else:
                    ap.highestColorTermBot = finalTerm
                    #print(ap.name, "Bot: ", finalTerm, sorted_by_value)
                    #print("----------------------------")

            data_to_save['person'][-1]['c_top'] = ap.highestColorTermTop
            data_to_save['person'][-1]['c_bot'] = ap.highestColorTermBot
            data_to_save['person'][-1]['c_Term'] = ap.colorterm

            print(data_to_save)


            # ------ END OF COLORS -----------

            putText = str(ap.name) + ", (" + str(ap.highestColorTermTop) + ", " + str(ap.highestColorTermBot) + ")"
            cv2.rectangle(image, (ap.curr_x, ap.curr_y),
                          (ap.curr_x + ap.curr_w, ap.curr_y + ap.curr_h), (255, 0, 0), 2)
            cv2.putText(image, putText, (ap.curr_x, ap.curr_y), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (255,255,255), 2, cv2.LINE_AA)


        #save to file
        if(len(data_to_save['person']) != 0):
            with open('data.txt', 'a') as outfile:
                json.dump(data_to_save, outfile)
        #cv2.rectangle(image, (120, 240), (250, 260), (0, 255, 0), 2)

        #1 = top->bottom, 2 = bottom->top, 3 = left->right, 4 = right->left
        #direction = 0







        #cv2.line(image, (150, 280), (250, 280), (0,255,0), 2)
        templist = []
        cv2.fillPoly(image, np.array([region]), (255, 255, 255))
        cv2.imshow("ori", image)
        cv2.setMouseCallback("ori", mousePosition)


        end = time.time()
        seconds = end - start
        fps  = 20 / seconds;
        #print("FPS: ", fps)

    key = cv2.waitKey(1) & 0xFF
    rawCapture.truncate(0)
    if key == ord("q"):
        break

