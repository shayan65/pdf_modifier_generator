# author: Shayan Hemmatiyan
import os
import shutil
from PIL import Image
import sys
sys.path.append("./src")
from src.generate import Generate
import cv2
from flask import (
    Flask,
    flash,
    request,
    render_template,
    redirect,
    url_for,
    session,
    send_from_directory,
    send_file,
    send_from_directory,
    send_file,
)
import uuid
import logging
import glob
import shutil
from pdf2image import convert_from_path
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
import numpy as np
from pathlib import Path




UPLOAD_FOLDER = os.path.basename(".") + "/static/tmp/upload"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
DOWNLOAD_FOLDER = os.path.basename(".") + "/static/tmp/download"
app.config["DOWNLOAD_FOLDER"] = DOWNLOAD_FOLDER
ZIP_FOLDER = os.path.basename(".") + "/static/tmp/zip"
app.config["ZIP_FOLDER"] = ZIP_FOLDER
os.environ["KMP_DUPLICATE_LIB_OK"] = "True"

def mk_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)
for path in [os.path.basename(".") + "/static/tmp",
             os.path.basename(".")+"/static/tmp/download",
             os.path.basename(".")+"/static/tmp/upload"]:
    mk_dir(path)


# Secret key for sessions encryption
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
__author__ = "Shayan Hemmatiyan <shemmatiyan@gliquidx.com>"
__source__ = ""
# logging stuff
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s: %(message)s"
)
logging.getLogger("werkzeug").setLevel(logging.DEBUG)
LOGGER = logging.getLogger(__name__)



@app.route("/health")
def health():
    LOGGER.info("Application is running successfully!")
    return "App is Running!"



def upload_folder(uid):
    return os.path.join(UPLOAD_FOLDER, uid)


def download_folder(uid):
    return os.path.join(DOWNLOAD_FOLDER, uid)


def make_tmp_dirs(uid):
    LOGGER.info("making tmp dirs for uid: " + uid)
    try:
        mk_dir(download_folder(uid))
        mk_dir(upload_folder(uid))
        mk_dir(zip_folder(uid))

    except:
        LOGGER.error("error while making tmp dirs")

def zip_folder(uid):
    return os.path.join(ZIP_FOLDER, uid)

def remove_tmp_dirs(uid):
    try:
        shutil.rmtree(upload_folder(uid))
        shutil.rmtree(download_folder(uid))
    except:
        LOGGER.info("error while removing tmp files")

def fileType(fileName):
    fileName = fileName.replace("\\", "/")
    return (str(fileName.split("/")[-1]).split(".")[-1]).lower()


def fileName(filePath):
    filePath = filePath.replace("\\", "/")
    return str(filePath.split("/")[-1]).split(".")[0]

@app.route("/")
def home():
    return render_template("index.html", title="Document Generator")
    # redirect('/generator', code=302)

@app.route('/generate',methods = ['GET', 'POST'])
def generate():
    if request.method == 'POST':
        LOGGER.info("received post request")
        # if 'file' not in request.files:
        #     flash('No files selected')
        #     return redirect('/')
        # try:
        #     shutil.rmtree('./images')
        # except:
        #     pass
        # os.mkdir('./images')
        uid = request.form.get("documentId")
        mk_dir("tmp")
        if not uid:
            uid = str(uuid.uuid4())
            LOGGER.info("generated uid: " + uid)
        else:
            LOGGER.info("received documentId: " + uid)
        make_tmp_dirs(uid)
        file = request.files.get("file")
        print("file", file)
        if not file:
            msg = "file was not uploaded"
            LOGGER.error(msg)
            return msg, 400
        pdf = os.path.join(upload_folder(uid), file.filename)
        file.save(pdf)
        # files = request.files.getlist("file")

        app.config["download_folder"] = str(download_folder(uid))
        app.config["upload_folder"]=str(upload_folder(uid))
        img_paths = [str(upload_folder(uid) + "/" + file.filename)]
        for img_path in img_paths:
            pages = convert_from_path(img_path,200)
        # Counter to store images of each page of PDF to image
        image_counter = 1
        # Iterate through all the pages stored above
        doc_names = []
        imgslst = []
        files =[]
        for page in pages:
            image = np.array(pages[image_counter-1])[:, :, ::-1]
            imgslst.append(image)    
            # get pixel at position y=10, x=15
            # where pix is an array of R, G, B.
            # e.g. pix[0] is the red part of the pixel
            #pix = image[10,15]
            
            # Declaring filename for each page of PDF as JPG
            doc_name = os.path.join(
                download_folder(uid),
                "page"
                + str(image_counter)
                + "_"
                + str(fileName(file.filename))
                + ".png",
            )
            files.append(doc_name)
            # Save the image of the page in system
            page.save(doc_name, "png")
            # Increment the counter to update filename
            image_counter = image_counter + 1
        cv2imgs = np.array(imgslst)
        del imgslst
        app.config["FILES"] = files
      
    else:
        files=[]
        app.config["download_folder"] = "./"
        app.config["FILES"] = files
    return redirect('tagger', code=302)
 

