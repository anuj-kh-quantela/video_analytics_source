import cv2
import numpy as np
import time
import sys
import datetime


class AbandonedObjects(object):

	@staticmethod
	def detect_abandoned_objects(records):
		"""
		<analytics_description>

		"""

		# TO-DO: 

		'''
		- bounding box: to be stored in a shared memory
		- some other meta info to be pushed to HTTP end-point
		'''


		# default algo variables

		print("INSIDE Abandoned Object CLASS")
		# sys.exit()
		
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