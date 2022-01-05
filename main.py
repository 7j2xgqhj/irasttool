import tkinter as tk
from tkinter import filedialog
import os
import cv2
import numpy
import time
import subprocess
from PIL import Image
from collections import defaultdict
############################################################################################
#######メモ
#######これ単体だとこれ以上早くならなさそうなので、色相やらなんやらに基づいてファイル名を変更して
#######ソートやら検索やらを高速化する案
#######→粗くて速いふるいにかけてからやると早くなる理論(粗くて速いふるい=色相データのみの判断とか)
#######例えば"r"+str((Rの合計値)/画素数)+"g"+str((Gの合計値)/画素数)+"b"+str((Bの合計値)/画素数)
#######試してみないとわからないがこれで各値誤差+-1の範囲にしてふるいにかければそもそも処理しないといけない数は減る
#######同名ファイル問題を防ぐために語尾に何かしら重複しない文字列を追加したい、time系とか
#######新しくアプリを作るor実行前に行わせる
#######実行前に行わせる場合、実行済みのファイルか区別するために先頭に何かつけるとか
#######もしくは実行中のみ一時的に変更して後で戻すとか？（遅そう）
#############################################################################################
THIS_FOLDER=__file__.replace("\\"+os.path.basename(__file__),"")
#########################日本語を含むファイルパス対策用cv2.imread()###############################
##################################################################################################
def imread(filename, flags=cv2.IMREAD_COLOR, dtype=numpy.uint8):
    try:
        n = numpy.fromfile(filename, dtype)
        img = cv2.imdecode(n, flags)
        return img
    except Exception as e:
        print(e)
        return None
#####################################################################################################
#########################日本語を含むファイルパス対策用cv2.imwrite()###############################
##################################################################################################
def imwrite(filename, img, params=None):
    try:
        ext = os.path.splitext(filename)[1]
        result, n = cv2.imencode(ext, img, params)
        if result:
            with open(filename, mode='w+b') as f:
                n.tofile(f)
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False
#########################################################################################################
##########################################
def filename(path):
    return os.path.splitext(os.path.basename(path))[0],os.path.splitext(os.path.basename(path))[1]
##########################################
def removekakko(text):
    while True:
        start=text.find("(")
        fin=text.find(")")
        if start==-1:
            return text
        print(start,fin)
        text=text.replace(text[start:fin+1],"")

