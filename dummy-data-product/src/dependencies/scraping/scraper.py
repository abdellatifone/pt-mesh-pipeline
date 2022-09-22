import requests
from bs4 import BeautifulSoup
from utils import *


region_list_1 = []
region_list_2 = []
sector_list = []
projects_title = []
authors_name = []
taxonomies_term = []
links = []
regions_name = []
sectors_name = []
times_information = []
imgs_information = []




def scrap_data(target_website):
	
	resulter = requests.get(f"{target_website}")#"https://constructionreviewonline.com/construction-leads")
	src = resulter.content
	soup = BeautifulSoup(src, "lxml")
	
	scrapped_sector  = soup.find_all("select",{"name":"_sft_sector[]"})
	for tag in scrapped_sector:
		tdTags = tag.find_all("option",{"class":"sf-level-0"})
		for tag in tdTags:
			if tag['value'] is not None and tag['value'] not in '':
				print(tag['value'])
				sector_list.append(tag['value'])
	filtered_sector_list = list(dict.fromkeys(sector_list))


	scrapped_region_level2  = soup.find_all("select",{"name":"_sft_region[]"})
	for tag in scrapped_region_level2:
		tdTags = tag.find_all("option",{"class":"sf-level-2"})
		for tag in tdTags:
			if tag['value'] is not None and tag['value'] not in '':
				region_list_2.append(tag['value'])

	#Scrap Level 1 of data due to an issue of data representation in the scrapped website
	scrapped_region_level1 = soup.find_all("select",{"name":"_sft_region[]"})
	for tag in scrapped_region_level1:
		dTags = tag.find_all("option",{"class":"sf-level-1"})
		for tag in dTags:
			if tag['value'] is not None and tag['value'] not in '':
				region_list_1.append(tag['value'])

	filtered_region_list = list(dict.fromkeys(region_list_1 + region_list_2))

	for x in filtered_sector_list:
		print(x)

	#filtered_region_list = ['burundi']

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
				
	for link in links:
		resulter = requests.get(link)
		src = resulter.content
		soup = BeautifulSoup(src, "lxml")
		time_information = soup.find_all("time",{"class":"entry-date updated td-module-date"})
		img_information_scrap = soup.find('img', {"class": "entry-thumb td-modal-image"})
		img_information = ''
		if img_information_scrap is not None:
			img_information = img_information_scrap['src']
		for x in range(len(time_information)):
			times_information.append(time_information[x].text)
			imgs_information.append(img_information)
			print(f"{time_information[x].text} {img_information}")


if __name__ == "__main__":

	ACCESS_KEY = 'AKIA6B2OC2F2BZKJYOOQ'
	SECRET_KEY = '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'
	BUCKET_NAME = "taiyo-timeseries-dev" 
	LOCAL_FILE = "/tmp/construction_review_scrapped_data.csv"
	TARGET_FILE_NAME = "construction_review_scrapped_data.csv"
	WEBSITE = "https://constructionreviewonline.com/construction-leads"

	scrap_data(WEBSITE)
	file_list = [regions_name, sectors_name, projects_title,links,taxonomies_term,authors_name,times_information,imgs_information]
	construct_csv_file(LOCAL_FILE, file_list)
	uploaded = upload_to_aws(LOCAL_FILE, BUCKET_NAME, TARGET_FILE_NAME, ACCESS_KEY, SECRET_KEY)
