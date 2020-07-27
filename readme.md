# Parser of books from web-site tululu.org

You can download books, covers of books from web-site [tululu.org](http://tululu.org/) automatically. Besides, you can get json-file with data of your books. 

### How to install

* Check that you have Python 3  
* Install requirements:  
```sh
$ pip install -r requirements.txt
```
* How to start parser  
```sh
python parse_tululu_category.py
```

### Arguments

You can use positional arguments:  
`--start_page` - You can choose first page to download books, default=1  
`--end_page` - You can choose last page to download books, default=1  
`--dest_folder` - You can choose destination folder for files 
`--skip_json` - You can skip downloading json  
`--skip_txt` - You can skip downloading books  
`--skip_images` - You can skip downloading images  

### Purpose

Code was writing for learning purpose as a part of course for web-developers [dvmn.org](https://dvmn.org/).