from flask import Flask, request, jsonify, send_file
import json
from api.image_differencing import *
from api.classifier import *
from api.utility import *
import cv2

app = Flask(__name__)

def string_to_number(str):
  if("." in str):
    try:
      res = float(str)
    except:
      res = str
  elif(str.isdigit()):
    res = int(str)
  else:
    res = str
  return(res)

sol_urls = {
  "short": """To repair “short” defect (we apply the way of Etching.
Etching is a "subtractive" method used for elimination of the excess copper from a PCB which an acid is used to remove unwanted copper from a PCB. 

To get rid of all unwanted copper follow these etching steps:
1.	applying a temporary mask that protects parts of the desired copper from the acid and keeps it untouched
2.	Put the board in the acid (ferric chloride (Eisen-3-Chlorid) and Sodium Persulfate) tank for about 20 minutes until the unwanted copper are completely etched. 
3.	Move the board into the rinse tank for a few seconds in order to clean it from the acid. You can also use an Isopropanol spray for cleaning.
4.	Dry the board with a cloth.
5.	After that paint the place of etching with solder mask to make sure that will be no electric conductance in that place.
""",
  "spurious":"""To repair “spurious copper” defect we apply the way of Etching.
Etching is a "subtractive" method used for elimination of the excess copper from a PCB which an acid is used to remove unwanted copper from a PCB. 

To get rid of all unwanted copper follow these etching steps:
1.	applying a temporary mask that protects parts of the desired copper from the acid and keeps it untouched
2.	Put the board in the acid (ferric chloride (Eisen-3-Chlorid) and Sodium Persulfate) tank for about 20 minutes until the unwanted copper are completely etched. 
3.	Move the board into the rinse tank for a few seconds in order to clean it from the acid. You can also use an Isopropanol spray for cleaning.
4.	Dry the board with a cloth.
5.	After that paint the place of etching with solder mask to make sure that will be no electric conductance in that place.
""",
  "spur": """To repair ‘spur’ defect we apply the way of Etching.
Etching is a ‘subtractive’ method used for elimination of the excess copper from a PCB which an acid is used to remove unwanted copper from a PCB. 

To get rid of all unwanted copper follow these etching steps:
1.	applying a temporary mask that protects parts of the desired copper from the acid and keeps it untouched
2.	Put the board in the acid (ferric chloride (Eisen-3-Chlorid) and Sodium Persulfate) tank for about 20 minutes until the unwanted copper are completely etched. 
3.	Move the board into the rinse tank for a few seconds in order to clean it from the acid. You can also use an Isopropanol spray for cleaning.
4.	Dry the board with a cloth.
5.	After that paint the place of etching with solder mask to make sure that will be no electric conductance in that place.
""",
  "not_defect":"Not detected defect type!"
}

@app.after_request
def add_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With"
    response.headers['Access-Control-Allow-Methods'] = "POST, GET, PUT, DELETE, OPTIONS"
    return response

@app.route("/call_function/", methods=["GET"])
def call_function():
    print("args = ",request)
    passed_function = request.args.get('function')
    print("---------------------------------------")
    print("Function = ", passed_function)
    print("---------------------------------------")
    args = dict(request.args)
    values = list(args.values())[1:]
    values = list(map(string_to_number, values))
    res = globals()[passed_function](*tuple(values))
    print("Resources = ", res)
    return(jsonify(res))

def imageIsColored(path):
  im_gray = cv2.imread(path)
  return not (im_gray[0][0][0] == im_gray[0][0][1] and im_gray[0][0][0] == im_gray[0][0][2])
# ***** Mobile API Part ***** #
@app.route("/Detect", methods=["GET"])
def detectEndPoint():
  try:
    temp_img= request.files["temp_image"]
    test_img= request.files["test_image"]
    temp_img.save(os.path.join("test_temps", "temp_img.png"))
    test_img.save(os.path.join("test_temps", "test_img.png"))

    if imageIsColored(os.path.join("test_temps", "temp_img.png")):
      convertToBw(os.path.join("test_temps", "temp_img.png"))
      convertToBw(os.path.join("test_temps", "test_img.png"))


    id = "ID"

    image_differencing("test_temps/temp_img.png","test_temps/test_img.png",id)
    extract_defects_using_contours("diff_img/diff_" + id + ".png",id)

    cnt = 0 # number of defects
    defects = {
      "status": "success",
      "list":[]
    }
    images = os.listdir("contours/"+id)
    for imageName in images:
      if("big" in imageName):
        continue
      image_defect_type = predict("contours/"+id+"/"+imageName)
      type = image_defect_type["Category"]
      if type != "not_defect":
        img_def = {
          "ImageId": imageName[:-4],
          "type": type,
          "solutionUrl":sol_urls[type]
        }
        defects["list"].append(img_def)
        cnt+=1
    defects["numberOfDefects"] = cnt
    return defects, 200

  except Exception as e:
    print(e)
    res = {
      "status":"faild",
      "message":"Some thing wrong!, try again later"
      #"exception":str(e)
    }
    return res, 500

@app.route("/GetImage/", methods=["GET"])
def getImage():
  id = "ID"
  try:
    imageID = request.args.get("ImageId")
    if(imageID == "diff"):
      path = os.getcwd()+"/diff_img/diff_ID.png"
      return send_file(path)
    else:
      path = os.getcwd()+"/contours/"+id +"/" + imageID+".png"
      return send_file(path)

  except Exception as e:
    res = {
    "status":"faild",
    "message":"Some thing wrong!, try again later and make sure ImgaeId is correct"
    #"exception":str(e)
    }
    return res, 500

def convertToBw(path):
  im_gray = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
  thresh = 127
  im_bw = cv2.threshold(im_gray, thresh, 255, cv2.THRESH_BINARY)[1]
  im_bw = cv2.bitwise_not(im_bw)
  cv2.imwrite(path, im_bw)
  
# @app.route("/Detect/colored", methods=["GET"])
# def detectColoredEndPoint():
#   try:
#     temp_img= request.files["temp_image"]
#     test_img= request.files["test_image"]
#     temp_img.save(os.path.join("test_temps", "temp_img.png"))
#     test_img.save(os.path.join("test_temps", "test_img.png"))
#     print(os.path.join("test_temps", "test_img.png"))
#     convertToBw(os.path.join("test_temps", "temp_img.png"))
#     convertToBw(os.path.join("test_temps", "test_img.png"))
    

#     id = "ID"

#     image_differencing("test_temps/temp_img.png","test_temps/test_img.png",id)
#     extract_defects_using_contours("diff_img/diff_" + id + ".png",id)

#     cnt = 0 # number of defects
#     defects = {
#       "status": "success",
#       "list":[]
#     }
#     images = os.listdir("contours/"+id)
#     for imageName in images:
#       if("big" in imageName):
#         continue
#       image_defect_type = predict("contours/"+id+"/"+imageName)
#       type = image_defect_type["Category"]
#       if type != "not_defect":
#         img_def = {
#           "ImageId": imageName[:-4],
#           "type": type,
#           "solutionUrl":sol_urls[type]
#         }
#         defects["list"].append(img_def)
#         cnt+=1
#     defects["numberOfDefects"] = cnt
#     return defects, 200

#   except Exception as e:
#     print(e)
#     res = {
#       "status":"faild",
#       "message":"Some thing wrong!, try again later"
#       #"exception":str(e)
#     }
#     return res, 500

if __name__ == "__main__":
    app.debug = True
    app.run('0.0.0.0')

