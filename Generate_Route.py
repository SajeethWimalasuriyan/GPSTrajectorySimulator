"""
Designed and built by Sajeeth Wimalasuriyan and Jue Wang.
Property of the University of Toronto Mississauga.
"""

#Imports
import arcpy
import random
import math
import datetime 

#Global UI parameters.
spatial_ref = int(arcpy.GetParameter(0))#Grabs number of wanted activity locations.
bufferSize = arcpy.GetParameter(1)#Grabs buffer size.
datasetAmount = arcpy.GetParameter(2)#Grabs number of datasets a user wants.
gpsNoise = arcpy.GetParameter(3)#Grabs extend of GPS noise user wants in dataset in M.
if gpsNoise > 1:
	gpsNoise = 1 + (gpsNoise/10)#Scales the Noise to be in Meters.
minTime = arcpy.GetParameter(4)#Grabs min time for activity locations. 
maxTime = arcpy.GetParameter(5)#Grabs the max time for activity locations.
minTimeWork = arcpy.GetParameter(6)#Grabs min time for work locations. 
maxTimeWork = arcpy.GetParameter(7)#Grabs max time for work locations. 
minTimeHome = arcpy.GetParameter(8)#Grabs min time for the home location. 
maxTimeHome = arcpy.GetParameter(9)#Grabs max time for the home location.
pointNumber = arcpy.GetParameter(10)#Points per second.

#Global operational parameters.
homePoint = ''#Stores home point in dataset.
workPoint = ''#Stores work point in dataset.
randomHouse = 10#Stores random ID of home location.
randomWork = 10#Stores random ID of work location.

