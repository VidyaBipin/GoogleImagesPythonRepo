#!/usr/bin/env python
# In[ ]:
#  coding: utf-8

###### Searching and Downloading Google Images to the local disk ######

# Import Libraries
import sys

version = (3, 0)
cur_version = sys.version_info

if cur_version >= version:  # If the Current Version of Python is 3.0 or above
    import urllib.request
    from urllib.request import Request, urlopen
    from urllib.request import URLError, HTTPError
    from urllib.parse import quote
    import http.client
    from http.client import IncompleteRead, BadStatusLine
    http.client._MAXHEADERS = 1000
else:  # If the Current Version of Python is 2.x
    import urllib2
    from urllib2 import Request, urlopen
    from urllib2 import URLError, HTTPError
    from urllib import quote
    import httplib
    from httplib import IncompleteRead, BadStatusLine
    httplib._MAXHEADERS = 1000

import time  # Importing the time library to check the time of code execution
import os
import argparse
import ssl
import datetime
import json
import re
import codecs

from constants import (
    args_list,
    aspect_ratio_params,
    color_params,
    color_type_params,
    downloads_directory,
    format_params,
    google_search,
    lang_param,
    time_params,
    type_params,
    size_params,
    usage_rights_params,
    user_agent,
    user_agent_3,
)