class Application(tk.Frame):
    def __init__(self,master):
        super().__init__(master)
        ###############対象フォルダの位置 なかったら終了
        self.file_path=tk.filedialog.askdirectory(initialdir=THIS_FOLDER)
        if self.file_path=="":
            exit()
        self.iqual_file_check_A()
        #self.rename(self.file_path)
        #self.rerename(self.file_path)
        print("fin")
    def search_png(self,path):#パス以下にある全てのpngのpathのリストを返す
        png_path_list=[]
        files=os.listdir(path)
        for file in files:
            if file.endswith(".png") or file.endswith(".jpg"):#.png or .jpgを見つけた場合
                png_path_list.append(path+"/"+file)
            elif os.path.isdir(path+"/"+file):#フォルダを見つけた場合
                png_path_list=png_path_list+self.search_png(path+"/"+file)#リストのため結合
        return png_path_list
    def change_file_path(self):
        path=tk.filedialog.askdirectory(initialdir=self.file_path)
        if path!="":
            self.file_path=path
    def iqual_file_check_AB(self):#対象フォルダAと対象フォルダBに共通する画像を抽出
        #Bの指定
        path=tk.filedialog.askdirectory(initialdir=self.file_path)
        if path!="":
            print("path searching...")
            fileA_paths=self.search_png(self.file_path)#A以下に存在する全てのpngのpathのリスト
            #print(len(fileA_paths))
            fileB_paths=self.search_png(path)#B以下に存在する全てのpngのpathのリスト
            #print(len(fileB_paths))
            if len(fileB_paths)>len(fileA_paths):#探索の都合的にAのほうが多いと早いので入れ替え
                fileA_paths,fileB_paths=fileB_paths,fileA_paths
            print("data loading...")
            #ここがかなり遅い
            start=time.time()
            fileA=[numpy.array(Image.open(i)) for i in fileA_paths]#Aのpngデータ群のリスト#imread()でもImage.openでも可
            fileB=[numpy.array(Image.open(i)) for i in fileB_paths]#Bのpngデータ群のリスト#ここを変えるだけ もしかしたらImage.openのほうが読み込みが速い？
            end=time.time()
            print(str(end-start)+"秒")
            print("state setting...")
            #もしかしてこっちも同じくらい遅い
            start=time.time()
            fileA_rgb_dict,fileA_path_dict=self.state(fileA,fileA_paths)#RGB:path,とpath:対応するfileAのnumpyのインデックスをもつ辞書
            fileB_rgb=[str(numpy.mean(arr[0::3],dtype="int"))+str(numpy.mean(arr[1::3],dtype="int"))+str(numpy.mean(arr[2::3],dtype="int")) for arr in fileB]
            end=time.time()
            print(str(end-start)+"秒")
            start=time.time()
            n=0
            nn=len(fileA)*len(fileB)
            print("A:"+str(len(fileA))+" B:"+str(len(fileB)))
            ans=[]
            for i,b in enumerate(fileB_rgb):
                for ap in fileA_rgb_dict[b]:
                        if self.equal(fileB[i],fileA[fileA_path_dict[ap]]) :
                            ans.append(ap)
                            ans.append(fileB_paths[i])
                            break
                n=n+len(fileA)
            if len(ans) !=0: 
                outputtext="Dim patharray("+str(len(ans))+')\nSet fs = WScript.CreateObject("WScript.Shell")\n'
                for i in range(0,len(ans)):
                    outputtext=outputtext+'Set patharray('+str(i)+') =fs.CreateShortcut("'+THIS_FOLDER+"\\result\\"+str(i)+'.lnk")\n'
                for i,path in zip(range(0,len(ans)),ans):
                    outputtext=outputtext+"patharray("+str(i)+').TargetPath = '+'"'+path+'"\n'
                for i in range(0,len(ans)):
                    outputtext=outputtext+"patharray("+str(i)+").save\n"
                try:
                    f=open(THIS_FOLDER+"\\linkmake.vbs",'w',encoding='shift_jis')
                    f.write(outputtext)
                    f.close()
                except Exception as e:
                    print(e)
                    try:
                        f=open(THIS_FOLDER+"\\linkmake.vbs",'w',encoding='s_jis')
                        f.write(outputtext)
                        f.close()
                    except Exception as e:
                        print(e)
                subprocess.run(["start",THIS_FOLDER+"\\linkmake.vbs"],shell=True)
                end=time.time()
                print(str(end-start)+"秒")
    def equal(self,a,b):
        
        if a.shape!=b.shape:#形が異なる場合
            return False
            #hight=min([a.shape[0],b.shape[0]])#たて
            #width=min([a.shape[0],b.shape[0]])#よこ
            #a=a[:hight-1,:width-1].copy()
            #b=b[:hight-1,:width-1].copy()
            print("reshape")
        sa=numpy.abs(a.astype(int)-b.astype(int))
        P=1#誤差許容範囲 緩いほどガバくなる ノイズかなんかで若干差があった場合用
        li=numpy.any(sa<P,axis=2)#
        percent=(len(li[li==True])/numpy.size(li))*100#一致率
        #print(str(percent)+"%")
        if percent>=99:
            return True
        else:
            return False
    def iqual_file_check_A(self):
        print("path searching...")
        fileA_paths=self.search_png(self.file_path)#A以下に存在する全てのpngのpathのリスト
        print("data loading...")
        fileA=[numpy.array(Image.open(i)) for i in fileA_paths]
        print("state setting...")
        fileA_rgb_dict,fileA_path_dict=self.state(fileA,fileA_paths)
        
        ans=[]
        for li in [fileA_rgb_dict[key] for key in list(fileA_rgb_dict.keys())]:
            for ap,bp in zip(li[:-1],li[1:]):
                if self.equal(fileA[fileA_path_dict[bp]],fileA[fileA_path_dict[ap]]) :
                    ans.append(ap)
                    ans.append(bp)
                    break
        if len(ans) !=0: 
                outputtext="Dim patharray("+str(len(ans))+')\nSet fs = WScript.CreateObject("WScript.Shell")\n'
                for i in range(0,len(ans)):
                    outputtext=outputtext+'Set patharray('+str(i)+') =fs.CreateShortcut("'+THIS_FOLDER+"\\result\\"+str(i)+'.lnk")\n'
                for i,path in zip(range(0,len(ans)),ans):
                    outputtext=outputtext+"patharray("+str(i)+').TargetPath = '+'"'+path+'"\n'
                for i in range(0,len(ans)):
                    outputtext=outputtext+"patharray("+str(i)+").save\n"
                f=open(THIS_FOLDER+"\\linkmake.vbs",'w',encoding='shift_jis')
                f.write(outputtext)
                f.close()
                subprocess.run(["start",THIS_FOLDER+"\\linkmake.vbs"],shell=True)
    def rename(self,path):
        fileA_paths=self.search_png(path)#A以下に存在する全てのpngのpathのリスト
        fileA=[imread(i) for i in fileA_paths]#Aのpngデータ群のリスト
        for a ,p in zip(fileA,fileA_paths):
            if ("R" in filename(p)[0] and "B" in filename(p)[0] and "G" in filename(p)[0]) ==False:
                print("rename")
                c=numpy.array(a).flatten()
                newname="("+filename(p)[0]+")"+"B"+str(round(numpy.mean(c[0::3])))+"G"+str(round(numpy.mean(c[1::3])))+"R"+str(round(numpy.mean(c[2::3])))
                os.rename(p,p.replace(filename(p)[0]+filename(p)[1],newname+filename(p)[1]))
    def rerename(self,path):
        fileA_paths=self.search_png(path)#A以下に存在する全てのpngのpathのリスト
        for p in fileA_paths:
            if ("R" in filename(p)[0] and "B" in filename(p)[0] and "G" in filename(p)[0]) ==True:
                print("rerename")
                newname=p.replace(filename(p)[0]+filename(p)[1],filename(p)[0].replace("(","")+filename(p)[1])
                newname=newname.replace(filename(p)[0].replace("(",""),filename(p)[0].replace("(","").replace(filename(p)[0][filename(p)[0].find(")"):],"").replace(filename(p)[1],""))
                os.rename(p,newname)
    def state(self,files,paths):
        out_rgb=defaultdict(list)
        out_path={}
        for index,arr_path in enumerate(zip(files,paths)):
            arr=arr_path[0]
            path=arr_path[1]
            out_rgb[str(numpy.mean(arr[0::3],dtype="int"))+str(numpy.mean(arr[1::3],dtype="int"))+str(numpy.mean(arr[2::3],dtype="int"))].append(path)
            out_path[path]=index
        return out_rgb,out_path
if __name__ =="__main__":
    root=tk.Tk()
    app=Application(root)
    app.mainloop()