class SyntheticGPSTrajectory():
	"""
	Contains all functions necessary to create a synthetic GPS dataset.
	"""

	def __init__(self,DataSetNumber):
		"""
		Initialize object.
		"""
		self.Internal_Count = DataSetNumber#Current dataset being made.

	def fcs_in_workspace(self):  
		"""
		Exploits ArcGIS data storage format to extract hidden files 
		necessary for the creation of synthetic datasets.
		"""
		workspace = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb"
		walk = arcpy.da.Walk(workspace, datatype="FeatureClass", type="Polyline")#Allows program to peer into filestructure.
		mainDir = '';
		dirOfDirection = '';
		dirStops = '';
		#Below code looks for files of interest within randomly generated dataset.
		for dirpath, dirnames, filenames in walk:
			mainDir = dirpath 
			for filename in filenames:
				if 'DirectionLines' in str(filename):
					dirOfDirection = mainDir + "\\" + filename
		walk = arcpy.da.Walk(workspace, datatype="FeatureClass", type="Point")
		for dirpath, dirnames, filenames in walk:
			for filename in filenames:
				if 'Stops' in str(filename):
					dirStops = mainDir + "\\" + filename
		return (mainDir,dirOfDirection,dirStops)

	def Find_Point(self):
		"""
		Determines random home and work location to be used in the output dataset. 
		Adds random points to the dataset and creates a line between them that has 
		a buffer specified by the user around it (represents the total extent of the dataset).
		"""
		HomesLoc = r"C:\SyntheticGPSTrajectory\WorkSpace\WherePeopleLive.shp"
		WorkLoc = r'C:\SyntheticGPSTrajectory\WorkSpace\Work.shp'
		Homes = r'C:\SyntheticGPSTrajectory\WorkSpace\Homes.shp'
		Works = r'C:\SyntheticGPSTrajectory\WorkSpace\Works.shp'

		#Below control flow uses zoning datasets to create potential home and work locations then chooses random locations.
		if arcpy.Exists(Homes):
			arcpy.Delete_management(Homes)
			arcpy.FeatureToPoint_management(HomesLoc, Homes,"CENTROID")
		else:
			arcpy.FeatureToPoint_management(HomesLoc, Homes,"CENTROID")
		randomHouse = random.randrange(int(arcpy.GetCount_management(Homes)[0]))

		if arcpy.Exists(Works):
			arcpy.Delete_management(Works)
			arcpy.FeatureToPoint_management(WorkLoc, Works,"CENTROID")
		else:
			arcpy.FeatureToPoint_management(WorkLoc, Works,"CENTROID")
		randomWork = random.randrange(int(arcpy.GetCount_management(Works)[0]))

		WorkSpace = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb"
		NewPointDataset = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\habitatareas"
		arcpy.CreateFeatureclass_management(WorkSpace, 'habitatareas', 'POINT')

		fields = ['SHAPE@XY']
		count = 0#Used to track and find points of interest.
		#Code below grabs houses from Homes dataset.
		with arcpy.da.UpdateCursor(Homes, fields) as cursor:
			for row in cursor:
				old_X = float(row[0][0])
				old_Y = float(row[0][1])
				count = count + 1
				if randomHouse == count:
					homePoint = ("HOME", 100, arcpy.Point(old_X, old_Y))#Saves randomly chosen home location.
		count = 0#Used to track and find points of interest.
		#Code below grabs workplaces from Work dataset.
		with arcpy.da.UpdateCursor(Works, fields) as cursor:
			for row in cursor:
				old_X = float(row[0][0])
				old_Y = float(row[0][1])
				count = count + 1
				if randomWork == count:
					workPoint = ("WORK", 100, arcpy.Point(old_X, old_Y))#Saves randomly chosen work location.

		#Below new feature class is created containing work and home locations.
		arcpy.AddField_management(NewPointDataset, "NAME", "TEXT")
		arcpy.AddField_management(NewPointDataset, "NEAR_DIST", "LONG")
		cursor = arcpy.da.InsertCursor(NewPointDataset, ["NAME","NEAR_DIST","SHAPE@XY"])
		xy = homePoint
		cursor.insertRow(xy)
		cursor.insertRow(workPoint)
		# Delete cursor object
		del cursor
		betweenWorkAndHome = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\WorkNHome"
		betweenWorkAndHomeBuffer = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\WorkNHomeBuffer"
		temp = r'C:\SyntheticGPSTrajectory\WorkSpace\temp.shp'
		BufferStorage = r'C:\SyntheticGPSTrajectory\WorkSpace\BufferStorage.shp'
		arcpy.Copy_management(Homes, temp)
		arcpy.DeleteFeatures_management(temp)
		arcpy.AddField_management(temp, "NAME", "TEXT")
		arcpy.AddField_management(temp, "NEAR_DIST", "LONG")
		cursor = arcpy.da.InsertCursor(temp, ["NAME","NEAR_DIST","SHAPE@XY"])
		xy = homePoint
		cursor.insertRow(xy)
		cursor.insertRow(workPoint)
		# Delete cursor object
		del cursor

		#Buffer between work and home point is made and cleanup occurs in code below.
		arcpy.PointsToLine_management(temp, BufferStorage)
		arcpy.Buffer_analysis(BufferStorage, betweenWorkAndHomeBuffer, str(bufferSize) + " Meters")
		arcpy.Delete_management(temp)
		arcpy.Delete_management(BufferStorage)

	def Network_Analysis(self):
		"""
		Finds the optimal route between home, work, and activity locations
		based on input .nd file. Most of the geoprocessing necessary for the
		operation of the algorithm occurs here.
		"""
		# To allow overwriting outputs change overwriteOutput option to True.
		arcpy.env.overwriteOutput = False
		# Check out any necessary licenses.
		arcpy.CheckOutExtension("Network")
		arcpy.CheckOutExtension("GeoStats")

		#Makes the route layer to enable route calculations.
		Network_Data_Source = r"C:\SyntheticGPSTrajectory\WorkSpace\roadnetwork\toronto_network_ND.nd"
		RandDest = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\RandomDestination"
		Route = arcpy.na.MakeRouteAnalysisLayer(network_data_source=Network_Data_Source,
		layer_name="RouteSKIA" +str(self.Internal_Count))

		torontoOutline =  r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\buffeting"
		workspaceForPoints = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb"
		betweenWorkAndHomeBuffer = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\WorkNHomeBuffer"

		arcpy.CreateRandomPoints_management(workspaceForPoints,"RandomDestination",betweenWorkAndHomeBuffer, 
		"",spatial_ref,"", "POINT") #This line of code controls the number of activity locations based on spatial_ref.

		final = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\finalDestinations"
		habitatareas = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\habitatareas"
		RandomPointsPlusHome = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\RandomPointsPlusHome"

		#Code below adds work, home and activity locations into 1 feature class.
		arcpy.Merge_management([habitatareas, RandDest],RandomPointsPlusHome)

		#Code below sets up a network analysis layer with all the stops (work, home and activity locations).
		Updated_Input_Network_Analysis_Layer = arcpy.AddLocations_na(in_network_analysis_layer=Route, sub_layer="Stops", 
		in_table=RandomPointsPlusHome, field_mappings="Name Name #", search_tolerance="5000 Meters", sort_field="", 
		search_criteria=[], match_type="MATCH_TO_CLOSEST", append="APPEND", snap_to_position_along_network="NO_SNAP", 
		snap_offset="5 Meters", exclude_restricted_elements="EXCLUDE", search_query=[])[0]

		#Code below finds the shortest route between home, work and activity locations.
		Network_Analyst_Layer, Solve_Succeeded = arcpy.Solve_na(in_network_analysis_layer=Updated_Input_Network_Analysis_Layer, 
		ignore_invalids="SKIP", terminate_on_solve_error="TERMINATE", simplification_tolerance="", overrides="")

		#Cleanup 
		arcpy.Delete_management(betweenWorkAndHomeBuffer)
		
	def Generate_Route(self):
		"""
		Orchestrates other methods to run the algorithm. The function also helps 
		to clean up after the algorithm is done (delete stopgap files).
		"""
		#Runs necessary function to assemple final output dataset.
		self.Find_Point()
		self.Network_Analysis()
		findr = self.fcs_in_workspace()
		PAL = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\PointAlongLine"
		arcpy.GeneratePointsAlongLines_management(findr[1], PAL, 'DISTANCE', Distance='210 meters')#210 was found to be optimal distance for subsequent steps.
		arcpy.Near_analysis(PAL, findr[2])
		self.Depth_Traversal(spatial_ref,findr)

		#Cleanup
		NewPointDataset = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\habitatareas"
		RandomPointsPlusHome = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\RandomPointsPlusHome"
		RandDest = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\RandomDestination"
		buffeting = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\buffeting"
		howFarFromHome = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\howFarFromHome"
		arcpy.Delete_management(RandomPointsPlusHome)
		arcpy.Delete_management(RandDest)
		arcpy.Delete_management(findr[0])
		arcpy.Delete_management(PAL)
		arcpy.Delete_management(NewPointDataset)
		arcpy.Delete_management(buffeting)
		arcpy.Delete_management(howFarFromHome)
	
	def Point_Scrambler(self,x,y,noise):
		"""
		Scrambles points to mimic GPS noise. The function can 
		also be used to space out points to help with timing operations.
		"""
		random_angle = random.uniform(0.0, math.pi*2)
		random_number = random.gauss(0,1)
		hypothenuse = random_number * (noise)
		delta_X = (math.cos(random_angle)) * hypothenuse
		delta_Y = (math.sin(random_angle)) * hypothenuse
		new_X = x + delta_X
		new_Y = y + delta_Y
		return [new_X,new_Y]

	def Internal_Clock(self,count):
		"""
		Manages time based on count. Restricted to one day, but can
		hand overflow up to 2 days.
		"""
		x = int(count) 
		day = 1
		if x > 1439:
			x = x - 1439
			day = 2
		hours = x // 60 #Truncating integer division.
		minutes = x % 60 #Modulo removes the upper digits.
		time = datetime.datetime(2009, 10, day,hours,minutes,0)
		return str(time)

	def Manage_Time(self, ppm):
		"""
		Helps to keep track of time based on the ppm (points per minute)
		specified by the user.
		"""
		if ppm < 60:
			return (ppm / 60.0) 
		else:
			return (ppm // 60) 

	def Assignment_Points(self,filePath):
		"""
		Finds the location of the home, work, and activity locations using proximity 
		to the reference dataset (done through utilizing critical points provided by filePath).
		"""
		for i in range(len(filePath)):#Runs through provided points of interest.

			PALPointStorage = []
			TemporaryWorkspace = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb"
			IndividualLocationTemporaryHold = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\IndividualLocationTemporaryHold"
			output = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\output"
			PAL = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\PointAlongLine"

			#Code below grabs each individual point from a list of points of interest and adds it to a new feature.
			arcpy.CreateFeatureclass_management(TemporaryWorkspace, 'IndividualLocationTemporaryHold', "POINT")
			arcpy.AddField_management(IndividualLocationTemporaryHold, "NAME", "TEXT")
			arcpy.AddField_management(IndividualLocationTemporaryHold, "NEAR_DIST", "TEXT")
			cursor = arcpy.da.InsertCursor(IndividualLocationTemporaryHold, ["NAME","NEAR_DIST","SHAPE@XY"])
			cursor.insertRow(filePath[i][0])
			del cursor #delete cursor

			#Run near analysis to find closest point on reference dataset to point of interest.
			arcpy.Near_analysis(PAL, IndividualLocationTemporaryHold)
			arcpy.Sort_management(PAL, output, [["NEAR_DIST", "ASCENDING"]])

			# Create update cursor for feature class 
			fields = ["SHAPE@XY"]
			with arcpy.da.UpdateCursor(output, fields) as cursor:
				for row in cursor:
					old_X = float(row[0][0])
					old_Y = float(row[0][1])
					PALPointStorage.append([old_X,old_Y])
					break
			del cursor #delete cursor

			#Finds equivilent point on reference dataset and labels accordingly as home, work or activity location.
			arcpy.AddField_management(PAL, "NAME", "TEXT")
			fields = ["SHAPE@XY", "NAME"]
			# Create update cursor for feature class 
			with arcpy.da.UpdateCursor(PAL, fields) as cursor:
				for row in cursor:
					old_X = float(row[0][0])
					old_Y = float(row[0][1])
					if float(PALPointStorage[0][0]) == old_X or float(PALPointStorage[0][1]) == old_Y:
						if (filePath[i][1] == 'HOME'):
							arcpy.AddMessage(filePath[i][1])
							row[1] = "HOME"
							cursor.updateRow(row) 
						elif (filePath[i][1] == 'WORK'):
							arcpy.AddMessage(filePath[i][1])
							row[1] = "WORK"
							cursor.updateRow(row) 	
						else:
							row[1] = "ACTIVITYLOCATION"
							arcpy.AddMessage(filePath[i][1])
							cursor.updateRow(row) 
			del cursor #delete cursor

			#cleanup
			arcpy.Delete_management(IndividualLocationTemporaryHold)
			arcpy.Delete_management(output)

	def Depth_Traversal(self,x,findr):
		"""
		Runs through network dataset that contains points along a route and 
		assigns timings along them and adds extra points where necessary. The
		function also determines where the home, work, and activity locations 
		need to be located and disperses points accordingly. Finally, the function 
		also determines the mode of transport randomly and adjusts the number of points 
		and timings accordingly. The final output dataset is made here.
		
		"""
		RandomPointsPlusHome = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\RandomPointsPlusHome"
		critPoints = [] #Critical points.

		#Below code finds points in RandomPointsPlusHome and labels them based on location type.
		fields = ["SHAPE@XY",'NAME']
		# Create update cursor for feature class 
		with arcpy.da.UpdateCursor(RandomPointsPlusHome, fields) as cursor:
			for row in cursor:
				old_X = float(row[0][0])
				old_Y = float(row[0][1])
				if (row[1] == 'HOME'):
					critPoints.append([("HOME", 100, arcpy.Point(old_X, old_Y)),"HOME"])	
				elif (row[1] == 'WORK'):
					critPoints.append([("WORK", 100, arcpy.Point(old_X, old_Y)),"WORK"])	
				else:
					row[1] = "ACTIVITYLOCATION"
					cursor.updateRow(row) 
					critPoints.append([("ACTIVITYLOCATION", 100, arcpy.Point(old_X, old_Y)),"ACTIVITYLOCATION"])
		del cursor, row #delete cursor

		self.Assignment_Points(critPoints)#Calls auxiliary function.

		s = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\PointAlongLine"
		xy = []#Stores points that will be added to final output dataset

		fields = ['NEAR_DIST','OBJECTID']
		pointsPerSecond = pointNumber
		count = 0
		arcpy.AddField_management(s, "UTC_DATE", "TEXT")
		fields = ['SHAPE@XY','OBJECTID','UTC_DATE','NAME']
		with arcpy.da.UpdateCursor(s, fields) as cursor:
			modeOfTransport = [10,8,5]#10 is a car @ 60km/h, 3 is biking @12km/h and 1 is walking/running @5km/h.
			chosenTransport = 10#Default is set to car.
			for row in cursor:
				old_X = float(row[0][0])
				old_Y = float(row[0][1])

				if row[3] == "HOME":
					#If location is a house the appropriate amount of points are dispersed.
					for i in range(int((random.randint(minTimeHome,maxTimeHome) * 3600)/pointsPerSecond)): #3600 is a aribitrary number that allows scaling.
						#Code below runs a modified version of gaussian displacement to add noise and mimic GPS tracking.
						random_angle = random.uniform(0.0, math.pi*2)
						random_number = random.gauss(0,1)
						hypothenuse = random_number * (1/1200) * (gpsNoise/10)
						delta_X = (math.cos(random_angle)) * hypothenuse
						delta_Y = (math.sin(random_angle)) * hypothenuse
						new_X = old_X + delta_X
						new_Y = old_Y + delta_Y
						new_point = arcpy.Point(new_X,new_Y)
						Distance = math.sqrt(math.pow(delta_X, 2) + math.pow(delta_Y, 2))
						xy.append((self.Internal_Clock(count), arcpy.Point(new_X, new_Y)))#Adds points to final dataset list.
						count = count + self.Manage_Time(pointsPerSecond)#Increments based on time and points per second.
					chosenTransport = modeOfTransport[random.randint(0,2)]#Switches transport type randomly.

				elif row[3] == "WORK":
					#If location is a work the appropriate amount of points are dispersed.
					for i in range(int((random.randint(minTimeWork,maxTimeWork) * 3600)/pointsPerSecond)):#3600 is a aribitrary number that allows scaling.
						#Code below runs a modified version of gaussian displacement to add noise and mimic GPS tracking.
						random_angle = random.uniform(0.0, math.pi*2)
						random_number = random.gauss(0,1)
						hypothenuse = random_number * (1/925) * (gpsNoise/10)
						delta_X = (math.cos(random_angle)) * hypothenuse
						delta_Y = (math.sin(random_angle)) * hypothenuse
						new_X = old_X + delta_X
						new_Y = old_Y + delta_Y
						new_point = arcpy.Point(new_X,new_Y)
						Distance = math.sqrt(math.pow(delta_X, 2) + math.pow(delta_Y, 2))
						xy.append((self.Internal_Clock(count), arcpy.Point(new_X, new_Y)))#Adds points to final dataset list.
						count = count + self.Manage_Time(pointsPerSecond)#Increments based on time and points per second.
					chosenTransport = modeOfTransport[random.randint(0,2)]#Switches transport type randomly.

				elif row[3] == "ACTIVITYLOCATION":
					#If location is a activity location the appropriate amount of points are dispersed.
					for i in range(int((random.randint(minTime,maxTime) * 3600)/pointsPerSecond)):
						#Code below runs a modified version of gaussian displacement to add noise and mimic GPS tracking.
						random_angle = random.uniform(0.0, math.pi*2)
						random_number = random.gauss(0,1)
						hypothenuse = random_number * (1/500) * (gpsNoise/10)
						delta_X = (math.cos(random_angle)) * hypothenuse
						delta_Y = (math.sin(random_angle)) * hypothenuse
						new_X = old_X + delta_X
						new_Y = old_Y + delta_Y
						new_point = arcpy.Point(new_X,new_Y)
						Distance = math.sqrt(math.pow(delta_X, 2) + math.pow(delta_Y, 2))
						xy.append((self.Internal_Clock(count), arcpy.Point(new_X, new_Y)))#Adds points to final dataset list.
						count = count + self.Manage_Time(pointsPerSecond)#Increments based on time and points per second.
					chosenTransport = modeOfTransport[random.randint(0,2)]#Switches transport type randomly.
					
				else: 
					#Below conditional operator helps to control the amount of points per minute based on user input.
					iteration = 1
					if pointsPerSecond < 60:
						iteration = 60 - pointsPerSecond
					else:
						iteration = 4 - pointsPerSecond // 60

					#Points leading to points of interest are generated below.
					for i in range(int(int(iteration) * (11 - int(chosenTransport)))):#Scales to amount of points and based on speed of transport
						points = self.Point_Scrambler(old_X,old_Y,(0.7 * (gpsNoise/10))/1000)
						xy.append((self.Internal_Clock(count), arcpy.Point(points[0], points[1])))
						#10 makes average car speed around 50 clicks
						#15.5 km/h is for bike == 3 adjust the 10 below to make changes to timing
						count = count + (self.Manage_Time(pointsPerSecond) / chosenTransport)

		WorkSpace = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb"
		NewPointDataset = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\SyntheticGPSTrajectoryResult" + str(self.Internal_Count)

		#Generates final output file for algorithm.
		if arcpy.Exists(NewPointDataset):
			arcpy.Delete_management(NewPointDataset)
			arcpy.CreateFeatureclass_management(WorkSpace, 'SyntheticGPSTrajectoryResult' + str(self.Internal_Count), 'POINT')
			self.Internal_Count += 1
		else:
			arcpy.CreateFeatureclass_management(WorkSpace, 'SyntheticGPSTrajectoryResult' + str(self.Internal_Count), 'POINT')
			self.Internal_Count += 1
		arcpy.AddField_management(NewPointDataset, "UTC_DATE", "TEXT")#Adds critical field to new dataset.

		#Code below adds all created points in xy to final output data class.
		cursor = arcpy.da.InsertCursor(NewPointDataset,['UTC_DATE', 'SHAPE@XY'])		
		for row in xy:
			cursor.insertRow(row)
		# Delete cursor object
		del cursor

		#Cleanup
		arcpy.Delete_management(s)
		
#Runs program in ArcGIS Pro
if __name__ == '__main__':
	with arcpy.EnvManager(scratchWorkspace=r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb", 
	workspace=r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb"): #Set up environment and run code within it.
		for i in range(datasetAmount):#Loops to control the number of datasets made.
			runner = SyntheticGPSTrajectory(i)#Creates new object.
			runner.Generate_Route()#Runs object to create data.