from bs4 import BeautifulSoup
from requests import get
from re import sub
from json import loads,dump
from re import findall,sub
from unicodecsv import QUOTE_ALL,DictWriter
totalJobs = []

def getPage(url):
    """
    Method to handle page request
    """
    headers = {
                    'Connection': 'keep-alive',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept': '*/*',
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'
    }
    response = get(url,verify=False,headers=headers)
    pageStatus = response.status_code
    while pageStatus!=200:
        print "Retrying page ",url
        response = get(url,verify=False,headers=headers)
        pageStatus = response.status_code
    cleaned_html = sub('\s\s+','',response.content.replace("<!--","").replace("-->",""))
    return cleaned_html


def getjobs(companyName,location):
    """
    Need to get locationId for respective location to get the job list
    """
    url = 'https://www.linkedin.com/ta/geo?query='+location.replace(' ','%20')+'&orig=jserp'
    html = getPage(url)
    jsonData = loads(html)
    try:
        locationId = jsonData['resultList'][0]['id']
        url = 'https://www.linkedin.com/jobs/searchRefresh?keywords='+companyName.replace(" ","%20")+'&refreshType=fullpage&locationId='+locationId+'&trk=jobs_jserp_search_button_execute&searchOrigin=JSERP'
        html= getPage(url)
        jsonData = loads(html)
        for job in jsonData['decoratedJobPostingsModule']['elements']:
            html = getPage(job['viewJobCanonicalUrl'])
            soup = BeautifulSoup(html)
            element = soup.find('code',attrs={'id':'decoratedJobPostingModule'})
            jsonData = loads(element.string)
            if jsonData:
                postedTime = jsonData['decoratedJobPosting']['formattedPostedDaysAgo']
                jobDescription = jsonData['decoratedJobPosting']['jobPosting']['description']['rawText']
                jobFunctions = jsonData['decoratedJobPosting']['formattedJobFunctions']
                jobFunctions = ",".join(jobFunctions) if jobFunctions else None
                employmentType = jsonData['decoratedJobPosting']['formattedEmploymentStatus']
                experience = jsonData['decoratedJobPosting']['formattedExperience']
                location = jsonData['decoratedJobPosting']['formattedLocation']
                jobTitle = jsonData['decoratedJobPosting']['jobPosting']['title']
                companyName = jsonData['decoratedJobPosting']['jobPosting']['companyName']
                industries = jsonData['decoratedJobPosting']['formattedIndustries']
                industries = ",".join(industries) if industries else None
                element = soup.find('code',attrs={'id':'topCardV2Module'})
                jsonData = loads(element.string)
                totalViews = jsonData['viewCount']
                item = {
                            "postedTime":postedTime,
                            "jobDescription":jobDescription,
                            "jobFunctions":jobFunctions,
                            "employmentType":employmentType,
                            "experience":experience,
                            "location":location,
                            "jobTitle":jobTitle,
                            "companyName":companyName,
                            "industries":industries,
                            "totalViews":totalViews,
                            "url":url
                }
                totalJobs.append(item)
    except:
        pass


if __name__ == '__main__':
    """ Provide the location and companyName """
    location = "New York"
    companyName = "Airbnb"
    getjobs(companyName,location)
    print "Total jobs got ",len(totalJobs)
    file = open('finalData.csv','wb')
    fields = [
                'jobTitle','companyName','location','postedTime','totalViews',
                'jobDescription','industries','employmentType','experience','employmentType',
                'jobFunctions','url'
    ]
    csvfile = DictWriter(file,fieldnames=fields,quoting=QUOTE_ALL,encoding="utf-8")
    csvfile.writeheader()
    for i in totalJobs:
        csvfile.writerow(i)
    file.close()
