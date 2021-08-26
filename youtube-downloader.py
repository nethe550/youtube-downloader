import argparse
import json
import re
import os
from sys import argv
from pytube import YouTube

# Used to check against the config version
VERSION = "1.0.0"
AUTHOR  =  "nethe550"

WHITE  = '\033[0m'
RED    = '\033[31m'
GREEN  = '\033[32m'
ORANGE = '\033[33m'
BLUE   = '\033[34m'
PURPLE = '\033[35m'

config = None
try:
    with open('config.jsonc', 'r') as file:
        try:
            # regex to remove comments from jsonc format
            config = json.loads(re.sub("//.*", "", file.read(), flags=re.MULTILINE))
            
        except Exception:
            print("Unable to read config.jsonc. Is it corrupted?")
            exit()
            
except Exception:
    print("Unable to find config.jsonc. Make sure it is in the same folder as this program.")
    exit()

# Windows-specific auto-completion of defaultDownloadPath
if os.name == 'nt':
    import win32api
    config['defaultDownloadPath'] = config['defaultDownloadPath'].replace('<USERNAME>', win32api.GetUserName())

if not config["version"] == VERSION:
    print(f"Invalid config version! Current version: {VERSION}")
    exit()

parameters = {
    "-u": {
        "aliases": ["--url"],
        "help": "Specify the URL of the video.",
        "dest": "url",
        "nargs": 1,
        "required": True,
        "metavar": f"{RED}<video url>{WHITE}"
    },
    "-p": {
        "aliases": ["--path"],
        "help": "Specify the path to download the video to.",
        "dest": "path",
        "default": config["defaultDownloadPath"],
        "nargs": 1,
        "metavar": f"{ORANGE}<download path>{WHITE}"
    },
    "-f": {
        "aliases": ["--format"],
        "help": "Specify the format of the downloaded video",
        "dest": "format",
        "default": config["defaultFormat"],
        "nargs": 1,
        "metavar": f"{ORANGE}<mp4|webm>{WHITE}",
        "choices": ["mp4", "webm"]
    }
}

splash = f"""
    {WHITE} /$$     /$${RED} /$$$$$$$$      {GREEN} /$$$$$$$                                    /$$                           /$$\                   {WHITE}    
    {WHITE}|  $$   /$$/{RED}|__  $$__/      {GREEN}| $$__  $$                                  | $$                          | $$                    {WHITE} 
    {WHITE} \  $$ /$$/ {RED}   | $$         {GREEN}| $$  \ $$  /$$$$$$  /$$  /$$  /$$ /$$$$$$$ | $$  /$$$$$$   /$$$$$$   /$$$$$$$  /$$$$$$   /$$$$$$ {WHITE}     
    {WHITE}  \  $$$$/  {RED}   | $$         {GREEN}| $$  | $$ /$$__  $$| $$ | $$ | $$| $$__  $$| $$ /$$__  $$ |____  $$ /$$__  $$ /$$__  $$ /$$__  $${WHITE}      
    {WHITE}   \  $$/   {RED}   | $$         {GREEN}| $$  | $$| $$  \ $$| $$ | $$ | $$| $$  \ $$| $$| $$  \ $$  /$$$$$$$| $$  | $$| $$$$$$$$| $$  \__/{WHITE}      
    {WHITE}    | $$    {RED}   | $$         {GREEN}| $$  | $$| $$  | $$| $$ | $$ | $$| $$  | $$| $$| $$  | $$ /$$__  $$| $$  | $$| $$_____/| $$      {WHITE}
    {WHITE}    | $$    {RED}   | $$         {GREEN}| $$$$$$$/|  $$$$$$/|  $$$$$/$$$$/| $$  | $$| $$|  $$$$$$/|  $$$$$$$|  $$$$$$$|  $$$$$$$| $$      {WHITE}
    {WHITE}    |__/    {RED}   |__/         {GREEN}|_______/  \______/  \_____/\___/ |__/  |__/|__/ \______/  \_______/ \_______/ \_______/|__/      {WHITE}

        {GREEN}By {ORANGE}{AUTHOR} {BLUE}(v{VERSION}){WHITE}
"""

def read_args(argv):
    """Print the splash screen, parse, and return the command-line arguments"""
    
    print(splash)
    
    help_formatter = lambda prog: argparse.HelpFormatter(prog, max_help_position=45, width=200)
    
    parser = argparse.ArgumentParser(description="", 
                                     add_help=False, 
                                     allow_abbrev=True, 
                                     epilog=f"Youtube Downloader v{VERSION}",
                                     formatter_class=help_formatter)
    
    parser._positionals.title = "Required arguments: "
    parser._optionals.title = "Optional arguments: "
    
    parser.add_argument('-v', '--version', 
                        action='version', 
                        version=f'v{VERSION}')
    
    parser.add_argument('-h', '--help', 
                        action='help', 
                        default=argparse.SUPPRESS, 
                        help="Show this help message.")
    
    for arg in parameters:
        options = [arg]
        for alias in parameters[arg]["aliases"]:
            options.append(alias)
            
        if "required" in parameters[arg]:
            parser.add_argument(*options, 
                                help=parameters[arg]["help"], 
                                nargs=parameters[arg]["nargs"],
                                dest=parameters[arg]["dest"], 
                                metavar=parameters[arg]["metavar"],
                                required=parameters[arg]["required"])
            
        else:
            if "default" in parameters[arg]:
                parser.add_argument(*options, 
                                    help=parameters[arg]["help"], 
                                    nargs=parameters[arg]["nargs"], 
                                    dest=parameters[arg]["dest"], 
                                    default=parameters[arg]["default"], 
                                    metavar=parameters[arg]["metavar"])
                
            else:    
                parser.add_argument(*options, 
                                    help=parameters[arg]["help"], 
                                    nargs=parameters[arg]["nargs"], 
                                    dest=parameters[arg]["dest"], 
                                    metavar=parameters[arg]["metavar"])
                
    return parser.parse_args(argv[1:])

