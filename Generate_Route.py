
import arcpy
import random
import math
import datetime 

spatial_ref = int(arcpy.GetParameter(0)) #Grabs number of wanted activity locations.
bufferSize = arcpy.GetParameter(1) #Grabs buffer size
datasetAmount = arcpy.GetParameter(2)
gpsNoise = arcpy.GetParameter(3)
minTime = arcpy.GetParameter(4)
maxTime = arcpy.GetParameter(5)
minTimeWork = arcpy.GetParameter(6)
maxTimeWork = arcpy.GetParameter(7)
minTimeHome = arcpy.GetParameter(8)
maxTimeHome = arcpy.GetParameter(9)

homePoint = ''
workPoint = ''
randomHouse = random.randrange(100)

class SyntheticGPSTrajectory():
	def __init__(self,x):
		self.workspace = ' '
		self.Internal_Count = x

	def fcs_in_workspace(self):  

		"""
		Workaround for arcmaps lack of file extraction for route analysis datasets.
		"""
		workspace = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb"
		walk = arcpy.da.Walk(workspace, datatype="FeatureClass", type="Polyline")
		mainDir = '';
		dirOfDirection = '';
		dirStops = '';
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
		HomesLoc = r"C:\SyntheticGPSTrajectory\WorkSpace\WherePeopleLive.shp"
		WorkLoc = r'C:\SyntheticGPSTrajectory\WorkSpace\Work.shp'
		Homes = r'C:\SyntheticGPSTrajectory\WorkSpace\Homes.shp'
		Works = r'C:\SyntheticGPSTrajectory\WorkSpace\Works.shp'
		if arcpy.Exists(Homes):
			arcpy.Delete_management(Homes)
			arcpy.FeatureToPoint_management(HomesLoc, Homes,"CENTROID")

		else:
			arcpy.FeatureToPoint_management(HomesLoc, Homes,"CENTROID")
		if arcpy.Exists(Works):
			arcpy.Delete_management(Works)
			arcpy.FeatureToPoint_management(WorkLoc, Works,"CENTROID")

		else:
			arcpy.FeatureToPoint_management(WorkLoc, Works,"CENTROID")


		WorkSpace = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb"
		NewPointDataset = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\habitatareas"
		arcpy.CreateFeatureclass_management(WorkSpace, 'habitatareas', 'POINT')
		fields = ['SHAPE@XY']
		count = 0
		with arcpy.da.UpdateCursor(Homes, fields) as cursor:
		# Update the field used in Buffer so the distance is based on road 
		# type. Road type is either 1, 2, 3, or 4. Distance is in meters. 
			for row in cursor:
				old_X = float(row[0][0])
				old_Y = float(row[0][1])
				count = count + 1
				if randomHouse == count:
					homePoint = ("HOME", 100, arcpy.Point(old_X, old_Y))
		count = 0
		with arcpy.da.UpdateCursor(Works, fields) as cursor:
		# Update the field used in Buffer so the distance is based on road 
		# type. Road type is either 1, 2, 3, or 4. Distance is in meters. 
			for row in cursor:
				old_X = float(row[0][0])
				old_Y = float(row[0][1])
				count = count + 1
				if randomHouse == count:
					workPoint = ("WORK", 100, arcpy.Point(old_X, old_Y))



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
		arcpy.PointsToLine_management(temp, BufferStorage)



		arcpy.Buffer_analysis(BufferStorage, betweenWorkAndHomeBuffer, str(bufferSize) + " Meters")
		arcpy.Delete_management(temp)
		arcpy.Delete_management(BufferStorage)


	def Work_Plus_Activities(self):
		buffeting = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\buffeting"
		howFarFromHome = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\howFarFromHome"
		Homes = r"C:\SyntheticGPSTrajectory\WorkSpace\Homes.shp"
		homePoly = 's'
		WorkSpace = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb"
		arcpy.Buffer_analysis(Homes, howFarFromHome, "3000 Meters")
		fields = ['SHAPE@']
		count = 0
		with arcpy.da.UpdateCursor(howFarFromHome, fields) as cursor:
		# Update the field used in Buffer so the distance is based on road 
		# type. Road type is either 1, 2, 3, or 4. Distance is in meters. 
		
		
			for row in cursor:
				count += 1
				if randomHouse == count:
					homePoly = row 

		arcpy.CreateFeatureclass_management(WorkSpace, 'buffeting', 'POLYGON')
		cursor = arcpy.da.InsertCursor(buffeting,("SHAPE@"))
		cursor.insertRow(homePoly)

		# Delete cursor object
		del cursor



	def Network_Analysis(self):
		# To allow overwriting outputs change overwriteOutput option to True.
		arcpy.env.overwriteOutput = False

		# Check out any necessary licenses.
		arcpy.CheckOutExtension("Network")
		arcpy.CheckOutExtension("GeoStats")
		Network_Data_Source = r"C:\SyntheticGPSTrajectory\WorkSpace\roadnetwork\toronto_network_ND.nd"
		RandDest = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\RandomDestination"
		Route = arcpy.na.MakeRouteAnalysisLayer(network_data_source=Network_Data_Source, layer_name="RouteSKIA" +str(self.Internal_Count))
		torontoOutline =  r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\buffeting"
		workspaceForPoints = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb"
		# Process: Add Locations (Add Locations) 
		betweenWorkAndHomeBuffer = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\WorkNHomeBuffer"

		arcpy.CreateRandomPoints_management(workspaceForPoints,"RandomDestination",betweenWorkAndHomeBuffer, "",3,"", "POINT")
		# Process: Solve (Solve) 
		final = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\finalDestinations"

		habitatareas = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\habitatareas"
		RandomPointsPlusHome = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\RandomPointsPlusHome"
		arcpy.Merge_management([habitatareas, RandDest], 
	                       RandomPointsPlusHome)
		Updated_Input_Network_Analysis_Layer = arcpy.AddLocations_na(in_network_analysis_layer=Route, sub_layer="Stops", in_table=RandomPointsPlusHome, field_mappings="Name Name #", search_tolerance="5000 Meters", sort_field="", search_criteria=[], match_type="MATCH_TO_CLOSEST", append="APPEND", snap_to_position_along_network="NO_SNAP", snap_offset="5 Meters", exclude_restricted_elements="EXCLUDE", search_query=[])[0]

		Network_Analyst_Layer, Solve_Succeeded = arcpy.Solve_na(in_network_analysis_layer=Updated_Input_Network_Analysis_Layer, ignore_invalids="SKIP", terminate_on_solve_error="TERMINATE", simplification_tolerance="", overrides="")
		
		arcpy.Delete_management(betweenWorkAndHomeBuffer)
		



	def Generate_Route(self):

		

		
		self.Find_Point()
		
		self.Work_Plus_Activities()
		
		self.Network_Analysis()
		findr = self.fcs_in_workspace()
		PAL = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\PointAlongLine"
		arcpy.GeneratePointsAlongLines_management(findr[1], PAL, 'DISTANCE', Distance='210 meters')
		arcpy.Near_analysis(PAL, findr[2])
		NewPointDataset = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\habitatareas"
		RandomPointsPlusHome = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\RandomPointsPlusHome"
		RandDest = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\RandomDestination"
		buffeting = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\buffeting"
		howFarFromHome = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\howFarFromHome"


		self.Depth_Traversal(spatial_ref,findr)

		arcpy.Delete_management(RandomPointsPlusHome)
		arcpy.Delete_management(RandDest)
		arcpy.Delete_management(findr[0])
		arcpy.Delete_management(PAL)
		arcpy.Delete_management(NewPointDataset)
		arcpy.Delete_management(buffeting)
		arcpy.Delete_management(howFarFromHome)
		
		
		"""
		REMEMBER TO DELETE THE OLD GDB FILES FROM THE RANDOME DATASET IT MAKES
		"""
	def Point_Scrambler(self,x,y,noise):
		random_angle = random.uniform(0.0, math.pi*2)
		random_number = random.gauss(0,1)
		hypothenuse = random_number * (noise)
		delta_X = (math.cos(random_angle)) * hypothenuse
		delta_Y = (math.sin(random_angle)) * hypothenuse
		new_X = x + delta_X
		new_Y = y + delta_Y
		return [new_X,new_Y]

	def Internal_Clock(self,count):
		x = int(count) 
		day = 1
		if x > 1439:
			
			x = x - 1439
			day = 2
		hours = x // 60  # Truncating integer division
		minutes = x % 60  # Modulo removes the upper digits

		time = datetime.datetime(2009, 10, day,hours,minutes,0)
		return str(time)
	def Manage_Time(self, time):
		if time < 60:
			return (time / 60.0) 
		else:
			return (time // 60) 
	def Assignment_Points(self,filePath):
		"""
		Adds the activity locations and the home/work locations 
		Run through the file containing all activity locations
		grab 1 point at a time and find lowest dist to point than 
		name the nearest point based on inp point.
				arcpy.Near_analysis(PAL, findr[2])




				REMAINING TASKS FEED THE NEW FILES LABELED INTO THE TIMER MAKE SURE THIS WORKS PROPERLY DIDNT WORK LAST TIME
		"""
		for i in range(len(filePath)):

			PALPointStorage = []
			TemporaryWorkspace = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb"
			IndividualLocationTemporaryHold = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\IndividualLocationTemporaryHold"
			output = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\output"
			PAL = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\PointAlongLine"
			arcpy.CreateFeatureclass_management(TemporaryWorkspace, 'IndividualLocationTemporaryHold', "POINT")
			arcpy.AddField_management(IndividualLocationTemporaryHold, "NAME", "TEXT")
			arcpy.AddField_management(IndividualLocationTemporaryHold, "NEAR_DIST", "TEXT")
			cursor = arcpy.da.InsertCursor(IndividualLocationTemporaryHold, ["NAME","NEAR_DIST","SHAPE@XY"])
			cursor.insertRow(filePath[i][0])
			del cursor
			arcpy.Near_analysis(PAL, IndividualLocationTemporaryHold)
			arcpy.Sort_management(PAL, output, [["NEAR_DIST", "ASCENDING"]])
			fields = ["SHAPE@XY"]
			# Create update cursor for feature class 
			with arcpy.da.UpdateCursor(output, fields) as cursor:
			# Update the field used in Buffer so the distance is based on road 
			# type. Road type is either 1, 2, 3, or 4. Distance is in meters. 

				for row in cursor:
					old_X = float(row[0][0])
					old_Y = float(row[0][1])
					PALPointStorage.append([old_X,old_Y])
					break
			del cursor
			arcpy.AddField_management(PAL, "NAME", "TEXT")


			fields = ["SHAPE@XY", "NAME"]
			# Create update cursor for feature class 
			with arcpy.da.UpdateCursor(PAL, fields) as cursor:
			# Update the field used in Buffer so the distance is based on road 
			# type. Road type is either 1, 2, 3, or 4. Distance is in meters. 

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
  
						

			del cursor
			arcpy.Delete_management(IndividualLocationTemporaryHold)
			arcpy.Delete_management(output)






	def Depth_Traversal(self,x,findr):
		RandomPointsPlusHome = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\RandomPointsPlusHome"


		critPoints = []

		fields = ["SHAPE@XY",'NAME']
		# Create update cursor for feature class 
		with arcpy.da.UpdateCursor(RandomPointsPlusHome, fields) as cursor:
		# Update the field used in Buffer so the distance is based on road 
		# type. Road type is either 1, 2, 3, or 4. Distance is in meters. 
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
		



		

		del cursor, row
		arcpy.AddMessage(critPoints)
		self.Assignment_Points(critPoints)

		s = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\PointAlongLine"



		xy = []
		fields = ['NEAR_DIST','OBJECTID']
		pointsPerSecond = 120

	
		count = 0
		arcpy.AddField_management(s, "UTC_DATE", "TEXT")
		fields = ['SHAPE@XY','OBJECTID','UTC_DATE','NAME']
		with arcpy.da.UpdateCursor(s, fields) as cursor:
		# Update the field used in Buffer so the distance is based on road 
		# type. Road type is either 1, 2, 3, or 4. Distance is in meters. 
			modeOfTransport = [10,8,5] #10 is a car @ 60km/h, 3 is biking @12km/h and 1 is walking/running @5km/h
			chosenTransport = 'car'
			for row in cursor:
				old_X = float(row[0][0])
				old_Y = float(row[0][1])
				if row[3] == "HOME":
					for i in range(int((random.randint(minTimeHome,maxTimeHome) * 3600)/pointsPerSecond)): #3600 is a aribitrary number that allows scaling.
						random_angle = random.uniform(0.0, math.pi*2)
						random_number = random.gauss(0,1)
						hypothenuse = random_number * gpsNoise/1000
						delta_X = (math.cos(random_angle)) * hypothenuse
						delta_Y = (math.sin(random_angle)) * hypothenuse
						new_X = old_X + delta_X
						new_Y = old_Y + delta_Y
						new_point = arcpy.Point(new_X,new_Y)
						Distance = math.sqrt(math.pow(delta_X, 2) + math.pow(delta_Y, 2))
						
						xy.append((self.Internal_Clock(count), arcpy.Point(new_X, new_Y)))
						count = count + self.Manage_Time(pointsPerSecond)
					chosenTransport = modeOfTransport[random.randint(0,2)]
				elif row[3] == "WORK":
					for i in range(int((random.randint(minTimeWork,maxTimeWork) * 3600)/pointsPerSecond)):#3600 is a aribitrary number that allows scaling.
						random_angle = random.uniform(0.0, math.pi*2)
						random_number = random.gauss(0,1)
						hypothenuse = random_number * gpsNoise/1000
						delta_X = (math.cos(random_angle)) * hypothenuse
						delta_Y = (math.sin(random_angle)) * hypothenuse
						new_X = old_X + delta_X
						new_Y = old_Y + delta_Y
						new_point = arcpy.Point(new_X,new_Y)
						Distance = math.sqrt(math.pow(delta_X, 2) + math.pow(delta_Y, 2))
						
						xy.append((self.Internal_Clock(count), arcpy.Point(new_X, new_Y)))
						count = count + self.Manage_Time(pointsPerSecond)
					chosenTransport = modeOfTransport[random.randint(0,2)]
					

				elif row[3] == "ACTIVITYLOCATION":
					for i in range(int((random.randint(minTime,maxTime) * 3600)/pointsPerSecond)):
						random_angle = random.uniform(0.0, math.pi*2)
						random_number = random.gauss(0,1)
						hypothenuse = random_number * gpsNoise/1000
						delta_X = (math.cos(random_angle)) * hypothenuse
						delta_Y = (math.sin(random_angle)) * hypothenuse
						new_X = old_X + delta_X
						new_Y = old_Y + delta_Y
						new_point = arcpy.Point(new_X,new_Y)
						Distance = math.sqrt(math.pow(delta_X, 2) + math.pow(delta_Y, 2))
						
						xy.append((self.Internal_Clock(count), arcpy.Point(new_X, new_Y)))
						count = count + self.Manage_Time(pointsPerSecond)
					chosenTransport = modeOfTransport[random.randint(0,2)]
					
	
				else: 
					iteration = 1
					if pointsPerSecond < 60:
						iteration = 60 - pointsPerSecond
					else:
						iteration = 4 - pointsPerSecond // 60
					for i in range(int(iteration * (11 - chosenTransport))):#Scalls to amount of points and based on speed of transport
						points = self.Point_Scrambler(old_X,old_Y,0.5/1000)
						xy.append((self.Internal_Clock(count), arcpy.Point(points[0], points[1])))
						#10 makes average car speed around 50 clicks
						#15.5 km/h is for bike == 3 adjust the 10 below to make changes to timing
						count = count + (self.Manage_Time(pointsPerSecond) / chosenTransport)

				

		WorkSpace = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb"
		NewPointDataset = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\SyntheticGPSTrajectoryResult" + str(self.Internal_Count)

		if arcpy.Exists(NewPointDataset):
			arcpy.Delete_management(NewPointDataset)
			arcpy.CreateFeatureclass_management(WorkSpace, 'SyntheticGPSTrajectoryResult' + str(self.Internal_Count), 'POINT')
			self.Internal_Count += 1
		else:
			arcpy.CreateFeatureclass_management(WorkSpace, 'SyntheticGPSTrajectoryResult' + str(self.Internal_Count), 'POINT')
			self.Internal_Count += 1


		arcpy.AddField_management(NewPointDataset, "UTC_DATE", "TEXT")

		cursor = arcpy.da.InsertCursor(NewPointDataset,
		['UTC_DATE', 'SHAPE@XY'])

		# Insert new rows that include the county name and a x,y coordinate
		#  pair that represents the county center
		for row in xy:
			cursor.insertRow(row)

		# Delete cursor object
		del cursor
		arcpy.Delete_management(s)
		


if __name__ == '__main__':
    # Global Environment settings
	with arcpy.EnvManager(scratchWorkspace=r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb", workspace=r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb"):

		for i in range(datasetAmount):
			runner = SyntheticGPSTrajectory(i)
			runner.Generate_Route()
