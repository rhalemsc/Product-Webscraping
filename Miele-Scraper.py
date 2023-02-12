from bs4 import BeautifulSoup
import datetime
from datetime import date
import time
from selenium import webdriver
import mysql.connector
import requests
import re

#Establish connection to database and query to get a list of items
mydb = mysql.connector.connect(
  host="123.123.12.1",
  user="1234",
  password="1234",
  database="1234"
)

model_query=[]
mycursor = mydb.cursor()
mycursor.execute("SELECT opt.osku, opt.osku2 "\
                 "FROM hpl_option AS opt INNER JOIN asdf AS p "\
                 "ON opt.pid=p.pid INNER JOIN asdf AS br "\
                 "ON p.bid=br.id LEFT OUTER JOIN tbl_scraped_data AS sd "\
                 "ON opt.osku=sd.osku "\
                 "WHERE br.bname='Miele' AND opt.optid IN ('1','2', '3', '4') AND sd.data_xml IS NULL AND opt.opactive<>'Discontinued' "\
                 "AND opt.osku2 IS NOT NULL AND opt.osku2 NOT LIKE '%USA%' AND opt.osku2<>''")

model_query = mycursor.fetchall()
model_list = [item for item in model_query]

#Set bid here for this particular brand
bid=33

#Main loop to go through items list
for osku in model_list:
    URL='https://www.mieleusa.com/e/w-'+osku[1]+'-p'
    print('Working On', osku[0], URL, sep='\t')

    time.sleep(5)
    driverPath='C:\\Users\\rh\\PyCharmProjects\\Utilities\\chromedriver.exe'
    driver = webdriver.Chrome(driverPath)
    driver.get(URL)
    html=driver.page_source
    driver.close()

    #Insert source from chrome driver as a BS object, format as HTML
    bsObj = BeautifulSoup(html, "html.parser")

    header=str(bsObj.find('h1', class_='hdl hdl--display hdl--inverted'))

    try:
        if 'Sorry' in header:
            print('updated as missing')
            insert_missing_sql =    'INSERT INTO '\
	                                    'tbl_scraped_data (osku, data_source_bid, date_updated, date_first_checked) '\
                                    'VALUES(%s, %s, %s, %s) '\
                                    'ON DUPLICATE KEY UPDATE '\
                                        "osku='" + str(osku[0])+"', "\
                                        'data_source_bid='+ str(bid) +', '\
                                        "date_updated ='" + str(date.today()) +"'"
            missing_sql_val = (osku[0], bid, str(date.today()), str(date.today()))
            mycursor.execute(insert_missing_sql, missing_sql_val)
            mydb.commit()
    except:
        pass

    try:
        if 'Sorry' in header:
            continue
    except:
        pass

    #Arrays
    spec_names_list=[]
    spec_values_list=[]
    doc_names_list=[]
    doc_source_list=[]
    images_source_list=[]
    features_titles_list=[]
    features_descriptions_list=[]
    features_images_list=[]

    #Other
    category_name=''
    product_xml='<item>'
    specifications_xml='<specifications>'
    documents_xml='<documents>'
    images_xml='<images>'
    features_xml='<features>'

    #Product Name
    product_name=''

    #Internet ID
    internet_id=bsObj.find('h1', {'itemprop':'name'}).get_text()

    #Category
    navs = []
    navs = bsObj.findAll('li', class_='nav-breadcrumb__item')
    navs_len = len(navs) - 2
    category_name=navs[navs_len].get_text()

    #Images
    images=[]
    for image in bsObj.find('div', class_='carousel carousel--buttons-on-hover carousel--initialized').findAll('span', class_='thumbnail-fixer'):
        images_source_list.append(image.find_next('img').get('src')\
                                  .replace('d=100', 'd=1000')\
                                  .replace('&impolicy=boxed', '')
                                  )

    # Features
    try:
        for feature in bsObj.findAll('div', class_='tsr-text tsr-text--in-grid tsr-text--in-grid--col-4 toggle'):
            # Feature Images
            features_images_list.append(str(feature.find_next('a')) \
                                        .replace('<a class="tsr-text__visual" href="#" style="background-image: url(','') \
                                        .replace(')" tabindex="-1"><span class="tsr-label tsr-label--left tsr-label--red cpy--body-small cpy--inverted">Exclusive to Miele</span></a>','') \
                                        .replace(')" tabindex="-1"></a>', '') \
                                        .replace(')" tabindex="0"><span class="tsr-label tsr-label--left tsr-label--red cpy--body-small cpy--inverted">Exclusive to Miele</span></a>','') \
                                        .replace('"><span class="tsr-label tsr-label--left tsr-label--red cpy--body-small cpy--inverted">Exclusive to Miele</span></a>','') \
                                        .replace(')"></a>', '') \
                                        .replace(')', '')
                                        )
            # Feature Titles
            feature_title = feature.find_next('p',class_='cpy cpy--body-small cpy--primary cpy--bold mb-3x').get_text().replace('&', 'and')
            feature_title = re.sub(r'\[(.)\]', '', feature_title)
            feature_title = re.sub(r'\[(..)\]', '', feature_title)
            features_titles_list.append(feature_title)
            # Description
            feature_description = feature.find_next('div',class_='tsr-text__description cpy cpy--body cpy--primary mb-3x').get_text().replace('&', 'and')
            feature_description = re.sub(r'\[(.)\]', '', feature_description)
            feature_description = re.sub(r'\[(..)\]', '', feature_description)
            features_descriptions_list.append(feature_description)
    except:
        features_titles_list.append('')
        features_descriptions_list.append('')
        features_images_list.appened('')

    #Specifications
    try:
        for spec in bsObj.find('section', {'id': 'section03'}).findAll('tr'):
            spec_names_list.append(spec.find_next('td').get_text()[:50].replace('&', 'and'))
            spec_value = spec.find_next('td').find_next('td').get_text() \
                .replace('•', 'Yes') \
                .replace('-', 'No') \
                .replace('&', 'and')
            spec_value = re.sub(r'\((...)\)', '', spec_value)
            spec_value = re.sub(r'\((.)\)', '', spec_value)
            spec_value = re.sub(r'\((..)\)', '', spec_value)
            spec_value = re.sub(r'\((....)\)', '', spec_value)
            spec_values_list.append(spec_value)
    except:
        spec_names_list.append('')
        spec_values_list.append('')


    #Documents
    #User manual
    try:
        for doc in bsObj.findAll('div', class_='download-item bg-color-white'):
            doc_names_list.append(doc.find_next('div', class_='download-item__title').find_next('div').get_text())
            doc_source_list.append(doc.find_next('div', class_='download-item__icon').find_next('a').get('onclick') \
                                   .replace("window.open('", ""). \
                                   replace("'); return false;", "")
                                   )
    except:
        doc_names_list.append('')
        doc_source_list.append('')

    i=0
    for name in spec_names_list:
       specifications_xml=specifications_xml+ '\n<specification>' +'\n\t<specification_name>'+spec_names_list[i]+'</specification_name>\n'+\
                          '\t<specification_value>'+ spec_values_list[i]+'</specification_value>\n</specification>'
       i=i+1
    specifications_xml=specifications_xml+'\n</specifications>'

    i=0
    for document in doc_names_list:
       documents_xml=documents_xml+ '\n<document>\n'+ '\t<document_name>'+ doc_names_list[i]+ '</document_name>'+\
                     '\n\t<document_source><![CDATA['+ doc_source_list[i]+']]></document_source>\n</document>'
       i=i+1
    documents_xml=documents_xml+'\n</documents>\n'

    i=0
    for image in images_source_list:
        images_xml=images_xml+'\n\t<image>'+image+'</image>'
        i=i+1
    images_xml=images_xml+'\n</images>'

    i=0
    for features in features_titles_list:
        features_xml=features_xml + '\n<feature>\n\t<feature_title>'+ features_titles_list[i]+'</feature_title>\n\t<feature_description>' + features_descriptions_list[i] +\
                        '</feature_description>\n\t<feature_image>' + features_images_list[i] +'</feature_image>\n</feature>'
        i=i+1
    features_xml=features_xml+'\n </features>' \
                              ''
    #Create XML
    product_xml=product_xml + '\n' +\
                '<osku>'+osku[0]+'</osku>\n'+\
                '<manuf_url>'+URL+'</manuf_url>\n'+\
                '<manuf_id>'+internet_id+'</manuf_id>\n'+\
                '<category_path>'+category_name+'</category_path>\n'+\
                '<product_name>'+product_name+'</product_name>\n'+\
                images_xml+ '\n' +\
                specifications_xml +'\n'+\
                documents_xml  + '\n'+\
                features_xml +\
                '</item>'

    insert_sql='INSERT INTO tbl_scraped_data (osku, data_source_bid, data_xml, date_updated, date_first_checked, num_specs, num_images, num_features, num_documents) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
    sql_val=(osku[0], bid, product_xml, str(date.today()), str(date.today()), len(spec_names_list), len(images_source_list), len(features_titles_list), len(doc_names_list))
    mycursor.execute(insert_sql, sql_val)
    mydb.commit()