@app.route('/tagger')
def tagger():
    if (app.config["HEAD"] == len(app.config["FILES"])):
        app.config["HEAD"] = 0
        return redirect(url_for('final'))
    directory = app.config["download_folder"].replace("\\","/")
    print("directory", directory)
    print("Is directory existed? ",os.path.exists(directory))
    image = app.config["FILES"][app.config["HEAD"]].replace("\\","/")
    image = fileName(image) +"."+image.split(".")[-1]
    file_ = directory+"/"+image

    print("is image exist?", os.path.exists(file_))
    labels = app.config["LABELS"]
    print("labels", labels)
    not_end = not(app.config["HEAD"] == len(app.config["FILES"]) - 1)
    print(not_end)
    return render_template('tagger.html', not_end=not_end, directory=directory,\
         image=image, labels=labels, head=app.config["HEAD"] + 1, len=len(app.config["FILES"]),code=305)

@app.route('/next')
def next():
    image = app.config["FILES"][app.config["HEAD"]]
    img = cv2.imread(image)
    new_img = img.copy()
    download_f = app.config["download_folder"]
    app.config["HEAD"] = app.config["HEAD"] + 1
    with open(app.config["OUT"],'a') as f:
        for label in app.config["LABELS"]:
            bb = [[round(float(label["xMin"])), round(float(label["yMin"]))],
                  [round(float(label["xMax"])), round(float(label["yMax"]))]]
            print("bb", bb)
            new_img = Generate(new_img, image, download_f, bb,str(label["name"])).gen()
            f.write(image + "," +
            label["id"] + "," +
            label["name"] + "," +
            str(round(float(label["xMin"]))) + "," +
            str(round(float(label["xMax"]))) + "," +
            str(round(float(label["yMin"]))) + "," +
            str(round(float(label["yMax"]))) + "\n")
    cv2.imwrite(str(download_f)+"/gen_"+str(fileName(image) +".png"), new_img)
    #cv2.imwrite("fig.png", new_img)
    app.config["LABELS"] = []
    del new_img
    return redirect('tagger')

@app.route("/final")
def final():
    return render_template('final.html')

@app.route('/add/<id>')
def add(id):
    xMin = request.args.get("xMin")
    xMax = request.args.get("xMax")
    yMin = request.args.get("yMin")
    yMax = request.args.get("yMax")
    bb = [[xMin, yMin],[xMax, yMax]]

    app.config["LABELS"].append({"id":id, "name":"", "xMin":xMin, "xMax":xMax, "yMin":yMin, "yMax":yMax})
    return redirect(url_for('tagger'))

@app.route('/remove/<id>')
def remove(id):
    index = int(id) - 1
    del app.config["LABELS"][index]
    for label in app.config["LABELS"][index:]:
        label["id"] = str(int(label["id"]) - 1)
    return redirect(url_for('tagger'))

@app.route('/label/<id>')
def label(id):
    name = request.args.get("name")
    app.config["LABELS"][int(id) - 1]["name"] = name
    return redirect(url_for('tagger'))

@app.route('/image/<f>')
def images(f):
    images = app.config["download_folder"]
    return send_file(images +'/'+f)

@app.route('/download')
def download():
    mk_dir("images")
    # shutil.copyfile('out.csv', 'images/annotations.csv')
    for file_ in glob.glob(os.path.join(app.config["download_folder"], "gen*")):
        shutil.copy(file_,"images/"+fileName(file_)+".png" )
    shutil.make_archive('final', 'zip', 'images')
    shutil.rmtree(app.config["download_folder"])
    shutil.rmtree(app.config["upload_folder"])
    shutil.rmtree("images")
    
    
    return send_file('final.zip',
                     mimetype='text/csv',
                     attachment_filename='final.zip',
                     as_attachment=True)

if __name__ == "__main__":
    app.config["download_folder"] = 'images'
    app.config["LABELS"] = []
    app.config["HEAD"] = 0
    app.config["OUT"] = "out.csv"
    with open("out.csv",'w') as f:
        f.write("image,id,name,xMin,xMax,yMin,yMax\n")
    app.run(host='0.0.0.0', debug="True",use_reloader=True)
