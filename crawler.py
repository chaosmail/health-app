from bs4 import BeautifulSoup, NavigableString
import urllib.request
import os, re, pprint, string, json


base_url = "http://www.health.ch/"
data_dir = "data/"
results_file = "results.json"


def parse_name(name):
    return re.sub(r"\s{2,}|&nbsp;", " ", name)

def parse_link(link):
    return re.sub(r"/$", "/index.html", re.sub(r"^/", "", link))

def parse_phone(phone):
    return re.sub(r"^Tel: ", "", phone)

def parse_fax(fax):
    return re.sub(r"^Fax: ", "", fax)

def load_page(page):

    url = base_url + page
    file_path = data_dir + page
    file_dir = os.path.dirname(file_path)
    html = ""

    print("Using", url, file_path)

    # Create Folder, it it doesnot exist
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
        print("Creating", file_dir)

    # Download and save Webpage, if it doesnot exist
    if not os.path.exists(file_path):
        result = urllib.request.urlopen(url)
        html = result.read()
        print("Downloading", url)

        file_handle = open(file_path, 'wb')
        file_handle.write(html)
        file_handle.close()
        print("Storing", file_path)

    # Read Webpage from results directory
    else:
        file_handle = open(file_path, 'rb')
        html = file_handle.read()
        file_handle.close()
        print("Reading", file_path)

    # Initialize Beautiful Soup
    return BeautifulSoup(html)


# Start traversing the page from here
dirs = [{'name': 'Doctors', 'sub_url': 'doctors/index.html', 'ch': []}]

for d in dirs:

    # Load the Webpage
    page = load_page(d["sub_url"])

    # Load the Categories of the Register
    categories = page.find_all(attrs={"class": "text-schwarz-block"})

    for category in categories:

        cat_name = parse_name( category.string )
        cat_sub_url = parse_link( category.get('href') )
        cat_slug = os.path.basename( os.path.dirname(cat_sub_url) )
        cat_children = []

        # Dont consider external Links
        if re.match(r"^http://", cat_sub_url):
            continue

        # Loop over the alphabet
        for l in string.ascii_lowercase:

            page_sub_url = cat_slug + "/" + cat_slug + "_n_" + l + ".html"
            page_sub_page = load_page(page_sub_url)

            vip_pages = page_sub_page.find_all(attrs={"class": "text-vip-home-block"})

            novip_pages = page_sub_page.find_all(attrs={"class": "text-novip-home-block"})

            for entry in novip_pages:

                en_name = parse_name( entry.string.replace(u"\u00A0", " ") )
                en_sub_url = parse_link( entry.get("href") )

                # Fix this
                if isinstance(entry.next_sibling.next_sibling, NavigableString):
                    continue

                cells = entry.next_sibling.next_sibling.contents

                address = str(cells[0].contents[0]).replace(u"\u00A0", " ")
                email = str(cells[0].contents[3].string).replace(u"\u00A0", " ") if len(cells[0].contents) > 3 else ""
                phone = parse_phone( str(cells[1].contents[0]).replace(u"\u00A0", " ") )
                fax = parse_fax( str(cells[1].contents[2]).replace(u"\u00A0", " ") if len(cells[1].contents) > 2 else "")

                cat_children.append({'name': en_name, 'sub_url': en_sub_url, 'address': address, 'email': email, 'phone': phone, 'fax': fax})

        d["ch"].append({'name': cat_name, 'sub_url': cat_sub_url, 'ch':  cat_children})

# pp = pprint.PrettyPrinter(indent=2)
# pp.pprint(dirs)

file_handle = open(results_file, 'w')
file_handle.write(json.dumps(dirs))
file_handle.close()