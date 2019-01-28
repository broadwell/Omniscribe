### To be used on the stripped version of the csv file generated from zooniverse

import pandas as pd
import json

CSV_PATH = '/Users/silver/Desktop/buildUCLA/stripped-book-annotation-classification-classifications-11June2018.csv'

# ASSUMES FILES ARE .PNG FORMAT
META_DATA_PATH = '/Users/silver/Desktop/buildUCLA/phase2/annotations-computervision/books meta data.csv'

# WARNING CSV file is inconsistent with the key identifier for the key names. 'filename' 'manifest.csv' and 'uclaclark_QD25S87_0291.png' are keys to retrieve the file name
def extractROIs(csv_file_path):
	assert csv_file_path
	df = pd.read_csv(csv_file_path, usecols=['annotations', 'subject_data','subject_ids'])

	# need to add this bit to map file names to the randomized IDs
	df_meta = pd.read_csv(META_DATA_PATH, usecols=['ID','File Name'])
	name2id = dict()
	for index, row in df_meta.iterrows():
		name2id[row[1].replace(".png",".jpg")] = str(row[0]) + ".png"

	fileNames = []
	coordinates = []

	# gets all fileNames of images in rows that use 'filename' as the key
	for index, row in df.iterrows():

		s_id = str(row['subject_ids'])

		s_data = json.loads(row['subject_data'])

		try: # if this succeeds, then we can retrieve its annotations as well
			
			fn = s_data[s_id]['filename']

			# name2id to convert file name to our id naming convention
			fileNames.append(name2id[s_data[s_id]['filename']])
			
			tasks = json.loads(df.iloc[index]['annotations'])

			imageCoordinates = []

			for t in tasks:

				if t['task'] == 'T1':
					listOfCoordinates = t['value']

					for coord in listOfCoordinates:
						formattedCoord = coord['x'], coord['y'], coord['width'], coord['height']
						imageCoordinates.append(formattedCoord)

			coordinates.append(imageCoordinates)
		except:
			try: # if this succeeds, then we are getting all the clark images
			
				fn = s_data[s_id]['manifest.csv']

				fileNames.append(s_data[s_id]['manifest.csv'])
			
				tasks = json.loads(df.iloc[index]['annotations'])

				imageCoordinates = []

				for t in tasks:

					if t['task'] == 'T1':
						listOfCoordinates = t['value']

						for coord in listOfCoordinates:
							formattedCoord = coord['x'], coord['y'], coord['width'], coord['height']
							imageCoordinates.append(formattedCoord)

				coordinates.append(imageCoordinates)
			except:
				try: # if this succeeds, then we are getting all the remaining images
			
					fn = s_data[s_id]['uclaclark_QD25S87_0291.png']

					fileNames.append(s_data[s_id]['uclaclark_QD25S87_0291.png'])
			
					tasks = json.loads(df.iloc[index]['annotations'])

					imageCoordinates = []

					for t in tasks:

						if t['task'] == 'T1':
							listOfCoordinates = t['value']

							for coord in listOfCoordinates:
								formattedCoord = coord['x'], coord['y'], coord['width'], coord['height']
								imageCoordinates.append(formattedCoord)

					coordinates.append(imageCoordinates)
				except:
					pass	

	duplicatedRegionData = list(zip(fileNames,coordinates))

	d = dict()


	falsePositives = ['2032.png', '2269.png', '2512.png', '2565.png','2710.png','2736.png', 'uclaclark_AY751Z71673_0061.png','uclaclark_AY751Z71673_0119.png','uclaclark_AY751Z71673_0124.png']
	unannotated_count= 0
	region_count = 0
	for pair in duplicatedRegionData:

		# skin unannotated regions
		if pair[0] in falsePositives or not pair[1]:
			unannotated_count += 1
			continue

		if pair[0] in d:
			[d[pair[0]].append(r) for r in pair[1]]
		else:
			d[pair[0]] = pair[1]

	for rl in d.values():
		for r in rl:
			region_count += 1 


	print('There are {} unannotated images'.format(unannotated_count))
	print('There are {} regions of interest'.format(region_count))

	#print('This is the length of d: {}'.format(len(d)))

	# unit tests 
	#print('Here are the regions for image "779.png": {}'.format(d['779.png']))
	#print('Here are the regions for image "uclaclark_AY751Z71673_0065": {}'.format(d['uclaclark_AY751Z71673_0065.png']))

	return d

def convertToMaskRCNN(regionImageData: dict):
	
	# the actual JSON
	regionDataFormatted = dict()

	for img,regions in regionImageData.items():

		regionDataFormatted[img] = dict()

		regionValue = dict() #the region is itself a dictionary
		for i in range(len(regions)):

			someD = dict()

			someD["shape_attributes"] = {"name" : "polygon", "all_points_x": [regions[i][0],regions[i][0] + regions[i][2]], "all_points_y": [regions[i][1],regions[i][1] + regions[i][3]]}

			regionValue[str(i)] = dict()
			regionValue[str(i)] = someD

		regionDataFormatted[img]["filename"] = img
		regionDataFormatted[img]["regions"] = regionValue

	return regionDataFormatted


regionData = extractROIs(CSV_PATH)

for img in sorted(regionData.keys()):
	print(img)
regionDataFormatted = convertToMaskRCNN(regionData)

print(regionDataFormatted['uclaclark_AY751Z71673_0135.png'])

print('There are {} elements in our zooniverse list'.format(sum(1 for _ in regionData)))