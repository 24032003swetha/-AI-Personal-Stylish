from flask import Flask, render_template
import os
import cv2
from cvzone.PoseModule import PoseDetector
import cvzone

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/products')
def products():
    return render_template('products.html')

@app.route('/account')
def account():
    return render_template('account.html')

@app.route('/productdetails')
def productdetails():
    return render_template('productdetails.html')

@app.route('/productdetails1')
def productdetails1():
    return render_template('productdetails1.html')

@app.route('/productdetails2')
def productdetails2():
    return render_template('productdetails2.html')

@app.route('/productdetails3')
def productdetails3():
    return render_template('productdetails3.html')

@app.route('/productdetails4')
def productdetails4():
    return render_template('productdetails4.html')

@app.route('/productdetails5')
def productdetails5():
    return render_template('productdetails5.html')

@app.route('/productdetails6')
def productdetails6():
    return render_template('productdetails6.html')

@app.route('/productdetails7')
def productdetails7():
    return render_template('productdetails7.html')

# Try now 
@app.route('/trynow')
def tryNow():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Change to front camera
    detector = PoseDetector()

    shirtFolderPath = "Resources/Shirts"
    listShirts = os.listdir(shirtFolderPath)
    fixedRatio = 250/100 * 0.3  # widthOfShirt/WidthOfPoint 11 to 12
    shirtRatioHeightWidth = 100/340 * 0.2
    imageNumber = 0
    imgButtonRight = cv2.imread("Resources/button.png", cv2.IMREAD_UNCHANGED)
    imgButtonLeft = cv2.flip(imgButtonRight, 1)
    counterRight = 0
    counterLeft = 0
    selectionSpeed = 10
    width = 1000
    height = 1000
    dim = (width, height)
    offset = (0, 0)  # Define offset here
    heightOfShirt = 0  # default value
    widthOfShirt = 0  # default value
    flag = True
   
    while flag:
        success, img = cap.read()
        frame = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
        img = detector.findPose(img)
        lmlist, bboxInfo = detector.findPosition(img, bboxWithHands=False, draw=False)
        if lmlist:
            lm11 = lmlist[11][1:3]
            lm12 = lmlist[12][1:3]
            midpoint = ((lm11[0] + lm12[0]) // 2, (lm11[1] + lm12[1] + heightOfShirt) // 2)
            offset = (25, 50 + heightOfShirt)
            imgShirt_path = os.path.join(shirtFolderPath, listShirts[imageNumber])
            if os.path.exists(imgShirt_path):
                imgShirt = cv2.imread(imgShirt_path, cv2.IMREAD_UNCHANGED)
                
                img = cvzone.overlayPNG(img, imgShirt, (midpoint[0] - offset[0], midpoint[1] - offset[1]))
                # Check if image shirt is not None
                if imgShirt is not None:
                    # Calculate dimensions for resizing
                    if abs(lm11[0]-lm12[0])>0:
                        widthOfShirt = int(abs(lm11[0] - lm12[0])*0.3 * fixedRatio)
                        heightOfShirt = int(widthOfShirt * shirtRatioHeightWidth)

                    # Check if dimensions are valid
                    if widthOfShirt > 0 and heightOfShirt > 0:
                        imgShirt = cv2.resize(imgShirt, (widthOfShirt, heightOfShirt))
                        print("Overlaying shirt image...")
                        print("Shirt image path:", imgShirt_path)
                        print("Shirt image dimensions:", imgShirt.shape)
                        currentScale = abs(lm11[0] - lm12[0]) / 190
                        offset = (int(44 * currentScale), int(48 * currentScale))
                        if lm11[0] < lm12[0]:
                            offset = (-offset[0], offset[1])

                            
                        print("Overlay position:", (lm12[0] - offset[0], lm12[1] - offset[1]))
                        imgShirt = cv2.resize(imgShirt, (widthOfShirt, heightOfShirt))

                        currentScale = (lm11[0] - lm12[0]) / 190
                        offset = (int(25 * currentScale), int(18 * currentScale))

                        try:
                            img = cvzone.overlayPNG(img, imgShirt, (lm12[0] - offset[0], lm12[1] - offset[1]))
                            # Ensure imgButtonRight and imgButtonLeft are loaded successfully
                            if imgButtonRight is not None and imgButtonLeft is not None:
                                print("Overlaying buttons...")
                                img = cvzone.overlayPNG(img, imgButtonRight, (490, 293))
                                img = cvzone.overlayPNG(img, imgButtonLeft, (25, 293))
                            else:
                                print("Error loading button images. Skipping overlay.")
                        except Exception as e:
                            print("Error:", e)
                            pass
                    else:
                        print("Invalid dimensions for resizing. Skipping overlay.")
                else:
                    print("Error: Shirt image is None. Skipping overlay.")

            else:
                print("Error: Shirt image path does not exist. Skipping overlay.")
            
            # Check if lmist index exists and is within bounds
            if len(lmlist) > 16:
                if lmlist[16][1] < 170:
                    counterRight += 1
                    cv2.ellipse(img, (80, 260), (55, 55), 0, 0,
                                counterRight * selectionSpeed, (0, 255, 0), 20)
                    if counterRight * selectionSpeed > 360:
                        counterRight = 0
                        if imageNumber < len(listShirts) - 1:
                            imageNumber += 1
                elif lmlist[15][1] > 500:
                    counterLeft += 1
                    cv2.ellipse(img, (550, 360), (66, 66), 0, 0,
                                counterLeft * selectionSpeed, (0, 255, 0), 20)
                    if counterLeft * selectionSpeed > 360:
                        counterLeft = 0
                        if imageNumber > 0:
                            imageNumber -= 1
                else:
                    counterRight = 0
                    counterLeft = 0
            else:
                print("Error: Invalid index in lmlist. Skipping ellipse.")

        else:
            print("Human Object is Not detected.")

        cv2.imshow("archange", img)
        if cv2.waitKey(1) == 10:
            cv2.destroyAllWindows()
            flag = False
    
    return "Done"

if __name__ == "__main__":
    app.run(debug=True, port=8888)