def user_input():
    # Taking command line arguments from users
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', '--keywords', type=str, required=False,
                        help='Delimited list input')
    parser.add_argument('-kf', '--keywords_from_file',
                        help='Extract list of keywords from a text file', type=str, required=False)
    parser.add_argument('-sk', '--suffix_keywords', type=str, required=False,
                        help='Comma separated additional words added after to main keyword',)
    parser.add_argument('-pk', '--prefix_keywords', type=str, required=False,
                        help='Comma separated additional words added before main keyword')
    parser.add_argument('-l', '--limit', type=str, required=False,
                        help='Delimited list input')
    parser.add_argument('-f', '--format', type=str, required=False,
                        help='Download images with specific format',
                        choices=['jpg', 'gif', 'png', 'bmp', 'svg', 'webp', 'ico'])
    parser.add_argument('-u', '--url', type=str, required=False,
                        help='Search with google image URL')
    parser.add_argument('-x', '--single_image', type=str, required=False,
                        help='Downloading a single image from URL')
    parser.add_argument('-o', '--output_directory', type=str, required=False,
                        help='Download images in a specific main directory')
    parser.add_argument('-i', '--image_directory', type=str, required=False,
                        help='Download images in a specific sub-directory')
    parser.add_argument('-n', '--no_directory', default=False, action="store_true",
                        help='Download images in the main directory but no sub-directory')
    parser.add_argument('-d', '--delay', type=int, required=False,
                        help='Delay in seconds to wait between downloading two images')
    parser.add_argument('-co', '--color', type=str, required=False,
                        help='Filter on color',
                        choices=['red', 'orange', 'yellow', 'green', 'teal', 'blue', 'purple',
                                 'pink', 'white', 'gray', 'black', 'brown'])
    parser.add_argument('-ct', '--color_type', type=str, required=False,
                        help='Filter on color',
                        choices=['full-color', 'black-and-white', 'transparent'])
    parser.add_argument('-r', '--usage_rights', type=str, required=False,
                        help='Usage rights',
                        choices=['labeled-for-reuse-with-modifications', 'labeled-for-reuse',
                                 'labeled-for-noncommercial-reuse-with-modification', 'labeled-for-nocommercial-reuse'])
    parser.add_argument('-s', '--size', type=str, required=False,
                        help='Image size',
                        choices=['large', 'medium', 'icon', '>400*300', '>640*480', '>800*600', '>1024*768', '>2MP',
                                 '>4MP', '>6MP', '>8MP', '>10MP', '>12MP', '>15MP', '>20MP', '>40MP', '>70MP'])
    parser.add_argument('-es', '--exact_size', type=str, required=False,
                        help='Exact image resolution "WIDTH,HEIGHT"')
    parser.add_argument('-t', '--type', type=str, required=False,
                        help='Image type',
                        choices=['face', 'photo', 'clipart', 'line-drawing', 'animated'])
    parser.add_argument('-w', '--time', type=str, required=False,
                        help='Image age',
                        choices=['past-24-hours', 'past-7-days', 'past-month', 'past-year'])
    parser.add_argument('-wr', '--time_range', type=str, required=False,
                        help=('Time range for the age of the image. should be in the format'
                              ' {"time_min":"MM/DD/YYYY","time_max":"MM/DD/YYYY"}'))
    parser.add_argument('-a', '--aspect_ratio', type=str, required=False,
                        help='Comma separated additional words added to keywords',
                        choices=['tall', 'square', 'wide', 'panoramic'])
    parser.add_argument('-si', '--similar_images', type=str, required=False,
                        help='Downloads images very similar to the image URL you provide')
    parser.add_argument('-ss', '--specific_site', type=str, required=False,
                        help='Downloads images that are indexed from a specific website')
    parser.add_argument('-p', '--print_urls', default=False, action="store_true",
                        help="Print the URLs of the images")
    parser.add_argument('-ps', '--print_size', default=False, action="store_true",
                        help="Print the size of the images on disk")
    parser.add_argument('-pp', '--print_paths', default=False, action="store_true",
                        help="Prints the list of absolute paths of the images")
    parser.add_argument('-m', '--metadata', default=False, action="store_true",
                        help="Print the metadata of the image")
    parser.add_argument('-e', '--extract_metadata', default=False, action="store_true",
                        help="Dumps all the logs into a text file")
    parser.add_argument('-st', '--socket_timeout', default=False, type=float,
                        help="Connection timeout waiting for the image to download")
    parser.add_argument('-th', '--thumbnail', default=False, action="store_true",
                        help="Downloads image thumbnail along with the actual image")
    parser.add_argument('-tho', '--thumbnail_only', default=False, action="store_true",
                        help="Downloads only thumbnail without downloading actual images")
    parser.add_argument('-la', '--language', default=False, type=str, required=False,
                        help=("Defines the language filter. The search results are "
                              "authomatically returned in that language"),
                        choices=['Arabic', 'Chinese (Simplified)', 'Chinese (Traditional)', 'Czech', 'Danish', 'Dutch',
                                 'English', 'Estonian', 'Finnish', 'French', 'German', 'Greek', 'Hebrew', 'Hungarian',
                                 'Icelandic', 'Italian', 'Japanese', 'Korean', 'Latvian', 'Lithuanian', 'Norwegian',
                                 'Portuguese', 'Polish', 'Romanian', 'Russian', 'Spanish', 'Swedish', 'Turkish'])
    parser.add_argument('-pr', '--prefix', default=False,  type=str, required=False,
                        help="A word that you would want to prefix in front of each image name",)
    parser.add_argument('-px', '--proxy', type=str, required=False,
                        help='Specify a proxy address and port')
    parser.add_argument('-cd', '--chromedriver', type=str, required=False,
                        help='Specify the path to chromedriver executable in your local machine')
    parser.add_argument('-ri', '--related_images', default=False,  action="store_true",
                        help="Downloads images that are similar to the keyword provided")
    parser.add_argument('-sa', '--safe_search', default=False, action="store_true",
                        help="Turns on the safe search filter while searching for images")
    parser.add_argument('-nn', '--no_numbering', default=False, action="store_true",
                        help="Allows you to exclude the default numbering of images")
    parser.add_argument('-of', '--offset', type=str, required=False,
                        help="Where to start in the fetched links")
    parser.add_argument('-nd', '--no_download', default=False, action="store_true",
                        help="Prints the URLs of the images and/or thumbnails without downloading them")
    parser.add_argument('-iu', '--ignore_urls', default=False, type=str,
                        help="Delimited list input of image urls/keywords to ignore")
    parser.add_argument('-sil', '--silent_mode', default=False, action="store_true",
                        help="Remains silent. Does not print notification messages on the terminal")
    parser.add_argument('-is', '--save_source', type=str, required=False,
                        help="Creates a text file containing a list of downloaded images along with source page url")
    parser.add_argument('-cf', '--config_file', default='', type=str, required=False,
                        help='Config file name')

    args = vars(parser.parse_args())
    config_file_name = args['config_file']

    if config_file_name != '':
        if any(key != 'config_file' for key in args):
            print('Config file provided, ignoring other provided arguments')
        records = []
        json_file = json.load(open(config_file_name))

        for record in json_file['Records']:
            arguments = {}
            for argument in args_list:
                arguments[argument] = record.get(argument)
            records.append(arguments)
    else:
        records = [args]
    return records


