
import arcpy
import random
import math
import datetime 

spatial_ref = int(arcpy.GetParameter(0)) #Grabs number of wanted activity locations.
yourOwnTemplate = arcpy.GetParameter(1) #Grabs time spent at locations.
homeTime = arcpy.GetParameter(2)
gpsNoise = arcpy.GetParameter(3)
minTime = arcpy.GetParameter(4)
maxTime = arcpy.GetParameter(5)
homePoint = ''
randomHouse = random.randrange(100)
def fcs_in_workspace():  

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














def Find_Point():
	HomesLoc = r"C:\SyntheticGPSTrajectory\WorkSpace\WherePeopleLive.shp"
	Homes = r'C:\SyntheticGPSTrajectory\WorkSpace\Homes.shp'
	if arcpy.Exists(Homes):
		arcpy.Delete_management(Homes)
		arcpy.FeatureToPoint_management(HomesLoc, Homes,"CENTROID")

	else:
		arcpy.FeatureToPoint_management(HomesLoc, Homes,"CENTROID")

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

	arcpy.AddField_management(NewPointDataset, "NAME", "TEXT")
	arcpy.AddField_management(NewPointDataset, "NEAR_DIST", "LONG")
	cursor = arcpy.da.InsertCursor(NewPointDataset, ["NAME","NEAR_DIST","SHAPE@XY"])
	xy = homePoint

	cursor.insertRow(xy)

	# Delete cursor object
	del cursor
def Work_Plus_Activities():
	NewPointDataset = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\buffeting"
	RandDest = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\howFarFromHome"
	Homes = r"C:\SyntheticGPSTrajectory\WorkSpace\Homes.shp"
	homePoly = 's'
	WorkSpace = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb"
	arcpy.Buffer_analysis(Homes, RandDest, "3000 Meters")
	fields = ['SHAPE@']
	count = 0
	with arcpy.da.UpdateCursor(RandDest, fields) as cursor:
	# Update the field used in Buffer so the distance is based on road 
	# type. Road type is either 1, 2, 3, or 4. Distance is in meters. 
	
	
		for row in cursor:
			count += 1
			if randomHouse == count:
				homePoly = row 

	arcpy.CreateFeatureclass_management(WorkSpace, 'buffeting', 'POLYGON')
	cursor = arcpy.da.InsertCursor(NewPointDataset,("SHAPE@"))
	cursor.insertRow(homePoly)

	# Delete cursor object
	del cursor



def Network_Analysis():
	# To allow overwriting outputs change overwriteOutput option to True.
	arcpy.env.overwriteOutput = False

	# Check out any necessary licenses.
	arcpy.CheckOutExtension("Network")
	arcpy.CheckOutExtension("GeoStats")
	Network_Data_Source = r"C:\SyntheticGPSTrajectory\WorkSpace\roadnetwork\toronto_network_ND.nd"
	RandDest = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\RandomDestination"
	Route = arcpy.na.MakeRouteAnalysisLayer(network_data_source=Network_Data_Source, layer_name="RouteSKIA")
	torontoOutline =  r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\buffeting"
	workspaceForPoints = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb"
	# Process: Add Locations (Add Locations) 
	arcpy.CreateRandomPoints_management(workspaceForPoints,"RandomDestination",torontoOutline, "",5,"", "POINT")
	# Process: Solve (Solve) 
	final = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\finalDestinations"

	habitatareas = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\habitatareas"
	RandomPointsPlusHome = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\RandomPointsPlusHome"
	arcpy.Merge_management([habitatareas, RandDest], 
                       RandomPointsPlusHome)
	Updated_Input_Network_Analysis_Layer = arcpy.AddLocations_na(in_network_analysis_layer=Route, sub_layer="Stops", in_table=RandomPointsPlusHome, field_mappings="Name Name #", search_tolerance="5000 Meters", sort_field="", search_criteria=[], match_type="MATCH_TO_CLOSEST", append="APPEND", snap_to_position_along_network="NO_SNAP", snap_offset="5 Meters", exclude_restricted_elements="EXCLUDE", search_query=[])[0]

	Network_Analyst_Layer, Solve_Succeeded = arcpy.Solve_na(in_network_analysis_layer=Updated_Input_Network_Analysis_Layer, ignore_invalids="SKIP", terminate_on_solve_error="TERMINATE", simplification_tolerance="", overrides="")
	

	"""
	REMEMBER TO DELETE THE OLD GDB FILES FROM THE RANDOME DATASET IT MAKES
	"""


def Generate_Route():

	

	
	Find_Point()
	
	Work_Plus_Activities()
	Network_Analysis()
	findr = fcs_in_workspace()
	PAL = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\PointAlongLine"
	arcpy.GeneratePointsAlongLines_management(findr[1], PAL, 'DISTANCE', Distance='210 meters')
	arcpy.Near_analysis(PAL, findr[2])
	NewPointDataset = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\habitatareas"
	RandomPointsPlusHome = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\RandomPointsPlusHome"
	RandDest = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\RandomDestination"


	Depth_Traversal(spatial_ref,findr)

	arcpy.Delete_management(RandomPointsPlusHome)
	arcpy.Delete_management(RandDest)
	arcpy.Delete_management(findr[0])
	#arcpy.Delete_management(PAL)
	arcpy.Delete_management(NewPointDataset)
	
	"""
	REMEMBER TO DELETE THE OLD GDB FILES FROM THE RANDOME DATASET IT MAKES
	"""
def Point_Scrambler(x,y,noise):
	random_angle = random.uniform(0.0, math.pi*2)
	random_number = random.gauss(0,1)
	hypothenuse = random_number * (noise)
	delta_X = (math.cos(random_angle)) * hypothenuse
	delta_Y = (math.sin(random_angle)) * hypothenuse
	new_X = x + delta_X
	new_Y = y + delta_Y
	return [new_X,new_Y]

