# pdf_modifier_generator

# pdf text modifier/generator

A pdf text modifier Flask app that can be used to modify text in the pdf


## Setup

* Clone the repository using:
```
git clone "this repo"
```
* Install requirements
```
pip3 install -r requirements.txt
```

## How to use

* Run the app using `python app.py`
* In your browser navigate to `localhost:5000`
* Select the pdf you want to modify
* The image will be displayed 
* Drag on the image, on the part which you want to modify
* On the left write the name of the annotation and click enter
* If you want to delete an annotation click "-" button beside the annotation
* Click the next button to go to the next pdf page
* Modify all the pages in the pdf
* At last, download the zip file

## Run using Docker

* Build the Docker image using the Dockerfile

```bash
docker build -t <image-name-here> .
```

* Run the Docker image

```bash
docker run -d -p 5000:5000 <pdf-name-here>
```

* Naviage to `localhost:5000` in your browser


