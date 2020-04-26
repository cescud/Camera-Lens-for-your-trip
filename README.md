# SI507 Final Project
Project Name: What Lens should you bring?
Creator: HoJoon Kim
Email: cescud@umich.edu

# Required Packages
- plotly
- pandas
- sqlite3

**Installing instructions** 

***python*** 
[https://packaging.python.org/tutorials/installing-packages/](https://packaging.python.org/tutorials/installing-packages/)

***Anaconda***
[https://docs.anaconda.com/anaconda/user-guide/tasks/install-packages/](https://docs.anaconda.com/anaconda/user-guide/tasks/install-packages/)

## FlickrAPI Key Instructions

You need to have a personal FlickrAPI Key to use this program. Instruction can be found in the below link
[https://www.flickr.com/services/api/misc.api_keys.html](https://www.flickr.com/services/api/misc.api_keys.html)

create a secrets.py file in your working directory folder where you cloned the program
and add your keys into secrets.py folder like below.

FLICKER_API_KEY = (Your key goes here)
FLICKER_API_SECRET = (Your secret goes here)

## Interaction with the program

- User will be prompted to enter a search keyward of locations he would like to photograph (e.g. antelopecanyon)

- Plotly bar graph of what focal length, brand, model was used to take the returned photos will be presented

- Links to actual photos (Access via CTRL + Click) will be presented.

- The user will be prompted to choose what brand of camera he or she is willing to bring to the trip

- The user will be prompted to choose what focal length she is planning to use (judging from the plotly visualizaiton. E.g. Antelope Canyon tends to be taken with Ultra Wide Angle Lenses)

- Lens information that meets the conditions of the user’s input will be displayed (Lens name, focal length, mount information, brand information, example photos of each lenses)

- You can click the link by (CTRL + Click) to see the lens information and example photos

### Note About Database

**Please use the provided lens_db.sqlite file**
If you do wish to create your own db, you can uncomment #obtain_db() in the interactive section of the
program (if __name__ = "__main__") however this part is scraping about 500 webpages so it will take about
30 minutes depending on your conditions