def validate_args(args):
    """Checks if the given arguments are complete and valid according to 'parameters'"""
    
    if not os.path.exists(args['path']):
        print('The download path provided is invalid.\n\t- If you provided a path, make sure it exists.\n\t- Otherwise, check the config.jsonc \'defaultDownloadPath\' option.')
    
    if 'url' in args and 'path' in args and 'format' in args:
        for choice in parameters["-f"]["choices"]:
            if choice in args["format"]:
                return True
            
    else:
        print("Invalid arguments. see '--help'.")
        exit()
        
    return False

# =============== #

def download_progress(stream = None, chunk = None, bytes_remaining = None):
    """Track the downloaded percentage of the video"""
    
    if file_size == -1:
        return
    
    else:
        percent_completed = (100 * (file_size - bytes_remaining)) / file_size
        print("{:00.0f}% downloaded...".format(percent_completed))

def download_complete(stream, file_path):
    """Notify the user when the download is completed"""
    
    print(f"Video downloaded to '{file_path}'")

def main():
    """The main program. Downloads a Youtube video according to the command-line arguments"""
    
    if (len(argv) > 1):
        arg_vars = vars(read_args(argv))
        
        args = {}
        for arg in arg_vars:
            if type(arg_vars[arg]) == list:
                args[arg] = arg_vars[arg][0]
                
            else:
                args[arg] = arg_vars[arg]

        
        if (validate_args(args)):
            url = args["url"]
            
            print("Getting video...")
            video = None
            try:
                video = YouTube(args["url"], on_progress_callback=download_progress, on_complete_callback=download_complete)
                video.bypass_age_gate()
            except Exception:
                print(f"Video is unavailable. Make sure the link exists and is valid.\nURL: ({url})")
                exit()
            
            print("Getting video details...")
            title = video.title
            length = video.length
            rating = video.rating
            views = video.views
            author = video.author
            
            print("Getting video streams...")
            mp4_stream = video.streams.filter(progressive=True, file_extension="mp4").order_by('resolution').desc().first()
            webm_stream = video.streams.filter(progressive=True, file_extension="webm").order_by('resolution').desc().first()
            
            global file_size
            
            print("Selecting video format...")
            if args["format"] == "mp4":
                if not mp4_stream == None:
                    try:
                        try:
                            file_size = mp4_stream.filesize
                            
                        except Exception:
                            print("Cannot read mp4 stream size; download progress unknown until completed.")
                            file_size = -1
                            
                        mp4_stream.download(args["path"])
                        
                    except Exception:
                        print(f"Failed to download video. <mp4>\nURL: ({url})")
                        exit()
                        
                else:
                    print(f"Unable to get mp4 stream of the video. Try another format.\nURL: {url}")
                    exit()
                    
            elif args["format"] == "webm":
                if not webm_stream == None:
                    try:
                        try:
                            file_size = webm_stream.filesize
                            
                        except Exception:
                            print("Cannot read webm stream size; download progress unknown until completed.")
                            file_size = -1
                            
                        webm_stream.download(args["path"])
                        
                    except Exception:
                        print(f"Failed to download video. <webm>\nURL: ({url})")
                        exit()
                        
                else:
                    print(f"Unable to get webm stream of the video. Try another format.\nURL: {url}")
                    exit()
                    
            else:
                print("I'm not sure how you got to this point, but there seems to be an issue with your specified format.")
                exit()
                
                
            extra_data = input("Do you want extra info on the video? (y/n): ")
            if extra_data == "y" or extra_data == "yes":
                extra = f"\tTitle: {title}\n\tVideo Length: {length}\n\tRating: {rating}\n\tViews: {views}\n\tAuthor: {author}\n"
                print("")
                print(extra)
                
            elif extra_data == "n" or extra_data == "no":
                print("Extra data omitted.")
                
            else:
                print("You didn't pick yes (or no), so the program will exit.")

            print(f"{GREEN}Thanks for using {WHITE}You{RED}Tube {GREEN}Downloader.{WHITE}")
            exit()
                
        else:
            print("Invalid arguments passed. see '--help'.")
            exit()

    else:
        print(f"Arguments required. see '--help'.")
        exit()
        
if __name__ == '__main__':
    try:
        main()
        
    except Exception:
        print("I'm not sure how you got to this point, but there seems to be an issue with the program itself. Make sure it isn't corrupted.")