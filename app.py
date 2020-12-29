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
  "short": "shortURL",
  "spurious":"spuriousURL",
  "spur": "spurURL",
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


# ***** Mobile API Part ***** #
@app.route("/Detect", methods=["GET"])
def detectEndPoint():
  try:
    temp_img= request.files["temp_image"]
    test_img= request.files["test_image"]
    temp_img.save(os.path.join("test_temps", "temp_img.png"))
    test_img.save(os.path.join("test_temps", "test_img.png"))

    id = "ID"

    image_differencing("test_temps/temp_img.png","test_temps/test_img.png",id)
    extract_defects_using_contours("diff_img/diff_" + id + ".png",id)

    cnt = count_contours(id) # number of defects
    defects = {
      "status": "success",
      "list":[]
    }
    images = os.listdir("contours/"+id)
    for imageName in images:
      image_defect_type = predict("contours/"+id+"/"+imageName)
      type = image_defect_type["Category"]
      if type != "not_defect":
        img_def = {
          "ImageId": imageName[:-4],
          "type": type,
          "solutionUrl":sol_urls[type]
        }
        defects["list"].append(img_def)
      else:
        cnt-=1
    defects["numberOfDefects"] = cnt
    return defects, 200

  except Exception as e:
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
    path = os.getcwd()+"/contours/"+id +"/" + imageID+".png"
    return send_file(path)

  except Exception as e:
    res = {
    "status":"faild",
    "message":"Some thing wrong!, try again later and make sure ImgaeId is correct"
    #"exception":str(e)
    }
    return res, 500
if __name__ == "__main__":
    app.debug = True
    app.run('0.0.0.0')

