# -*- coding: utf-8 -*-
'''
Title: Tracker
Description: Offline tracker for detection of rats
             in the novel Hex-Maze experiment as
             a replacement for the manual location scoring.
             Uses a neural network model in onnx format and
             gives as output the tracked video with path annotations
             (.mp4), complete trials locations detected (.logs)
             and session summary (.txt).
Organistaion: Genzel Lab, Donders Institute
              Radboud University, Nijmegen
Author(s): Atharva Kand-Giulia Porro
Notes: If run outside Colab uncomment last lines of run_vid (e.g. cv2.destroyAllWindows()
       and key = cv2.waitKey(1) & 0xFF) ##see comment lines
'''

from itertools import groupby
from datetime import date, timedelta, datetime
from pathlib import Path
from collections import deque
from tools import mask
import cv2
import onnxruntime


import os
import math
import time
import logging
import threading
import numpy as np
import pandas as pd

FONT = cv2.FONT_HERSHEY_TRIPLEX
font = cv2.FONT_HERSHEY_PLAIN  # cv2.FONT_HERSHEY_TRIPLEX #
colors = np.random.uniform(0, 255, size=(100, 3))


# force tf2onnx to cpu
#os.environ['CUDA_VISIBLE_DEVICES'] = "-1"
# vid_width,vid_height = 1176, 712

# find the shortest distance between two points in space
def points_dist(p1, p2):
    dist = math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)
    return dist


# convert time in milli seconds to -> hh:mm:ss,uuu format
def convert_milli(time):
    sec = (time / 1000) % 60
    minute = (time / (1000 * 60)) % 60
    hr = (time / (1000 * 60 * 60)) % 24
    return f'{int(hr):02d}:{int(minute):02d}:{sec:.3f}'


