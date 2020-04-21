from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains your API key
import time
import sqlite3
import re

api_key = secrets.FLICKER_API_KEY
api_secret = secrets.FLICKER_API_SECRET

BASE_URL = 'https://www.flickr.com/services/rest/?'
CACHE_FILE_NAME = 'cache.json'
CACHE_DICT = {}
LENS_URL = 'https://www.lens-db.com/lens-lineup/'

headers = {
    'User-Agent': 'UMSI 507 Course Project - Python Scraping',
    'From': 'cescud@umich.edu',
    'Course-Info': 'https://si.umich.edu/programs/courses/507'
}

def load_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache


def save_cache(cache):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    cache_file = open(CACHE_FILE_NAME, 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()

def make_url_request_using_cache(url, cache):

    '''Searches Cache keys first and if the unique url key 
    is not found, makes request via url
    
    Parameters
    ----------
    url: string
        The URL for the API endpoint
    
    cache: dict
        cache to search for
    
    Returns
    -------
    dict
        the data returned from making the request in the form of 
        a dictionary
    '''

    if (url in cache.keys()): # the url is our unique key
        print("Using cache")
        return cache[url]

    else:
        print("Fetching")
        time.sleep(1)
        response = requests.get(url, headers=headers)
        cache[url] = response.text
        save_cache(cache)
        return cache[url]

def make_api_request_using_cache(url, params, cache):
    '''Searches Cache keys first and if the unique url key 
    is not found, makes request via web API
    
    Parameters
    ----------
    url: string
        The URL for the API endpoint
    params: dictionary
        A dictionary of param:value pairs

    cache: dict
        cache to search for
    
    Returns
    -------
    dict
        the data returned from making the request in the form of 
        a dictionary
    '''
    if (f"{url}{params}" in cache.keys()): # the url is our unique key
        print("Using cache")
        return cache[f"{url}{params}"]

    else:
        print("Fetching")
        time.sleep(1)
        response = requests.get(url, params=params)
        cache[f"{url}{params}"] = response.json()
        save_cache(cache)
        return cache[f"{url}{params}"]

def get_photos_from_keyword(keyword):
    
    CACHE_DICT = load_cache()
    params = {"method" : "flickr.photos.search", "api_key" : api_key, 'per_page' : '30', 'format' : 'json',
                "tags" : keyword, 'nojsoncallback' : '1'}
    
    photos = make_api_request_using_cache(BASE_URL, params, CACHE_DICT)
    photos = photos['photos']['photo']

    return photos

def extract_photo_id(photo):
    
    # photo_id = []

    # for photo in photos:
    #     photo_id.append(photo['id'])

    return photo['id']



def get_exif_from_photos(photos):
    CACHE_DICT = load_cache()

    exif_list = []

    for item in photos:
        picture_id = extract_photo_id(item)
        params = {"method" : "flickr.photos.getExif", "api_key" : api_key, 'photo_id' : f"{picture_id}",
                'format': 'json', 'nojsoncallback' : '1'}
        exif_data = make_api_request_using_cache(BASE_URL, params, CACHE_DICT)
        exif_list.append(exif_data)
    
    return exif_list


def get_focal_length_from_exifs(exifs):
    focal_length_list = []
    for d in exifs:
        if 'photo' in d.keys():
            if 'exif' in d['photo']:
                for dic in d['photo']['exif']:
                    for key, value in dic.items():
                        if value == 'FocalLengthIn35mmFormat':
                            focal_length_list.append(dic['raw']['_content'])

    return focal_length_list

def get_camera_make_from_exifs(exifs):
    camera_make_list = []
    for d in exifs:
        if 'photo' in d.keys():
            if 'exif' in d['photo']:
                for dic in d['photo']['exif']:
                    for key, value in dic.items():
                        if value == 'Make':
                            camera_make_list.append(dic['raw']['_content'])
    return camera_make_list

def get_model_from_exifs(exifs):
    model_list = []
    for d in exifs:
        if 'photo' in d.keys():
            if 'exif' in d['photo']:
                for dic in d['photo']['exif']:
                    for key, value in dic.items():
                        if value == 'Model':
                            model_list.append(dic['raw']['_content'])
    
    return model_list

def get_picture_url_from_photos(photos):
    url_list = []
    for d in photos:
        url_list.append(f"https://farm{d['farm']}.staticflickr.com/{d['server']}/{d['id']}_{d['secret']}.jpg")
    
    return url_list




#data = get_exif_from_photos(extract_photo_id(get_photos_from_keyword('antelopecanyon')))
# CACHE_DICT = load_cache()
# print(get_picture_url_from_photos(get_photos_from_keyword('antelopecanyon')))



def scrape_lens_db(link):    

    CACHE_DICT = load_cache()
    lens_href = []
    lens_name = []
    development_year = []
    brand = []
    lens_mount = []
    focal_min = []
    focal_max = []

    response = make_url_request_using_cache(link, CACHE_DICT)
    soup = BeautifulSoup(response, 'html.parser')

    #Make list of lens href
    lens_table = soup.find('table', class_='uk-table lensdb uk-table-divider')
    for item in lens_table.find_all(('a')):
        lens_href.append(item['href'])


    #Make list of lens name
    lens_table = soup.find('table', class_='uk-table lensdb uk-table-divider')
    for item in lens_table.find_all(('a')):
        del item['href']
        #lens_href.append(item['href'])
        lens_name.append(str(item).strip('</a>'))

    #Make list of lens announcement year

    lens_table = soup.find('table', class_='uk-table lensdb uk-table-divider')
    for item in lens_table.find_all('td', {'style' : 'min-width: 3%; text-align: center; '}):
        del item['style']
        development_year.append(str(item).strip('</td>'))

    #Extracting Brand data

    for lens in lens_name:
        brand.append(lens.split()[0])

    #Extracting mount data
    for lens in lens_name:
        split_lens = lens.split()
        if split_lens[0] == 'Fujifilm':
            lens_mount.append(f"{split_lens[0]} {split_lens[2]}")
        elif split_lens[0] == 'Canon':
            lens_mount.append(f"{split_lens[0]} {split_lens[1]}")
        elif split_lens[0] == 'Nikon':
            if 'Z' in split_lens:
                if 'DX' in split_lens:
                    lens_mount.append(f"{split_lens[0]} Z DX")
                else:
                    lens_mount.append(f"{split_lens[0]} Z")

            else:
                if 'AF' or 'AF-S' == split_lens[1]:
                    if 'DX' in split_lens:
                        lens_mount.append(f"{split_lens[0]} AF DX")
                    else:
                        lens_mount.append(f"{split_lens[0]} {split_lens[1]}")

        elif split_lens[0] == 'Sony':
            lens_mount.append(f"{split_lens[0]} {split_lens[1]}")

        elif split_lens[0] == 'Sigma' or 'Leica' or 'Panasonic':
            lens_mount.append("L Mount")


    #Extracting focal length
    for lens in lens_name:
        split_lens = lens.split()
        for info in split_lens:
            if 'mm' in info:
                if '-' in info:
                    focal_range = info.split('-')
                    focal_min.append(focal_range[0].strip('mm'))
                    focal_max.append(focal_range[1].strip('mm'))
                else:
                    focal_min.append(info.strip('mm'))
                    focal_max.append(info.strip('mm'))

    #Creating nested lists to write to sqlite

    lens_db = []
    lens_db.extend([list(a) for a in zip(lens_name, brand, lens_mount, focal_min, focal_max, lens_href)])

    return lens_db

def make_lens_name_list(link):

    CACHE_DICT = load_cache()

    lens_db = scrape_lens_db(link)
    
    lens_name = []
    
    for item in lens_db:
        lens_name.append(item[0])
    
    return lens_name

def make_lens_detail_list(link):

    CACHE_DICT = load_cache()

    lens_db = scrape_lens_db(link)
    lens_href = []
    
    for item in lens_db:
        lens_href.append(item[5])

    return lens_href

def scrape_example_photos(href):

    CACHE_DICT = load_cache()
    all_photos = []
    
    response = make_url_request_using_cache(href, CACHE_DICT)
    soup = BeautifulSoup(response, 'html.parser')
    for photo in soup.find_all(('a')):
        if 'flickr.com' in str(photo):
            photo = str(photo).split('\n')[0]
            for item in photo.split():
                if 'href' in item:
                    all_photos.append(item.strip(r'(href=)').strip('"<>'))
        elif 'data-caption' and 'ISO' in str(photo):
            photo = str(photo).split('<img')[0]
            for item in photo.split():
                if 'href' in item:
                    all_photos.append(item.strip(r'(href=)').strip('"<>'))

    all_photos = all_photos[:3]
    

    return all_photos


def make_list_for_example_photos_db(link):
    final_db = []
    ex_photo1 = []
    ex_photo2 = []
    ex_photo3 = []
    lens_name_list = make_lens_name_list(link)
    href_list = make_lens_detail_list(link)
    

    for href in href_list:
        example_photos = scrape_example_photos(href)
        try:
            ex_photo1.append(example_photos[0])
            ex_photo2.append(example_photos[1])
            ex_photo3.append(example_photos[2])
        except IndexError:
            ex_photo1.append("NAN")
            ex_photo2.append("NAN")
            ex_photo3.append("NAN")
        

    final_db.extend([list(a) for a in zip(lens_name_list, ex_photo1, ex_photo2, ex_photo3)])

    
    return final_db


def create_db():

    conn = sqlite3.connect("lens_db.sqlite")
    cur = conn.cursor()

    drop_lensdb = '''
        DROP TABLE IF EXISTS "LensDatabase";
    '''

    create_lensdb = '''
        CREATE TABLE IF NOT EXISTS "LensDatabase" (
            "LensName"  TEXT NOT NULL PRIMARY KEY,
            "Brand"  TEXT NOT NULL,
            "LensMount" TEXT NOT NULL,
            "FocalLengthMin"  INTEGER NOT NULL,
            "FocalLengthMax"  INTEGER NOT NULL,
            "LensInfoLink" TEXT NOT NULL
        );
    '''

    drop_example_photos_db = '''
        DROP TABLE IF EXISTS "LensExamplePhotos";
    '''

    create_example_photos_db = '''
        CREATE TABLE IF NOT EXISTS "LensExamplePhotos" (
            "Id" INTEGER PRIMARY KEY AUTOINCREMENT,
            "LensName"  TEXT NOT NULL NOT UNIQUE,
            "Example1"  TEXT NOT NULL,
            "Example2" TEXT NOT NULL,
            "Example3"  TEXT NOT NULL
            
        );
    '''

    cur.execute(drop_lensdb)
    cur.execute(create_lensdb)
    cur.execute(drop_example_photos_db)
    cur.execute(create_example_photos_db)

def update_db(lens_db, example_photos_db):
    conn = sqlite3.connect("lens_db.sqlite")
    cur = conn.cursor()

    insert_lens = '''
    INSERT INTO "LensDatabase"
    VALUES (?, ?, ?, ?, ?, ?)
    '''
    
    for lens in lens_db:
        cur.execute(insert_lens, lens)
    
    insert_example_photos = '''
    INSERT or IGNORE INTO "LensExamplePhotos"
    VALUES (?, ?, ?, ?)
    '''
    
    for lens in example_photos_db:
        cur.execute(insert_example_photos, lens)
    
    conn.commit()

def obtain_db():
    
    create_lens_db()

    lens_links = ('https://lens-db.com/lens-lineup/canon-ef/', 'https://lens-db.com/lens-lineup/canon-ef-m/',
                    'https://lens-db.com/lens-lineup/canon-ef-s/', 'https://lens-db.com/lens-lineup/canon-rf/',
                    'https://lens-db.com/lens-lineup/fujifilm-x/', 'https://lens-db.com/lens-lineup/leica-l-35mm/',
                    'https://lens-db.com/lens-lineup/nikon-f-35mm/', 'https://lens-db.com/lens-lineup/nikon-f-aps-c/',
                    'https://lens-db.com/lens-lineup/nikon-z-35mm/', 'https://lens-db.com/lens-lineup/nikon-z-aps-c/',
                    'https://lens-db.com/lens-lineup/sony-e/', 'https://lens-db.com/lens-lineup/sony-e-aps-c/')
    
    for link in lens_links:
        update_db(scrape_lens_db(link), make_list_for_example_photos_db(link))













