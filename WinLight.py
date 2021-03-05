#! /usr/bin/python

# Import modules
import requests
import re
import os
import hashlib
import pathlib
import colorama

# Set environment variables
ImageUrl = "https://img-prod-cms-rt-microsoft-com.akamaized.net/cms/api/am/imageFileData"

JsonUrls = [
    "https://arc.msn.com/v3/Delivery/Placement?&fmt=json&cdm=1&ctry=FR&pid=209567",
    "https://arc.msn.com/v3/Delivery/Placement?&fmt=json&cdm=1&ctry=FR&pid=279978",
    "https://arc.msn.com/v3/Delivery/Placement?&fmt=json&cdm=1&ctry=FR&pid=338380",
    "https://arc.msn.com/v3/Delivery/Placement?&fmt=json&cdm=1&ctry=FR&pid=338387",
    "https://arc.msn.com/v3/Delivery/Placement?&fmt=json&cdm=1&ctry=FR&pid=338387"
]

SearchPattern = "(?<=imageFileData/).*?(?=\?ver)"
HttpHeader = {
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'no-cache',
    'User-Agent': 'WindowsShellClient/9.0.40929.0 (Windows)'
}

# Some colors
ColorRed = colorama.Fore.RED
ColorGreen = colorama.Fore.GREEN
ColorBlue = colorama.Fore.BLUE
ColorCyan = colorama.Fore.CYAN
ColorYellow = colorama.Fore.YELLOW
ColorBlack = colorama.Fore.BLACK
ColorWhite = colorama.Fore.WHITE
StyleBright = colorama.Style.BRIGHT
StyleDim = colorama.Style.DIM
StyleNormal = colorama.Style.NORMAL
ResetColor = colorama.Style.RESET_ALL

# Try all Urls
for JsonUrl in JsonUrls:

    print(f'{ColorWhite}' + 'Parsing ' + f'{StyleDim}' + JsonUrl +
          f'{StyleNormal}' + ' to find images...' + f'{ResetColor}')
    # Download JSON file
    Respose = requests.get(JsonUrl, headers=HttpHeader)
    content_raw = Respose.text

    # Remove back slashes
    content_raw = content_raw.replace("\\", "")

    # Remove opening quotes
    content_raw = content_raw.replace("\"{", "{")

    # Remove closing quotes
    content_raw = content_raw.replace("}\"", "}")

    # Get the hashes from links and download
    hash = re.findall(SearchPattern, content_raw, re.DOTALL)
    for i in hash:
        j = ImageUrl + "/" + i
        FileName = i + ".jpg"
        print(f'{ColorCyan}' + "Downloading " + f'{StyleDim}' + j +
              f'{ResetColor}')
        Respose = requests.get(j, headers=HttpHeader)
        # Ignore files less that 2 KB which are blank
        if int(Respose.headers['Content-Length']) < 2048:
            print(f'{ColorRed}' + 'Ignoring ' + i + ': ' + f'{StyleBright}' +
                  'file too small (' + Respose.headers['Content-Length'] +
                  ' bytes)' + f'{ResetColor}')
            continue
        # Check if the file already exist
        if os.path.isfile(FileName):
            OldHash = hashlib.md5(
                pathlib.Path(FileName).read_bytes()).hexdigest()
            NewHash = hashlib.md5(Respose.content).hexdigest()
            # Do we have the same content on disk?
            if OldHash != NewHash:
                NewFileName = i + '-' + NewHash + '.jpg'
                print(f'{ColorCyan}' +
                      'File already exist with different content, renaming ' +
                      f'{StyleBright}' + FileName + f'{StyleNormal}' + ' to ' +
                      f'{StyleBright}' + NewFileName + f'{ResetColor}')
                FileName = NewFileName
            print(f'{ColorYellow}' + 'Ignoring ' + i + ': ' + 'We ' +
                  f'{StyleBright}' + 'already downloaded' + f'{StyleNormal}' +
                  ' this file with the ' + f'{StyleBright}' +
                  'exact same content.' + f'{ResetColor}')
            continue
        with open(FileName, 'wb') as file:
            file.write(Respose.content)
            print(f'{ColorGreen}' + 'Saved as ' + f'{StyleBright}' + FileName +
                  f'{ResetColor}')