class Tracker:
    def __init__(self, vp, nl, out):
        '''Tracker class initialisations'''
        # set of threads to load network, input and variables
        threads = list()
        # thread to load network
        cnn = threading.Thread(target=self.load_network, args=(1,))
        threads.append(cnn)
        # thread to load session infos, date, rat number, goal and start locations, variables and create video and .txt saving path
        session = threading.Thread(target=self.load_session, args=(vp, nl, 1, out))
        threads.append(session)
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        print('\n -Network loaded- ', self.session)
        # find location of goal node and all start nodes
        self.start_nodes_locations = self.find_location(self.start_nodes, self.goal)
        print('\n  ________  SUMMARY SESSION  ________  ')
        print('\nPath video file:', self.save_video)
        print('\nPath .log and .txt files:', self.save)
        print('\nTotal trials current session:', self.num_trials, '\n\nGoal location node ', self.goal)
        for i in range(0, len(self.start_nodes)):
            print('\nStart node trial {} '.format(i + 1), self.start_nodes[i], 'location',
                  self.start_nodes_locations[i])

        # logger intitialisations
        self.logger = logging.getLogger('')
        self.logger.setLevel(logging.INFO)
        logfile_name = '{}/log_{}_{}.log'.format(out, str(self.date), 'Rat' + self.rat)

        fh = logging.FileHandler(str(logfile_name))
        formatter = logging.Formatter('%(levelname)s : %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        self.logger.info('Video Imported: {}'.format(vp))
        self.logger.info(f'The log format is: Video Timestamp(hh:mm:ss.ms), UTC Synchronised Timestamp in seconds, Rat position')
        self.logger.info(f'Use pd.to_datetime(sys_time, unit="s",utc=True) or datetime.utcfromtimestamp(sys_time) to convert UTC timestamp to datetime format.')
        print('\nCreating log files...')
        
        self.sync_ts_dict = pd.read_csv(str(out) + 'stitched_framewise_ts.csv', index_col=0).to_dict()
        self.run_vid()

    def load_network(self, n):
        # Load the model of yolov3-  weights files and cnn structure (.cfg config file)
        # Converted onnx weights
        print('Available providers:', onnxruntime.get_device())
        so = onnxruntime.SessionOptions()
        so.add_session_config_entry('session.load_model_format', 'ONNX')
        onnx_weights_path = './weights/yolov3_training_best.onnx'

        # Specify your models network size
        self.network_size = (416, 416)
        # prefer CUDA Execution Provider using GPU over CPU Execution Provider
        self.session = onnxruntime.InferenceSession(onnx_weights_path,
                                                    providers=['CUDAExecutionProvider','CPUExecutionProvider']) #
      #  self.session.get_providers()
        # get the input and outputs metadata as a list of :class:`onnxruntime.NodeArg`
        self.session.get_modelmeta()

        self.input_name = self.session.get_inputs()[0].name
        self.output_name_1 = self.session.get_outputs()[0].name
        self.output_name_2 = self.session.get_outputs()[1].name
        # load object classes - researcher, rat, head
        self.classes = []
        with open("tools/classes.txt", "r") as f:
            self.classes = f.read().splitlines()

    def load_session(self, vp, nl, n, out):
        # experiment meta-data
        start_point = input("\n>> Do you want to start tracking the video from a specific time point? \n\n > Press enter if you want to start tracking from the beginning \n   OR \n > Type starting point from the start of the video. Minutes (e.g.00:58:26.500 = 58): \n")
        if start_point == '':
            self.start_point = None
        else:
            start_point_seconds = input('\n Seconds (e.g. 26.5 ):')
            self.start_point = (float(start_point)*60) + float(start_point_seconds)
            self.custom_trial = input('\n From which trial does the tracking start?')
        self.rat = input("\n>> Enter rat number: ")
        self.date = input("\n>> Enter date of trial: ")
        self.num_trials = input("\n>> Enter num total trials: ")
        self.goal = input("\n>> Enter session GOAL node (number): ")
        self.trial_type = input(
            "\n>> Enter first trial type [1]-Normal [2]-New GoaL Location [3]-Probe [4]-Special(Ephys): ")
        # Session start goals
        self.start_nodes = []
        self.special_trials = []
        for i in range(int(self.num_trials)):
            if self.start_point is not None:
                node = input('\n> Enter START node (number) of trial {}: '.format(int(self.custom_trial) + i))
                self.start_nodes.append(int(node))
            else:
                node = input('\n> Enter START node (number) of trial {}: '.format(i + 1))
                self.start_nodes.append(int(node))
        if self.trial_type == '4':
            print(
                '\n> Enter position of 10 minutes trials (e.g. 12 > enter > 27 ...) \n Press enter when all 10 minutes trials are entered.')
            for i in range(10):
                trial = input('\n>>  Enter trial number n{}. Press Enter if done : '.format(i + 1))
                if trial == '':
                    break
                else:
                    self.special_trials.append(int(trial))
            print('Special 10 minutes trials are numbers', self.special_trials)

        self.node_list = str(nl)
        self.cap = cv2.VideoCapture(str(vp))
        self.start_trial = True  # Check start node if researcher is present before trial start
        self.end_session = False  # Check last goal location reached
        self.check = False  # Check for proximity between researcher and rat
        self.record_detections = False  ##True to save nodes
        self.goal_location = None
        self.reached = False
        self.frame = None
        self.disp_frame = None
        self.pos_centroid = None  # keep centroid rat
        self.center_researcher = None
        if self.start_point is None:
           self.trial_num = 1
        else:
           self.trial_num = int(self.custom_trial)
        self.counter = 0 #keep count of trials
        self.count_rat = 0
        self.count_head = 0
        self.start_time = 0  # timer start time
        # Normal trial True if trial type = 1 : starts upon rat placement and finished when goal location reached
        self.normal_trial = False
        # NGL True if trial type = 2 : 10 min timer starts upon rat placement
        self.NGL = False
        # Probe True if trial type = 3 :2 min timer starts upon rat placement
        self.probe = False
        # change maxlen value to chnage how long the path line is
        self.centroid_list = deque(maxlen=500)
        self.node_pos = []
        self.time_points = []  ##time point for velocity
        self.node_id = []  ##node num
        self.saved_nodes = []
        self.saved_velocities = []
        self.summary_trial = []
        self.store_fps = [] # store fps for mean

        self.save = '{}{}_{}'.format(out, str(self.date), 'Rat' + self.rat + '.txt')  # str(date.today())
        ##set output video saved in folder video/'date_unique file name'.mp4
        self.codec = cv2.VideoWriter_fourcc(*'mp4v')
        # self.codec = cv2.VideoWriter_fourcc(*'XVID')    #to change format video in .avi
        self.save_video = '{}{}_{}.mp4'.format(out, str(self.date), 'Rat' + self.rat)  # or .avi
        self.vid_fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.out = cv2.VideoWriter('{}'.format(self.save_video), self.codec, self.vid_fps, (1176, 712))
        
        # process and display video

    def run_vid(self):
        '''
        Frame by Frame looping of video
        '''
        print('\nStarting video.....\n')
        if self.start_point is None:
            with open(self.save, 'a+') as file:
                file.write(f"Rat number: {self.rat} , Date: {self.date} \n")
        self.Start_Time = time.time()
        # If a specific time point in which to start the video was specified calculate frame_count index and start video from that frame
        if self.start_point is not None:
            # Calculate frame index at specified time (must be in seconds, calculated from the start of the videos)
            frame_index = int(float(self.start_point) * self.vid_fps)
            # Set video to start at specific frame identified by the index number (=0 if first frame of the video)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        
        frame_itr = -1

        while True:
            success, self.frame = self.cap.read()
            self.frame_time = self.cap.get(cv2.CAP_PROP_POS_MSEC)
            self.converted_time = convert_milli(int(self.frame_time))
            frame_itr += 1
            # process and display frame (success is a boolean, False if frame is None, True otherwise)
            if success:
                self.disp_frame = self.frame.copy()
                self.disp_frame = cv2.resize(self.disp_frame, (1176, 712))
                self.t1 = time.time()
                self.cnn(self.disp_frame)  # , Rat, tracker,Init,boxes
                self.annotate_frame(self.disp_frame)
                # Uncomment line below to show video on screen outside Colab
              #  cv2.imshow('Tracker', self.disp_frame)
                # Keep recording video until it ends
                self.out.write(self.disp_frame)
                # Save centroid position in log file if trial started
                if self.record_detections:
                    if self.saved_nodes:
                        self.logger.info(
                            f'{self.converted_time} {self.sync_ts_dict["Corrected Time Stamp"][frame_itr]} : The rat position is: {self.pos_centroid} @ {self.saved_nodes[-1]}')
                    else:
                        self.logger.info(
                            f'{self.converted_time} {self.sync_ts_dict["Corrected Time Stamp"][frame_itr]} : The rat position is: {self.pos_centroid}')  # pos_centroid

                if self.end_session:
                    cv2.putText(self.disp_frame, "Session Finished", (60, 60),
                                fontFace=FONT, fontScale=0.75, color=(0, 255, 0), thickness=1)
                    print('\n', self.converted_time, '\n >>>> Session ended with ', self.trial_num, ' trials out of',
                          self.num_trials)
            # Uncomment lines below if running outside Colab
              #  key = cv2.waitKey(1) & 0xFF
              #  if key == ord('q'):
              #     print('Session ended with ', self.trial_num,' trials')
              #     print('#Program ended by user')
              #     break
            # if video is finished end tracking                          
            else:
                if not self.end_session:
                    self.calculate_velocity(self.time_points)
                    self.save_to_file(self.save)
                    print('\n', self.converted_time, '\n >>>> Session ended before trial time finished. Ends with ', self.trial_num, ' trials out of',
                          self.num_trials)
                break
        # Close video output and print time required for tracking if job is finished
        end = time.time()
        hours, rem = divmod(end - self.Start_Time, 3600)
        minutes, seconds = divmod(rem, 60)
        print("Tracking process finished in: {:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))
        self.cap.release()
        self.out.release()
        import statistics
        mean_fps = statistics.mean(self.store_fps)
        print('Average fps',mean_fps)
    # Uncomment outside colab
     #  cv2.destroyAllWindows()

    def find_start(self, center_rat):
        '''
        Function to find start of each trial [rat at least 40 pixels from center of start node]
        '''
        # calculate coordinate rectangle in start node
        print('\n', self.converted_time, '\n >>> Waiting Start Next Trial: ', self.trial_num, ' Start node:',
              self.start_nodes[self.counter])
        # print('Rat position', self.pos_centroid, 'Node', self.start_nodes_locations[self.trial_num])
        node = self.start_nodes_locations[self.counter]
        x = int(node[0])
        y = int(node[1])
        w = 15
        h = 13
        cv2.rectangle(self.disp_frame, (x - w, y + h), (x + w, y - h), (0, 255, 0), 2)
        if points_dist(center_rat, node) < 30:
            self.logger.info('Recording Trial {}'.format(self.trial_num))
            print('\n\n >>>> Start Trial {}'.format(self.trial_num))
            print('\nDistance researcher-rat start', round(points_dist(center_rat, node)))
            # Handle first trial Ephys, probe and NGL special trials types - start time to run the timer
            if self.trial_num == 1 and int(self.trial_type) != 1:
                self.start_time = (self.frame_time / (1000 * 60)) % 60
                if int(self.trial_type) == 3:
                    self.probe = True
                    print('\n >>> Start 10 minutes trial ephys: ', self.start_time)
                if int(self.trial_type) == 2:
                    self.NGL = True
                    print('\n >>> Start New Goal location trial', self.start_time)
            if int(self.trial_type) == 4:
                for n in self.special_trials:
                    if int(n) == self.trial_num:
                        self.NGL = True
                        self.start_time = (self.frame_time / (1000 * 60)) % 60
                        print('\n >>> Start 10 minutes trial ephys: ', self.start_time)
            if not self.probe and not self.NGL:
                    self.normal_trial = True
            self.counter += 1
            self.node_pos = []
            self.centroid_list = []
            self.time_points = []
            self.summary_trial = []
            self.saved_nodes = []
            self.node_id = []  ##node num
            self.saved_velocities = []
            self.record_detections = True  # start object detection
            self.pos_centroid = node
            self.centroid_list.append(self.pos_centroid)
            self.start_trial = False  # make sure proximitycheck set to false for next start node and

    def cnn(self, frame):
        # input to the CNN - blob.shape: (1, 3, 416, 416)
        image_blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416), swapRB=True, crop=False)
        # Run inference
        layers_result = self.session.run([self.output_name_1, self.output_name_2], {self.input_name: image_blob})
        layers_result = np.concatenate([layers_result[1], layers_result[0]], axis=1)
        boxes, confidences, class_ids, centroids = [], [], [], []
        # Convert layers_result to bbox, confs and classes
        height, width = frame.shape[0], frame.shape[1]
        # Go through the detections after filtering out the one with confidence > 0.8
        matches = layers_result[
            np.where(np.max(layers_result[:, 4:], axis=1) > 0.7)]  # boxes, confidences, class_ids, centroids
        for detect in matches:
            scores = detect[4:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            center_x = int(detect[0] * width)
            center_y = int(detect[1] * height)
            w = int(detect[2] * width)
            h = int(detect[3] * height)
            x = int(center_x - w / 2)
            y = int(center_y - h / 2)
            centroids.append((center_x, center_y))
            boxes.append([x, y, w, h])
            confidences.append(float(confidence))
            class_ids.append(class_id)
        # Apply non-max suppression- eliminate double boxes keep boxes with higher confidence threshold - > 0.9, nms_threshold - > 0.3
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.9, 0.3)
        self.Rat = None  # keep rat head position, if none, takes rat body instead
        self.Researcher = None
        if len(indexes) > 0:  # indices box= box[i], x=box[0],y=box[1],w=[box[2],h=box[3]]
            for i in indexes.flatten():  # Return a copy of the array collapsed into one dimension
                x, y, w, h = boxes[i]  # Get box coordinates
                label = str(self.classes[class_ids[i]])
                confidence = str(round(confidences[i], 2))
                color = colors[i]  # Different color for each detected object
                cv2.rectangle(self.disp_frame, (x, y), (x + w, y + h), color, 2)  # Bounding box and label object
                cv2.putText(self.disp_frame, label + " " + confidence, (x, y + 20), font, 1, (255, 255, 255), 1)

                # Check rat-researcher  proximity only when the training trial is not running
                if label == 'researcher':
                    # not check for start first trial - self.start_trial=True
                    if not self.check and not self.start_trial and not self.end_session and not self.record_detections:
                        self.check = True
                    if self.check:
                        self.Researcher = centroids[i]
                        print('\n Checking proximity...')
                        # Researcher and rat close > start detections on new start node
                        if self.Researcher is not None and self.Rat is not None and points_dist(self.Rat,
                                                                                                self.Researcher) <= 900:
                            self.start_trial = True
                            print('\n\n >>> Proximity Checked > start new trial')
                            self.trial_num += 1
                            self.check = False

                # Get box centroid if label object is head - main object to detect, if None take centroid rat body
                if label == 'head':
                    self.Rat = centroids[i]
                    if self.Rat is not None:
                        # Wait researcher proximity before start new trial
                        # If start of trial wait until rat is placed in new start node
                        if self.start_trial:
                            self.find_start(self.Rat)
                        # condition to save nodes
                        if self.record_detections:
                            self.count_head += 1
                            self.object_detection(rat=self.Rat)

                # Get box centroid if label object is rat [body + tail] if nohead etected
                if label == 'rat':
                    if self.Rat is None:  # get centroid of rat body only if rat head is not detected
                        self.Rat = centroids[i]  # center of bounding box (x,y)
                        if self.start_trial:
                            self.find_start(self.Rat)
                        if self.record_detections:
                            if self.Rat is None:
                                self.Rat = self.centroid_list[-1]
                            self.count_rat += 1
                            self.object_detection(rat=self.Rat)

    def object_detection(self, rat):
        self.pos_centroid = rat
        self.centroid_list.append(self.pos_centroid)
        # New Goal location trial: first trial 10 minutes long
        if self.NGL:
            # Keep minutes passed for 10 min trials
            minutes = self.timer(start=self.start_time)
            if not self.reached:
                if points_dist(self.pos_centroid, self.goal_location) <= 20:
                    self.reached = True
            if minutes >= 10:
                print('n\n\n >>> Ten minute passed... Goal location reached:', self.reached)
                # If not reached wait till the rat is guided towards it
                if self.reached:
                    print('n\n\n >>> End New Goal Location Trial - timeout', self.trial_num, ' out of ',
                          self.num_trials)
                    self.NGL = False
                    self.reached = False
                    self.end_trial()

        # Probe trial: look for goal location reached after first 2 minutes
        if self.probe:
            # Keep minutes passed for 2min probe trials
            minutes = self.timer(start=self.start_time)
            if minutes >= 2:
                if points_dist(self.pos_centroid, self.goal_location) <= 20:
                    print('\n\n >>> End Probe trial', self.trial_num, ' out of ', self.num_trials, '\nCount rat',
                          self.count_rat, ' head', self.count_head)
                    self.probe = False
                    self.end_trial()

        # Normal training - Check if rat reached Goal location
        if self.normal_trial:
            if points_dist(self.pos_centroid, self.goal_location) <= 20:
                print('\n\n >>> Goal location reached. End of trial ', self.trial_num, ' out of ', self.num_trials,
                      '\nCount rat', self.count_rat, ' head', self.count_head)
                self.normal_trial = False
                self.end_trial()

    def end_trial(self):
        # make sure last node is saved and written to file before self.record_detections = False
        self.pos_centroid = self.goal_location
        self.centroid_list.append(self.pos_centroid)
        self.annotate_frame(self.disp_frame)
        # if rat reached goal node calculate velocities and save to file
        # Save last centroid position in log file
        if self.saved_nodes:
            self.logger.info(
                f'{self.converted_time} : The rat position is: {self.pos_centroid} @ {self.saved_nodes[-1]}')
        else:
            self.logger.info(
                f'{self.converted_time} : The rat position is: {self.pos_centroid}')  # pos_centroid
        self.calculate_velocity(self.time_points)
        self.save_to_file(self.save)
        # Check if session is finished
        if self.counter == int(self.num_trials):
            print('\n >>>>>>  Session ends with', self.counter, ' trials. Last trial number', self.trial_num)
            self.end_session = True
        self.record_detections = False
        self.count_rat = 0
        self.count_head = 0

    # Timer for new goal location and probe trials
    def timer(self, start):
        end = (self.frame_time / (1000 * 60)) % 60
        duration = end - start
        if duration < 0:
            duration = duration + 60
        print('Timer:', round(duration, 2), 'minutes')
        return int(duration)

    def calculate_velocity(self, time_points):
        # Calculate rat speed between two consecutive nodes
        bridges = {('124', '201'): 0.60,
                   ('121', '302'): 1.72,
                   ('223', '404'): 1.69,
                   ('324', '401'): 0.60,
                   ('305', '220'): 0.60}
        if len(time_points) > 2:
            lenght = 0
            speed = 0
            # self.first_node = time_points[0][1]
            format = '%H:%M:%S.%f'
            # first_time=((time_points[i][0])/ 1000) % 60
            # iterate over list of touple with time points and nodes IDs
            # grab start time and node name and next node
            for i in range(0, len(time_points)):
                start_node = time_points[i][1]
                start_time = datetime.strptime((time_points[i][0]), format).time()
                j = i + 1
                if j == len(time_points):
                    self.last_node = time_points[i][1]
                else:
                    end_node = time_points[j][1]
                    end_time = datetime.strptime((time_points[j][0]), format).time()
                    difference = timedelta(hours=end_time.hour - start_time.hour,
                                           minutes=end_time.minute - start_time.minute,
                                           seconds=end_time.second - start_time.second,
                                           microseconds=end_time.microsecond - start_time.microsecond).total_seconds()
                    if (start_node, end_node) in bridges:
                        lenght = bridges[(start_node, end_node)]

                    elif (end_node, start_node) in bridges:
                        lenght = bridges[(end_node, start_node)]

                    else:
                        lenght = 0.30  # 30cm within islands
                    try:
                        speed = round(float(lenght) / float(difference), 3)
                    # Avoid errors accept division by 0
                    except ZeroDivisionError:
                        speed = 0
                    # Save calculated data to be passed to save_to_file function
                    finally:
                        self.summary_trial.append(
                            [(start_node, end_node), (time_points[i][0], time_points[j][0]), difference, lenght, speed])
                        self.saved_velocities.append(speed)

    @staticmethod
    def annotate_node(frame, point, node, t):
        '''Annotate traversed nodes on to the frame
        Input: Frame (to be annotated), Point: x, y coords of node, Node: Node name, t 1=start,2=walked,3=goal
        '''
        if t == 1:
            cv2.circle(frame, point, 20, color=(0, 255, 0), thickness=2)
            cv2.putText(frame, str(node), (point[0] - 16, point[1]),
                        fontScale=0.5, fontFace=FONT, color=(0, 255, 0), thickness=1,
                        lineType=cv2.LINE_AA)
            cv2.putText(frame, 'Start', (point[0] - 16, point[1] - 22),
                        fontScale=0.5, fontFace=FONT, color=(0, 255, 0), thickness=1,
                        lineType=cv2.LINE_AA)

        if t == 2:
            cv2.circle(frame, point, 20, color=(20, 110, 245), thickness=1)
            cv2.putText(frame, str(node), (point[0] - 16, point[1]),
                        fontScale=0.5, fontFace=FONT, color=(0, 69, 255), thickness=1,
                        lineType=cv2.LINE_AA)
        if t == 3:
            cv2.circle(frame, point, 20, color=(0, 0, 250), thickness=2)
            cv2.putText(frame, str(node), (point[0] - 16, point[1]),
                        fontScale=0.5, fontFace=FONT, color=(0, 0, 255), thickness=1,
                        lineType=cv2.LINE_AA)
            cv2.putText(frame, 'End', (point[0] - 16, point[1] - 22),
                        fontScale=0.5, fontFace=FONT, color=(0, 0, 255), thickness=1,
                        lineType=cv2.LINE_AA)

    def annotate_frame(self, frame):
        '''
        Annotates frame with frame information, path and nodes registered
        '''

        # Dictionary of node names and corresponding coordinates
        nodes_dict = mask.create_node_dict(self.node_list)
        # Annotate time, fps and goal node of the session
        cv2.putText(frame, str(self.converted_time), (970, 670),
                    fontFace=FONT, fontScale=0.75, color=(240, 240, 240), thickness=1)
        fps = 1. / (time.time() - self.t1) # calculate tracking speed in fps
        self.store_fps.append(fps)
        cv2.putText(frame, "FPS: {:.2f}".format(fps), (970, 650), fontFace=FONT, fontScale=0.75, color=(240, 240, 240),
                    thickness=1)
        self.annotate_node(frame, point=self.goal_location, node=self.goal, t=3)
        # Frame annotations while waiting rat to be placed in next start node
        if self.start_trial:
            cv2.putText(frame, 'Next trial:' + str(self.counter + 1), (60, 60),
                        fontFace=FONT, fontScale=0.75, color=(255, 255, 255), thickness=1)
            cv2.putText(frame, 'Waiting start new trial...', (60, 80),
                        fontFace=FONT, fontScale=0.75, color=(255, 255, 255), thickness=1)

            self.annotate_node(frame, point=self.start_nodes_locations[self.counter],
                               node=self.start_nodes[self.counter], t=1)

            # Frame annotations during recording
        if self.record_detections:
            # if the centroid position of rat is within 20 pixels of any node
            # register that node to a list.
            for node_name in nodes_dict:
                if points_dist(self.pos_centroid, nodes_dict[node_name]) <= 20:
                    self.saved_nodes.append(node_name)
                    self.node_pos.append(nodes_dict[node_name])
                    print('\nTrial', self.trial_num, ' Node', node_name, '\nTime', self.converted_time, ' FPS',
                          round(fps, 3))

                    # Save timepoints for speed calculation - self.calculate_velocity(self.time_points)
                    if len(self.time_points) == 0:
                        self.time_points.append([self.converted_time, node_name])
                    if node_name != self.saved_nodes[(len(self.saved_nodes)) - 2]:
                        self.time_points.append([self.converted_time, node_name])

            # Draw text in frame during trial
            cv2.putText(frame, 'Trial:' + str(self.trial_num), (60, 60),
                        fontFace=FONT, fontScale=0.75, color=(255, 255, 255), thickness=1)
            cv2.putText(frame, 'Currently writing to file...', (60, 80),
                        fontFace=FONT, fontScale=0.75, color=(255, 255, 255), thickness=1)
            cv2.putText(frame, "Rat Count: " + str(self.count_rat), (40, 130),
                        fontFace=FONT, fontScale=0.65, color=(255, 255, 255), thickness=1)
            cv2.putText(frame, "Rat-head Count: " + str(self.count_head), (40, 160),
                        fontFace=FONT, fontScale=0.65, color=(255, 255, 255), thickness=1)

            # Draw the path that the rat has traversed [centroid = head trace]
            if len(self.centroid_list) >= 2:
                for i in range(1, len(self.centroid_list)):
                    cv2.line(frame, self.centroid_list[i], self.centroid_list[i - 1],
                             color=(255, 0, 60), thickness=1)
                    # draw green cross to marc centroid position
            cv2.line(frame, (self.pos_centroid[0] - 5, self.pos_centroid[1]),
                     (self.pos_centroid[0] + 5, self.pos_centroid[1]),
                     color=(0, 255, 0), thickness=2)
            cv2.line(frame, (self.pos_centroid[0], self.pos_centroid[1] - 5),
                     (self.pos_centroid[0], self.pos_centroid[1] + 5),
                     color=(0, 255, 0), thickness=2)

            # Annotate all nodes the rat has traversed
            for i in range(0, len(self.saved_nodes)):
                self.annotate_node(frame, point=self.node_pos[i], node=self.saved_nodes[i],
                                   t=2)  # t=2 walked node during the trial

    # Save recorded nodes and calculated timepoints and velocities to file
    def save_to_file(self, fname):
        savelist = []
        print('\nNode crossed')
        with open(fname, 'a+') as file:
            for k, g in groupby(self.saved_nodes):
                savelist.append(k)
                print('{}'.format(k))
            file.writelines('%s,' % items for items in savelist)
            file.write(
                '\nSummary Trial {}\nStart-Next Nodes// Time points(s) //Seconds//Lenght(cm)// Velocity(m/s)\n'.format(
                    self.trial_num))
            print(
                '\nSummary Trial {}\nStart-Next Nodes// Time points(s) //Seconds//Lenght(cm)// Velocity(m/s)\n'.format(
                    self.trial_num))
            for i in range(0, len(self.summary_trial)):
                line = " ".join(map(str, self.summary_trial[i]))
                file.write(line + '\n')
                print(line + '\n')
            file.write('\n')
        file.close()

    def find_location(self, start_nodes, goal):
        nodes_dict = mask.create_node_dict(self.node_list)
        start_nodes_locations = []
        for node_name in nodes_dict:
            if node_name == str(goal):
                self.goal_location = nodes_dict[node_name]
        for node in start_nodes:
            for node_name in nodes_dict:
                if node_name == str(node):
                    start_nodes_locations.append(nodes_dict[node_name])
        return start_nodes_locations


if __name__ == "__main__":
    today = date.today()
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='OpenCV video processing')
    parser.add_argument('-i', "--input", dest='vid_path', help='full path to input video that will be processed')
    parser.add_argument('-o', "--output", dest='output', help='full path for saving processed video output')
    args = parser.parse_args()
    if args.vid_path is None:  # or args.output is None
        sys.exit("Please provide path to input and output video files! See --help")
    print('\nVideo path', args.vid_path, 'Logs output', args.output)  # , 'save to ', args.output

    node_list = Path('tools/node_list_new.csv').resolve()
    print('\n\nTracker version: v2.00\n\n')

    Tracker(vp=args.vid_path, nl=node_list, out=args.output)
    #Tracker(vp="/home/genzel/Desktop/Scripts/TRACKER/tracker/stitched.mp4", nl=node_list, out='/home/genzel/Desktop/Scripts/TRACKER/tracker')
