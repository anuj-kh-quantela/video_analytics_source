#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Eudie and Anuj

"""
This class is to encapsulate all the video analytics module into a package


"""
from __future__ import print_function
from __future__ import absolute_import
import multiprocessing
import cv2
import time
import os
import numpy as np
import datetime
import json



class VideoAnalytics(object):

	def __init__(self, video_path, city_name, analytics_name, location_name=""):
		"""
		Purpose: this is to set/make a pre-defined directory structure for 
		storing output of VideoAnalytics. 
		The constructor has some optional and required parameters.
		
		required:
		--------
		city_name - name of the city for which to deploy
		analytics_name - name LIST of analytics 

		optional:
		--------
		location_name - this comes nested under the city name folder
		purpose: if location name for a city is also available then
		we make a directory with location name under the city name directory
		this way we can keep the output more grannular and separate
		
		"""

		

		# TO-DO: code to make the following
		
		'''
			video_analytics_output/<city_name>/<location_name>/
														|- analytics_1/date/
																		|- video_snippet/	
																		|- alert_files/
		* in production, we'd be pushing the alerts to an HTTP end-point so 
		there is no need to write the alerts to a directory																		

		'''	
		self.__video_path = video_path

		print('Init done')

	def __frame_reader(self, records):
		"""
		- read frames from videos and store it in a shared list
		- size of the list is restricted to: threshold_seconds * incoming video fps
		- threshold_seconds: could be a configurable parameter, taken from config file
		
		"""
		
		cap = cv2.VideoCapture(self.__video_path)

		count = 0
		
		while cap.isOpened():
			ret, frame = cap.read()
			if not ret is False:
				records.append(frame.copy())
				
				if len(records) > 150:
					records.pop(0)
				cv2.imshow("inside_insert_record", frame)
				count += 1
				k = cv2.waitKey(1)
				if k == 27:
					break
					cap.release()
					cv2.destroyAllWindows()
					
			else:
				records.pop(0)
				
				if len(records) == 0:
					cap.release()
					cv2.destroyAllWindows()
					break
		cap.release()
		cv2.destroyAllWindows()		




	def __detect_abandoned_objects(self, records):
		"""
		<analytics_description>

		"""

		# TO-DO: 

		'''
		- bounding box: to be stored in a shared memory
		- some other meta info to be pushed to HTTP end-point
		'''


		# default algo variables
		interval = 0
		count = 0
		nPixel = 100
		flag = 0

		fgbg_mog2 = cv2.createBackgroundSubtractorMOG2(nPixel,cv2.THRESH_BINARY,2)
		remove_shadow = True

		# my variables
		aban = None
		sub = None

		# aban_eval_time_flag = None
		aban_interval = None

		algo_start_time = datetime.datetime.now().time().strftime('%H:%M:%S')

		current_date = str(datetime.datetime.now().date())
		
		while True:
			print("YES, LENGTH: " + str(len(records)))
			if len(records)  > 0:
				frame = records[-1]
				

				cv2.imshow("original image", frame)
				gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
				count += 1

				fgmask = fgbg_mog2.apply((gray))
				if remove_shadow:
					fgmask[fgmask == 127] = 0

				back = fgbg_mog2.getBackgroundImage()
				cv2.imshow('Static Background', back)
				#________________ bgs over _________		

				if flag == 0:
					# initialize aban
					aban = cv2.absdiff(back, back)
					interval = 300
					flag = 10

				if ((flag == 10) and (count >= nPixel)):
					# count >= nPixel - meaning that the background has been successfully captured
					aban = back.copy()
					flag = 20

				start_time = datetime.datetime.strptime(algo_start_time, '%H:%M:%S')
				check_time = datetime.datetime.now().time().strftime('%H:%M:%S')
				end_time = datetime.datetime.strptime(check_time, '%H:%M:%S')
				diff = (end_time - start_time)
				# print("\nPrinting time: " +str((diff.seconds)))

				if(diff.seconds >= interval):
					aban = back.copy()
					algo_start_time = datetime.datetime.now().time().strftime('%H:%M:%S')


				if count >= nPixel:
					sub = cv2.absdiff(back, aban)
					# cv2.imshow("Abandoned Object", sub)
					
					ret, thresh1 = cv2.threshold(sub,127,255,cv2.THRESH_BINARY)
					kernel = np.ones((3,3),np.uint8)
					dilation = cv2.dilate(thresh1, kernel, iterations = 4)
					
					# further thresholding required to get a clearer distinction
					ret,thresh = cv2.threshold(dilation,127,255,0)
					im2, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
					
					# cv2.drawContours(frame, contours, -1, (0,255,0), 3)
					# cv2.imshow('dilation-cont', frame)
					test = frame.copy()
					if not contours:
						# if out is not None:
						# 	out.release()
						# 	out = None

						# aban_eval_time_flag = True
						aban_interval = True

					else:

						if aban_interval:
							aban_counter = 0

						aban_interval = False
						aban_counter += 1

						# if an object is present for more than
						# threshold frames, then make a boinding box 
						# and start video writer
						if aban_counter > 150:

							# merge contour logic remaining

							for cnt in contours:
								x,y,w,h = cv2.boundingRect(cnt)
								cv2.rectangle(frame, (x,y), (x+w,y+h), (0,0,255), 2)

					cv2.imshow("Processed Output Window", frame)
				count += 1
				k = cv2.waitKey(1)

				if k == 27:
					break
					cv2.destroyAllWindows()
			
			else:
				print('count:')
				

		cv2.destroyAllWindows()



	def __analytics_2(self):
		"""
		<analytics_description>

		"""

		# TO-DO: 

		'''
		- bounding box: to be stored in a shared memory
		- some other meta info to be pushed to HTTP end-point
		'''
		pass

	def __combined_analytics_output(self, shared_video_list, shared_output_list):
		"""
		Purpose: uses the shared_video_list of video frames(generated by the __frame_reader)
		and puts the bounding box in the shared_output_list on the frames 
		to display 
		"""
		pass

	def run(self):

		with multiprocessing.Manager() as manager:
			# creating a list in server process memory
			records = manager.list([])
			
			result_list = manager.list([[], []])
			
			# q = multiprocessing.Queue(maxsize=10)

			# creating new processes
			p1 = multiprocessing.Process(target=self.__frame_reader, args=(records, ))
			p1.daemon = True
			p1.start()

			p2 = multiprocessing.Process(target=self.__detect_abandoned_objects, args=(records, ))
			p2.start()


			p1.join()
			p2.join()



if __name__ == '__main__':

	
	# video_path = '/media/anuj/Work-HDD/WORK/CLOUD-DRIVE/Google-Drive/Computer-Vision/Sample-Videos/RTSP-supported-videos/obama.webm'
	video_path = '/media/anuj/Work-HDD/WORK/CLOUD-DRIVE/Google-Drive/Computer-Vision/Sample-Videos/Abandoned-Object/pets2006_1.avi'
	vo = VideoAnalytics(video_path, 'bangalore', 'test', 'indiranagar')
	vo.run()