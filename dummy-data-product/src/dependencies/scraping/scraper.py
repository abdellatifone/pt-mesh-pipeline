import requests
from bs4 import BeautifulSoup
import csv
from itertools import zip_longest
import boto3
from botocore.exceptions import NoCredentialsError


def construct_csv_file(local_file, file_list):
	exported = zip_longest(*file_list)
	with open(f"{local_file}","w") as myfile:
		wr = csv.writer(myfile)
		wr.writerow(["regions_name", "sectors_name", "projects_title","links","taxonomies_term","authors_name","times_information","imgs_information"])
		wr.writerows(exported)


def upload_to_aws(local_file, bucket, s3_file, ACCESS_KEY , SECRET_KEY):
	s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
	try:
		s3.upload_file(local_file, bucket, s3_file)
		print("Upload Successful")
		return True
	except FileNotFoundError:
		print("The file was not found")
		return False
	except NoCredentialsError:
		print("Credentials not available")
	return False


def extract_toggles_values(target_website, extr_a, extr_b):
	elts_list = []	
	resulter = requests.get(f"{target_website}")
	src = resulter.content
	soup = BeautifulSoup(src, "lxml")
	
	scrapped_data  = soup.find_all("select",{"name":"{}".format(extr_a)})
	for tag in scrapped_data:
		tdTags = tag.find_all("option",{"class":"{}".format(extr_b)})
		for tag in tdTags:
			if tag['value'] is not None and tag['value'] not in '':
				elts_list.append(tag['value'])
	filtered_list = list(dict.fromkeys(elts_list))
	return filtered_list


def scrap_data(target_website):
	filtered_sector_list = extract_toggles_values(target_website, "_sft_sector[]", "sf-level-0")
	#Scrap Level 1 and Level 2 of data due to an issue of data representation in the scrapped website
	filtered_region_list = extract_toggles_values(target_website, "_sft_region[]", "sf-level-2") + extract_toggles_values(target_website, "_sft_region[]", "sf-level-1")

	filtered_region_list = ['burundi']

	for region_name in filtered_region_list:
		for sector_name in filtered_sector_list:
			index_page = 1
			print(index_page)
			while(True):
				page = f"{target_website}/?_sft_region={region_name}&_sft_sector={sector_name}&sf_paged={index_page}"
				print(page)
				result = requests.get(page)
				src = result.content
				soup = BeautifulSoup(src, "lxml")

				tester = soup.find_all("div", {"class":"cl-layout__no-results"})
				for x in range(len(tester)):
					if(tester[x].text is not None):
						print("not Data found in Area / Sector")
						break  
				project_title = soup.find_all("h3",{"class": "cl-element cl-element-title cl-element--instance-1179"})		
				author_name = soup.find_all("div",{"class":"cl-element-author__text"} )	
				taxonomy_term = soup.find_all("a",{"class":"cl-element-taxonomy__term"} )
				for i in range(len(project_title)):
					print(f"Region Name: {region_name} Sector name: {sector_name} Project title: {project_title[i].text} Author Name: {author_name[i].text}")
					regions_name.append(region_name)
					sectors_name.append(sector_name)
					projects_title.append(project_title[i].text)
					links.append(project_title[i].find("a").attrs['href'])
					taxonomies_term.append(taxonomy_term[i].text.strip())
					authors_name.append(author_name[i].text)	
								
				page_number = soup.find_all("a", {"class":"page-numbers"} )
				if  not page_number:
					break
				else:
					selector_iter = []
					for i in range(len(page_number)):
						selector_iter.append(page_number[i].text.replace(',', '') )
					cleaned_iter = [ x for x in selector_iter if x.isdigit() ]
					highest_iter = sorted(cleaned_iter,reverse=True)[0]
					if(index_page >= int(highest_iter) ):
                				break
					else:
						index_page+=1

	#get the links related to the images and times information			
	for link in links:
		resulter = requests.get(link)
		src = resulter.content
		soup = BeautifulSoup(src, "lxml")
		time_information = soup.find_all("time",{"class":"entry-date updated td-module-date"})
		img_information_scrap = soup.find('img', {"class": "entry-thumb td-modal-image"})
		img_information = ''
		if img_information_scrap is not None:
			img_information = img_information_scrap['src']
		for pos in range(len(time_information)):
			times_information.append(time_information[pos].text)
			imgs_information.append(img_information)
			print(f"{time_information[pos].text} {img_information}")


if __name__ == "__main__":

	#############The parameters ACCESS_KEY and SECRET_KEY should be declare and set##################

	BUCKET_NAME = "taiyo-timeseries-dev" 
	LOCAL_FILE = "/tmp/construction_review_base_data.csv"
	TARGET_FILE_NAME = "construction_review_base_data.csv"
	WEBSITE = "https://constructionreviewonline.com/construction-leads"

	projects_title = []
	authors_name = []
	taxonomies_term = []
	links = []
	regions_name = []	
	sectors_name = []
	times_information = []
	imgs_information = []

	scrap_data(WEBSITE)
	file_list = [regions_name, sectors_name, projects_title,links,taxonomies_term,authors_name,times_information,imgs_information]
	construct_csv_file(LOCAL_FILE, file_list)
	#upload_to_aws(LOCAL_FILE, BUCKET_NAME, TARGET_FILE_NAME, ACCESS_KEY, SECRET_KEY)