class GoogleImagesDownload:
    def __init__(self):
        pass

    # Downloading entire Web Document (Raw Page Content)
    def download_page(self, url):
        headers = {}
        exception_text =\
            ("Could not open URL. Please check your internet connection and/or ssl settings \n"
             "If you are using proxy, make sure your proxy settings is configured correctly")
        if cur_version >= version:  # If the Current Version of Python is 3.0 or above
            try:
                headers['User-Agent'] = user_agent_3
                req = urllib.request.Request(url, headers=headers)
                resp = urllib.request.urlopen(req)
                resp_data = str(resp.read())
                return resp_data
            except Exception as e:
                print(exception_text)
                sys.exit()
        else:  # If the Current Version of Python is 2.x
            try:
                headers['User-Agent'] = user_agent
                req = urllib2.Request(url, headers=headers)
                try:
                    response = urllib2.urlopen(req)
                except URLError:  # Handling SSL certificate failed
                    context = ssl._create_unverified_context()
                    response = urlopen(req, context=context)
                page = response.read()
                return page
            except:
                print(exception_text)
                sys.exit()
                return "Page Not found"

    # Download Page for more than 100 images
    def download_extended_page(self, url, chromedriver):
        from selenium import webdriver
        from selenium.webdriver.common.keys import Keys

        if cur_version < version:
            reload(sys)
            sys.setdefaultencoding('utf8')

        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument("--headless")

        try:
            browser = webdriver.Chrome(chromedriver, chrome_options=options)
        except Exception as e:
            print("Looks like we cannot locate the path the 'chromedriver' (use the '--chromedriver' "
                  "argument to specify the path to the executable.) or google chrome browser is not "
                  "installed on your machine (exception: %s)" % e)
            sys.exit()
        browser.set_window_size(1024, 768)

        # Open the link
        browser.get(url)
        time.sleep(1)
        print("Getting you a lot of images. This may take a few moments...")

        element = browser.find_element_by_tag_name("body")
        # Scroll down
        for i in range(30):
            element.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.3)

        try:
            browser.find_element_by_id("smb").click()
            for i in range(50):
                element.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.3)  # bot id protection
        except:
            for i in range(10):
                element.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.3)  # bot id protection

        print("Reached end of Page.")
        time.sleep(0.5)

        source = browser.page_source  # Page source
        # Close the browser
        browser.close()

        return source

    # Correcting the escape characters for python2
    def replace_with_byte(self, match):
        return chr(int(match.group(0)[1:], 8))

    def repair(self, broken_json):
        invalid_escape = re.compile(r'\\[0-7]{1,3}')  # Up to 3 digits for byte values up to FF
        return invalid_escape.sub(self.replace_with_byte, broken_json)

    # Finding 'Next Image' from the given raw page
    def get_next_tab(self, s):
        start_line = s.find('class="dtviD"')
        if start_line == -1:  # If no links are found then give an error!
            end_quote = 0
            link = "no_tabs"
            return link, '', end_quote
        else:
            start_line = s.find('class="dtviD"')
            start_content = s.find('href="', start_line + 1)
            end_content = s.find('">', start_content + 1)
            url_item = "https://www.google.com" + str(s[start_content + 6:end_content])
            url_item = url_item.replace('&amp;', '&')

            start_line_2 = s.find('class="dtviD"')
            s = s.replace('&amp;', '&')
            start_content_2 = s.find(':', start_line_2 + 1)
            end_content_2 = s.find('&usg=', start_content_2 + 1)
            url_item_name = str(s[start_content_2 + 1:end_content_2])

            chars = url_item_name.find(',g_1:')
            chars_end = url_item_name.find(":", chars + 6)
            if chars_end == -1:
                updated_item_name = (url_item_name[chars + 5:]).replace("+", " ")
            else:
                updated_item_name = (url_item_name[chars+5:chars_end]).replace("+", " ")

            return url_item, updated_item_name, end_content

    # Getting all links with the help of '_images_get_next_image'
    def get_all_tabs(self, page):
        tabs = {}
        while True:
            item, item_name, end_content = self.get_next_tab(page)
            if item == "no_tabs":
                break
            else:
                if len(item_name) > 100 or item_name == "background-color":
                    break
                else:
                    tabs[item_name] = item  # Append all the links in the list named 'Links'
                    time.sleep(0.1)  # Timer could be used to slow down the request for image downloads
                    page = page[end_content:]
        return tabs

    # Format the object in readable format
    def format_object(self, object):
        formatted_object = {}
        formatted_object['image_format'] = object['ity']
        formatted_object['image_height'] = object['oh']
        formatted_object['image_width'] = object['ow']
        formatted_object['image_link'] = object['ou']
        formatted_object['image_description'] = object['pt']
        formatted_object['image_host'] = object['rh']
        formatted_object['image_source'] = object['ru']
        formatted_object['image_thumbnail_url'] = object['tu']
        return formatted_object

    # Function to download single image
    def single_image(self, url):
        extensions = (".jpg", ".gif", ".png", ".bmp", ".svg", ".webp", ".ico")

        try:
            os.makedirs(downloads_directory)
        except OSError as e:
            if e.errno != 17:
                raise

        req = Request(url, headers={"User-Agent": user_agent})

        response = urlopen(req, None, 10)
        data = response.read()
        response.close()

        image_name = str(url[(url.rfind('/')) + 1:])
        if '?' in image_name:
            image_name = image_name[:image_name.find('?')]

        # if ".jpg" or ".gif" or ".png" or ".bmp"
        # or ".svg" or ".webp" or ".ico" not in image_name:
        if not any(map(lambda extension: extension in image_name, extensions)):
            image_name = image_name + ".jpg"

        file_name = downloads_directory + "/" + image_name

        try:
            output_file = open(file_name, 'wb')
            output_file.write(data)
            output_file.close()
        except (IOError, OSError) as e:
            raise e
        print("completed ====> " + image_name.encode('raw_unicode_escape').decode('utf-8'))
        return

    def similar_images(self, similar_images):
        if cur_version >= version:  # If the Current Version of Python is 3.0 or above
            try:
                searchUrl = 'https://www.google.com/searchbyimage?site=search&sa=X&image_url=' + similar_images
                headers = {}
                headers['User-Agent'] = user_agent_3

                req1 = urllib.request.Request(searchUrl, headers=headers)
                resp1 = urllib.request.urlopen(req1)
                content = str(resp1.read())
                l1 = content.find('AMhZZ')
                l2 = content.find('&', l1)
                urll = content[l1:l2]

                newurl = "https://www.google.com/search?tbs=sbi:" + urll + "&site=search&sa=X"
                req2 = urllib.request.Request(newurl, headers=headers)
                resp2 = urllib.request.urlopen(req2)
                l3 = content.find('/search?sa=X&amp;q=')
                l4 = content.find(';', l3 + 19)
                urll2 = content[l3 + 19:l4]
                return urll2
            except:
                return "Cloud not connect to Google Images endpoint"
        else:  # If the Current Version of Python is 2.x
            try:
                search_url = 'https://www.google.com/searchbyimage?site=search&sa=X&image_url=' + similar_images
                headers = {}
                headers['User-Agent'] = user_agent

                req1 = urllib2.Request(search_url, headers=headers)
                resp1 = urllib2.urlopen(req1)
                content = str(resp1.read())
                l1 = content.find('AMhZZ')
                l2 = content.find('&', l1)
                urll = content[l1:l2]

                newurl = "https://www.google.com/search?tbs=sbi:" + urll + "&site=search&sa=X"
                req2 = urllib2.Request(newurl, headers=headers)
                resp2 = urllib2.urlopen(req2)
                l3 = content.find('/search?sa=X&amp;q=')
                l4 = content.find(';', l3 + 19)
                urll2 = content[l3 + 19:l4]
                return(urll2)
            except:
                return "Cloud not connect to Google Images endpoint"

    # Building URL parameters
    def build_url_parameters(self, arguments):
        if arguments['language']:
            lang = "&lr="
            lang_url = lang + lang_param[arguments['language']]
        else:
            lang_url = ''

        if arguments['time_range']:
            json_acceptable_string = arguments['time_range'].replace("'", "\"")
            d = json.loads(json_acceptable_string)
            time_range = ',cdr:1,cd_min:' + d['time_min'] + ',cd_max:' + d['time_max']
        else:
            time_range = ''

        if arguments['exact_size']:
            size_array = [x.strip() for x in arguments['exact_size'].split(',')]
            exact_size = ",isz:ex,iszw:" + str(size_array[0]) + ",iszh:" + str(size_array[1])
        else:
            exact_size = ''

        built_url = "&tbs="
        counter = 0
        params = {
            'color': [arguments['color'], color_params],
            'color_type': [arguments['color_type'], color_type_params],
            'usage_rights': [arguments['usage_rights'], usage_rights_params],
            'size': [arguments['size'], size_params],
            'type': [arguments['type'], type_params],
            'time': [arguments['time'], time_params],
            'aspect_ratio': [arguments['aspect_ratio'], aspect_ratio_params],
            'format': [arguments['format'], format_params]
        }
        for key, value in params.items():
            if value[0] is not None:
                ext_param = value[1][value[0]]
                # counter will tell if it is first param added or not
                if counter == 0:
                    # add it to the built url
                    built_url = built_url + ext_param
                    counter += 1
                else:
                    built_url = built_url + ',' + ext_param
                    counter += 1
        built_url = lang_url+built_url+exact_size+time_range
        return built_url

    # Building main search URL
    def build_search_url(self, search_term, params, url, similar_images,
                         specific_site, safe_search):
        # Check safe_search
        safe_search_string = "&safe=active"
        # Check the args and choose the URL
        if url:
            url = url
        elif similar_images:
            print(similar_images)
            keywordem = self.similar_images(similar_images)
            url = google_search + keywordem + '&espv=2&biw=1366&bih=667&site=webhp&source=lnms&tbm=isch&sa=X&ei=XosDVaCXD8TasATItgE&ved=0CAcQ_AUoAg'
        elif specific_site:
            url = google_search + quote(
                search_term.encode('utf-8')) + '&as_sitesearch=' + specific_site + '&espv=2&biw=1366&bih=667&site=webhp&source=lnms&tbm=isch' + params + '&sa=X&ei=XosDVaCXD8TasATItgE&ved=0CAcQ_AUoAg'
        else:
            url = google_search + quote(
                search_term.encode('utf-8')) + '&espv=2&biw=1366&bih=667&site=webhp&source=lnms&tbm=isch' + params + '&sa=X&ei=XosDVaCXD8TasATItgE&ved=0CAcQ_AUoAg'

        # Safe search check
        if safe_search:
            url = url + safe_search_string

        return url

    # Measures the file size
    def file_size(self, file_path):
        if os.path.isfile(file_path):
            file_info = os.stat(file_path)
            size = file_info.st_size
            for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
                if size < 1024.0:
                    return "%3.1f %s" % (size, x)
                size /= 1024.0
            return size

    # Keywords from file
    def keywords_from_file(self, file_name):
        search_keyword = []
        with codecs.open(file_name, 'r', encoding='utf-8-sig') as f:
            if '.csv' in file_name or '.txt' in file_name:
                for line in f:
                    if line in ['\n', '\r\n']:
                        pass
                    else:
                        search_keyword.append(line.replace('\n', '').replace('\r', ''))
            else:
                print("Invalid file type: Valid file types are either .txt or .csv \n"
                      "exiting...")
                sys.exit()
        return search_keyword

    # Make directories
    def create_directories(self, main_directory, dir_name,
                           thumbnail, thumbnail_only):
        dir_name_thumbnail = dir_name + " - thumbnail"
        # Make a search keyword  directory
        try:
            if not os.path.exists(main_directory):
                os.makedirs(main_directory)
                time.sleep(0.2)
                path = (dir_name)
                sub_directory = os.path.join(main_directory, path)
                if not os.path.exists(sub_directory):
                    os.makedirs(sub_directory)
                if thumbnail or thumbnail_only:
                    sub_directory_thumbnail = os.path.join(main_directory, dir_name_thumbnail)
                    if not os.path.exists(sub_directory_thumbnail):
                        os.makedirs(sub_directory_thumbnail)
            else:
                path = (dir_name)
                sub_directory = os.path.join(main_directory, path)
                if not os.path.exists(sub_directory):
                    os.makedirs(sub_directory)
                if thumbnail or thumbnail_only:
                    sub_directory_thumbnail = os.path.join(main_directory, dir_name_thumbnail)
                    if not os.path.exists(sub_directory_thumbnail):
                        os.makedirs(sub_directory_thumbnail)
        except OSError as e:
            if e.errno != 17:
                raise
            pass
        return

    # Download Image thumbnails
    def download_image_thumbnail(self, image_url, main_directory, dir_name, return_image_name,
                                 print_urls, socket_timeout, print_size, no_download,
                                 save_source, img_src):
        if print_urls or no_download:
            print("Image URL: " + image_url)
        if no_download:
            return "success", "Printed url without downloading"
        try:
            req = Request(image_url, headers={"User-Agent": user_agent})
            try:
                # Timeout time to download an image
                if socket_timeout:
                    timeout = float(socket_timeout)
                else:
                    timeout = 10

                response = urlopen(req, None, timeout)
                data = response.read()
                response.close()

                path = main_directory + "/" + dir_name + " - thumbnail" + "/" + return_image_name

                try:
                    output_file = open(path, 'wb')
                    output_file.write(data)
                    output_file.close()
                    if save_source:
                        list_path = main_directory + "/" + save_source + ".txt"
                        list_file = open(list_path, 'a')
                        list_file.write(path + '\t' + img_src + '\n')
                        list_file.close()
                    download_status = 'success'
                    download_message = "Completed Image Thumbnail ====> " + return_image_name

                except (OSError, IOError) as e:
                    download_status = 'fail'
                    download_message = "{} on an image...trying next one... Error: {}".\
                        format(e.__name__, str(e))

                # Image size parameter
                if print_size:
                    print("Image Size: " + str(self.file_size(path)))

            except UnicodeEncodeError as e:
                download_status = 'fail'
                download_message = "UnicodeEncodeError on an image...trying next one..." + " Error: " + str(e)

        except (HTTPError, URLError, ssl.CertificateError, IOError) as e:
            download_status = 'fail'
            download_message = "{} on an image...trying next one... Error: {}". \
                format(e.__name__, str(e))

        return download_status, download_message

    # Download Images
    def download_image(self, image_url, image_format, main_directory, dir_name,
                       count, print_urls, socket_timeout, prefix, print_size,
                       no_numbering, no_download, save_source, img_src, silent_mode,
                       thumbnail_only, format, ignore_urls):
        if not silent_mode:
            if print_urls or no_download:
                print("Image URL: " + image_url)
        if ignore_urls:
            if any(url in image_url for url in ignore_urls.split(',')):
                return "fail", "Image ignored due to 'ignore url' parameter", None, image_url
        if thumbnail_only:
            return "success", "Skipping image download...", str(image_url[(image_url.rfind('/')) + 1:]), image_url
        if no_download:
            return "success", "Printed url without downloading", None, image_url
        try:
            req = Request(image_url, headers={"User-Agent": user_agent})
            try:
                # Timeout time to download an image
                if socket_timeout:
                    timeout = float(socket_timeout)
                else:
                    timeout = 10

                response = urlopen(req, None, timeout)
                data = response.read()
                response.close()

                extensions = [".jpg", ".jpeg", ".gif", ".png", ".bmp", ".svg", ".webp", ".ico"]
                # Keep everything after the last '/'
                image_name = str(image_url[(image_url.rfind('/')) + 1:])
                if format:
                    if not image_format or image_format != format:
                        download_status = 'fail'
                        download_message = "Wrong image format returned. Skipping..."
                        return_image_name = ''
                        absolute_path = ''
                        return download_status, download_message, return_image_name, absolute_path

                if image_format == "" or not image_format or "." + image_format not in extensions:
                    download_status = 'fail'
                    download_message = "Invalid or missing image format. Skipping..."
                    return_image_name = ''
                    absolute_path = ''
                    return download_status, download_message, return_image_name, absolute_path
                elif image_name.lower().find("." + image_format) < 0:
                    image_name = image_name + "." + image_format
                else:
                    image_name = image_name[:image_name.lower().find("." + image_format) + (len(image_format) + 1)]

                # Prefix name in image
                if prefix:
                    prefix = prefix + " "
                else:
                    prefix = ''

                if no_numbering:
                    path = main_directory + "/" + dir_name + "/" + prefix + image_name
                else:
                    path = main_directory + "/" + dir_name + "/" + prefix + str(count) + "." + image_name

                try:
                    output_file = open(path, 'wb')
                    output_file.write(data)
                    output_file.close()
                    if save_source:
                        list_path = main_directory + "/" + save_source + ".txt"
                        list_file = open(list_path, 'a')
                        list_file.write(path + '\t' + img_src + '\n')
                        list_file.close()
                    absolute_path = os.path.abspath(path)
                    # Return image name back to calling method to use it for thumbnail downloads
                    download_status = 'success'
                    download_message = "Completed Image ====> " + prefix + str(count) + "." + image_name
                    return_image_name = prefix + str(count) + "." + image_name

                except OSError as e:
                    download_status = 'fail'
                    download_message = "OSError on an image...trying next one..." + " Error: " + str(e)
                    return_image_name = ''
                    absolute_path = ''

                # Image size parameter
                if not silent_mode:
                    if print_size:
                        print("Image Size: " + str(self.file_size(path)))

            except (UnicodeEncodeError, URLError, BadStatusLine) as e:
                download_status = 'fail'
                download_message = "{} on an image...trying next one... Error: {}".\
                    format(e.__name__, str(e))
                return_image_name = ''
                absolute_path = ''

        except (HTTPError, URLError, ssl.CertificateError, IOError, IncompleteRead) as e:
            download_status = 'fail'
            download_message = "{} on an image...trying next one... Error: {}".\
                format(e.__name__, str(e))
            return_image_name = ''
            absolute_path = ''

        return download_status, download_message, return_image_name, absolute_path

    # Finding 'Next Image' from the given raw page
    def _get_next_item(self, s):
        start_line = s.find('rg_meta notranslate')
        if start_line == -1:  # If no links are found then give an error!
            end_quote = 0
            link = "no_links"
            return link, end_quote
        else:
            start_line = s.find('class="rg_meta notranslate">')
            start_object = s.find('{', start_line + 1)
            end_object = s.find('</div>', start_object + 1)
            object_raw = str(s[start_object:end_object])

            # Remove escape characters based on python version
            if cur_version >= version: # python3
                try:
                    object_decode = bytes(object_raw, "utf-8").decode("unicode_escape")
                    final_object = json.loads(object_decode)
                except:
                    final_object = ""
            else:  # python2
                try:
                    final_object = (json.loads(self.repair(object_raw)))
                except:
                    final_object = ""
            return final_object, end_object

    # Getting all links with the help of '_images_get_next_image'
    def _get_all_items(self, page, main_directory, dir_name,
                       limit, arguments):
        items = []
        abs_path = []
        errorCount = 0
        i = 0
        count = 1
        while count < limit+1:
            object, end_content = self._get_next_item(page)
            if object == "no_links":
                break
            elif object == "":
                page = page[end_content:]
            elif arguments['offset'] and count < int(arguments['offset']):
                    count += 1
                    page = page[end_content:]
            else:
                # Format the item for readability
                object = self.format_object(object)
                if arguments['metadata']:
                    if not arguments["silent_mode"]:
                        print("\nImage Metadata: " + str(object))

                # Download the images
                download_status, download_message, return_image_name, absolute_path = \
                    self.download_image(object['image_link'], object['image_format'], main_directory, dir_name,
                                        count, arguments['print_urls'], arguments['socket_timeout'],
                                        arguments['prefix'], arguments['print_size'], arguments['no_numbering'],
                                        arguments['no_download'], arguments['save_source'], object['image_source'],
                                        arguments["silent_mode"], arguments["thumbnail_only"], arguments['format'],
                                        arguments['ignore_urls'])
                if not arguments["silent_mode"]:
                    print(download_message)
                if download_status == "success":

                    # Download image_thumbnails
                    if arguments['thumbnail'] or arguments["thumbnail_only"]:
                        download_status, download_message_thumbnail = \
                            self.download_image_thumbnail(
                                object['image_thumbnail_url'], main_directory, dir_name, return_image_name,
                                arguments['print_urls'], arguments['socket_timeout'], arguments['print_size'],
                                arguments['no_download'], arguments['save_source'], object['image_source'],
                                arguments['ignore_urls'])
                        if not arguments["silent_mode"]:
                            print(download_message_thumbnail)

                    count += 1
                    object['image_filename'] = return_image_name
                    items.append(object)  # Append all the links in the list named 'Links'
                    abs_path.append(absolute_path)
                else:
                    errorCount += 1

                # Delay param
                if arguments['delay']:
                    time.sleep(int(arguments['delay']))

                page = page[end_content:]
            i += 1
        if count < limit:
            print("\n\nUnfortunately all " + str(
                limit) + " could not be downloaded because some images were not downloadable. " + str(
                count-1) + " is all we got for this search filter!")
        return items, errorCount, abs_path

    # Bulk Download
    def download(self, arguments):
        paths_agg = {}
        # For input coming from other python files
        if __name__ != "__main__":
            # If the calling file contains config_file param
            if 'config_file' in arguments:
                records = []
                total_errors = 0
                json_file = json.load(open(arguments['config_file']))

                for record in json_file['Records']:
                    arguments = {}
                    for argument in args_list:
                        arguments[argument] = record.get(argument)
                    records.append(arguments)

                for rec in records:
                    paths, errors = self.download_executor(rec)
                    for i in paths:
                        paths_agg[i] = paths[i]
                    if not arguments["silent_mode"] and arguments['print_paths']:
                        print(paths.encode('raw_unicode_escape').decode('utf-8'))
                    total_errors = total_errors + errors

                return paths_agg, total_errors

            # If the calling file contains params directly
            else:
                paths, errors = self.download_executor(arguments)
                for i in paths:
                    paths_agg[i] = paths[i]
                if not arguments["silent_mode"] and arguments['print_paths']:
                    print(paths.encode('raw_unicode_escape').decode('utf-8'))

                return paths_agg, errors
        # For input coming from CLI
        else:
            paths, errors = self.download_executor(arguments)
            for i in paths:
                paths_agg[i] = paths[i]
            if not arguments["silent_mode"] and arguments['print_paths']:
                print(paths.encode('raw_unicode_escape').decode('utf-8'))
        return paths_agg, errors

    def download_executor(self, arguments):
        paths = {}

        for arg in args_list:
            if arg not in arguments:
                arguments[arg] = None

        # Initialization and Validation of user arguments
        if arguments['keywords']:
            search_keyword = [str(item) for item in arguments['keywords'].split(',')]

        if arguments['keywords_from_file']:
            search_keyword = self.keywords_from_file(arguments['keywords_from_file'])

        # Both time and time range should not be allowed in the same query
        if arguments['time'] and arguments['time_range']:
            raise ValueError('Either time or time range should be used in a query. '
                             'Both cannot be used at the same time.')

        # Both time and time range should not be allowed in the same query
        if arguments['size'] and arguments['exact_size']:
            raise ValueError('Either "size" or "exact_size" should be used in a query. '
                             'Both cannot be used at the same time.')

        # Both image directory and no image directory should not be allowed in the same query
        if arguments['image_directory'] and arguments['no_directory']:
            raise ValueError('You can either specify image directory or specify no image directory, not both!')

        # Additional words added to keywords
        if arguments['suffix_keywords']:
            suffix_keywords = [" " + str(sk) for sk in arguments['suffix_keywords'].split(',')]
        else:
            suffix_keywords = ['']

        # Additional words added to keywords
        if arguments['prefix_keywords']:
            prefix_keywords = [str(sk) + " " for sk in arguments['prefix_keywords'].split(',')]
        else:
            prefix_keywords = ['']

        # Setting limit on number of images to be downloaded
        if arguments['limit']:
            limit = int(arguments['limit'])
        else:
            limit = 100

        if arguments['url']:
            current_time = str(datetime.datetime.now()).split('.')[0]
            search_keyword = [current_time.replace(":", "_")]

        if arguments['similar_images']:
            current_time = str(datetime.datetime.now()).split('.')[0]
            search_keyword = [current_time.replace(":", "_")]

        # If single_image or url argument not present then keywords is mandatory argument
        if arguments['single_image'] is None and arguments['url'] is None and arguments['similar_images'] is None and arguments['keywords'] is None and arguments['keywords_from_file'] is None:
            print('-------------------------------\n'
                  'Uh oh! Keywords is a required argument \n\n'
                  'Please refer to the documentation on guide to writing queries \n'
                  'https://github.com/hardikvasa/google-images-download#examples'
                  '\n\nexiting!\n'
                  '-------------------------------')
            sys.exit()

        # If this argument is present, set the custom output directory
        if arguments['output_directory']:
            main_directory = arguments['output_directory']
        else:
            main_directory = downloads_directory

        # Proxy settings
        if arguments['proxy']:
            os.environ["http_proxy"] = arguments['proxy']
            os.environ["https_proxy"] = arguments['proxy']
            # Initialization Complete

        total_errors = 0
        for pky in prefix_keywords:                 # 1.For every prefix keywords
            for sky in suffix_keywords:             # 2.For every suffix keywords
                i = 0
                while i < len(search_keyword):      # 3.For every main keyword
                    iteration = "\n" + "Item no.: " + str(i + 1) + " -->" + " Item name = " + (pky) + (search_keyword[i]) + (sky)
                    if not arguments["silent_mode"]:
                        print(iteration.encode('raw_unicode_escape').decode('utf-8'))
                        print("Evaluating...")
                    else:
                        print("Downloading images for: " + (pky) + (search_keyword[i]) + (sky) + " ...")
                    search_term = pky + search_keyword[i] + sky

                    if arguments['image_directory']:
                        dir_name = arguments['image_directory']
                    elif arguments['no_directory']:
                        dir_name = ''
                    else:
                        dir_name = search_term + ('-' + arguments['color'] if arguments['color'] else '')  # Sub-directory

                    if not arguments["no_download"]:
                        self.create_directories(main_directory, dir_name, arguments['thumbnail'],
                                                arguments['thumbnail_only'])  # Create directories in OS

                    params = self.build_url_parameters(arguments)     # Building URL with params

                    url = self.build_search_url(
                        search_term, params, arguments['url'], arguments['similar_images'],
                        arguments['specific_site'], arguments['safe_search'])  # Building main search url

                    if limit < 101:
                        raw_html = self.download_page(url)  # Download page
                    else:
                        raw_html = self.download_extended_page(url, arguments['chromedriver'])

                    if not arguments["silent_mode"]:
                        if arguments['no_download']:
                            print("Getting URLs without downloading images...")
                        else:
                            print("Starting Download...")
                    items, errorCount, abs_path = self._get_all_items(
                        raw_html, main_directory, dir_name, limit, arguments)  # Get all image items and download images
                    paths[pky + search_keyword[i] + sky] = abs_path

                    # Dumps into a json file
                    if arguments['extract_metadata']:
                        try:
                            if not os.path.exists("logs"):
                                os.makedirs("logs")
                        except OSError as e:
                            print(e)
                        json_file = open("logs/"+search_keyword[i]+".json", "w")
                        json.dump(items, json_file, indent=4, sort_keys=True)
                        json_file.close()

                    # Related images
                    if arguments['related_images']:
                        print("\nGetting list of related keywords...this may take a few moments")
                        tabs = self.get_all_tabs(raw_html)
                        for key, value in tabs.items():
                            final_search_term = (search_term + " - " + key)
                            print("\nNow Downloading - " + final_search_term)
                            if limit < 101:
                                new_raw_html = self.download_page(value)  # Download page
                            else:
                                new_raw_html = self.download_extended_page(value, arguments['chromedriver'])
                            self.create_directories(main_directory, final_search_term,
                                                    arguments['thumbnail'], arguments['thumbnail_only'])
                            self._get_all_items(new_raw_html, main_directory,
                                                search_term + " - " + key, limit, arguments)

                    i += 1
                    total_errors = total_errors + errorCount
                    if not arguments["silent_mode"]:
                        print("\nErrors: " + str(errorCount) + "\n")
        return paths, total_errors


# Main Program
def main():
    records = user_input()
    total_errors = 0
    t0 = time.time()  # start the timer

    for arguments in records:
        if arguments['single_image']:  # Download Single Image using a URL
            response = GoogleImagesDownload()
            response.single_image(arguments['single_image'])
        else:  # Or download multiple images based on keywords/keyphrase search
            response = GoogleImagesDownload()
            paths, errors = response.download(arguments)  # Wrapping response in a variable just for consistency
            total_errors = total_errors + errors

        t1 = time.time()  # Stop the timer
        total_time = t1 - t0  # Calculating the total time required to crawl, find and download all the links of 60,000 images
        if not arguments["silent_mode"]:
            print("\nEverything downloaded!")
            print("Total errors: " + str(total_errors))
            print("Total time taken: " + str(total_time) + " Seconds")


if __name__ == "__main__":
    main()

# In[ ]:
