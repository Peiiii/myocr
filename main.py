from utils import reciept,yyzz,passport,idcard,trainTicket
import os,glob,cv2

def demo():
    input_dirs={'yyzz':'data/imgs/yyzz',
            'idcard':'data/imgs/idcard',
            'trainticket':'data/imgs/train_ticket',
            'passport':'data/imgs/passport',
            'reciept':'data/imgs/reciept'}
    apps={'yyzz':yyzz,
        'idcard':idcard,
        'trainticket':trainTicket,
        'reciept':reciept,
        'passport':passport}

    # flag = 'passport'
    # flag = 'yyzz'
    # flag = 'idcard'
    # flag = 'trainticket'
    flag = 'reciept'

    input_dir=input_dirs[flag]
    app=apps[flag].Predictor()
    fs=glob.glob(input_dir+'/*.jpg')
    for i,f in enumerate(fs):
        img=cv2.imread(f)
        res=app.predict(img)
        print(f,res)


if __name__ == '__main__':
    demo()