def Internal_Clock(count):
	x = count 
	day = 1
	if x > 1439:
		x = count - 1439
		day = 2
	hours = x // 60  # Truncating integer division
	minutes = x % 60  # Modulo removes the upper digits

	time = datetime.datetime(2009, 10, day,hours,minutes,0)
	return str(time)

def Depth_Traversal(x,findr):
	s = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\PointAlongLine"

	xy = []
	fields = ['NEAR_DIST','OBJECTID']
	lowestValue = 10
	lowestValueID = [10]

	# Create update cursor for feature class 
	with arcpy.da.UpdateCursor(s, fields) as cursor:
	# Update the field used in Buffer so the distance is based on road 
	# type. Road type is either 1, 2, 3, or 4. Distance is in meters. 
		for row in cursor:

			# Update the BUFFER_DISTANCE field to be 100 times the 
			# ROAD_TYPE field.
			if float(row[0]) < lowestValue:
				if len(lowestValueID) < x:
					lowestValueID.append(row[1])
					lowestValue = row[0]
				else:
					lowestValueID.pop(0)
					lowestValueID.append(row[1])
					lowestValue = row[0]
	del cursor, row
	count = 0
	arcpy.AddField_management(s, "UTC_DATE", "TEXT")
	fields = ['SHAPE@XY','OBJECTID','UTC_DATE']
	with arcpy.da.UpdateCursor(s, fields) as cursor:
	# Update the field used in Buffer so the distance is based on road 
	# type. Road type is either 1, 2, 3, or 4. Distance is in meters. 
		modeOfTransport = ['car','bike','walk']
		chosenTransport = 'car'
		for row in cursor:
			old_X = float(row[0][0])
			old_Y = float(row[0][1])
			if count == 0:
				for i in range(homeTime * 43):
					random_angle = random.uniform(0.0, math.pi*2)
					random_number = random.gauss(0,1)
					hypothenuse = random_number * gpsNoise/1000
					delta_X = (math.cos(random_angle)) * hypothenuse
					delta_Y = (math.sin(random_angle)) * hypothenuse
					new_X = old_X + delta_X
					new_Y = old_Y + delta_Y
					new_point = arcpy.Point(new_X,new_Y)
					Distance = math.sqrt(math.pow(delta_X, 2) + math.pow(delta_Y, 2))
					
					xy.append((Internal_Clock(count), arcpy.Point(new_X, new_Y)))
					count = count + 1
				chosenTransport = modeOfTransport[random.randint(0,2)]
				
			if row[1] in lowestValueID:
				for i in range(random.randint(minTime,maxTime)):
					random_angle = random.uniform(0.0, math.pi*2)
					random_number = random.gauss(0,1)
					hypothenuse = random_number * gpsNoise/1000
					delta_X = (math.cos(random_angle)) * hypothenuse
					delta_Y = (math.sin(random_angle)) * hypothenuse
					new_X = old_X + delta_X
					new_Y = old_Y + delta_Y
					new_point = arcpy.Point(new_X,new_Y)
					Distance = math.sqrt(math.pow(delta_X, 2) + math.pow(delta_Y, 2))
					
					xy.append((Internal_Clock(count), arcpy.Point(new_X, new_Y)))
					count = count + 1
				chosenTransport = modeOfTransport[random.randint(0,2)]
			else: 
				if chosenTransport == 'car':
					points = Point_Scrambler(old_X,old_Y,0.5/1000)
					xy.append((Internal_Clock(count), arcpy.Point(points[0], points[1])))
					count = count + 1

				if chosenTransport == 'bike':
					points = Point_Scrambler(old_X,old_Y,1/1000)
					xy.append((Internal_Clock(count), arcpy.Point(points[0], points[1])))
					count = count + 1
					points = Point_Scrambler(old_X,old_Y,1.6/1000)
					xy.append((Internal_Clock(count), arcpy.Point(points[0], points[1])))
					count = count + 1
				

				if chosenTransport == 'walk':
					points = Point_Scrambler(old_X,old_Y,1.6/1000)
					xy.append((Internal_Clock(count), arcpy.Point(points[0], points[1])))
					count = count + 1
					points = Point_Scrambler(old_X,old_Y,1.6/1000)
					xy.append((Internal_Clock(count), arcpy.Point(points[0], points[1])))
					count = count + 1
					points = Point_Scrambler(old_X,old_Y,1.6/1000)
					xy.append((Internal_Clock(count), arcpy.Point(points[0], points[1])))
					count = count + 1
			

	WorkSpace = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb"
	NewPointDataset = r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb\habitatareas2"

	if arcpy.Exists(NewPointDataset):
		arcpy.Delete_management(NewPointDataset)
		arcpy.CreateFeatureclass_management(WorkSpace, 'habitatareas2', 'POINT')
	else:
		arcpy.CreateFeatureclass_management(WorkSpace, 'habitatareas2', 'POINT')

	arcpy.AddField_management(NewPointDataset, "UTC_DATE", "TEXT")

	cursor = arcpy.da.InsertCursor(NewPointDataset,
	['UTC_DATE', 'SHAPE@XY'])

	# Insert new rows that include the county name and a x,y coordinate
	#  pair that represents the county center
	for row in xy:
		cursor.insertRow(row)

	# Delete cursor object
	del cursor




if __name__ == '__main__':
    # Global Environment settings
    with arcpy.EnvManager(scratchWorkspace=r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb", workspace=r"C:\SyntheticGPSTrajectory\SyntheticGPSTrajectory.gdb"):
        Generate_Route()
