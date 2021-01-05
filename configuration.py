import os


class ConfigClass:

    def __init__(self):
        # link to a zip file in google drive with your pretrained model
        self._model_url = 'https://drive.google.com/file/d/1oXRanO6zdOkZbIZkEZ16R00I2JWd_M_Z/view?usp=sharing'
        # False/True flag indicating whether the testing system will download 
        # and overwrite the existing model files. In other words, keep this as 
        # False until you update the model, submit with True to download 
        # the updated model (with a valid model_url), then turn back to False 
        # in subsequent submissions to avoid the slow downloading of the large 
        # model file with every submission.
        self._download_model = False

        self.corpusPath = 'C:/Users/User/PycharmProjects/Search_Engine_AN/data'
        self.savedFileMainFolder = 'output_path'
        self.saveFilesWithStem = self.savedFileMainFolder + "/WithStem"
        self.saveFilesWithoutStem = self.savedFileMainFolder + "/WithoutStem"
        self.toStem = False
        self.oneFile = True
        self.cutFreqBy = 1000


        print('Project was created successfully..')

    def setoneFile(self,bool):
        self.oneFile = bool
    def getoneFile(self):
        return self.oneFile

    def get_outputPath(self):
        if self.toStem:
            try:
                if not os.path.exists(self.saveFilesWithStem):
                    os.makedirs(self.saveFilesWithStem)
            except:
                pass
                #print("fail in creating output folder")
            return self.saveFilesWithStem + "/"
        else:
            try:
                if not os.path.exists(self.saveFilesWithoutStem):
                    os.makedirs(self.saveFilesWithoutStem)
            except:
                pass
                #print("fail in creating output folder")
            return self.saveFilesWithoutStem + "/"

    def get__corpusPath(self):
        return self.corpusPath

    def set_corpusPath(self, corpusPath):
        self.corpusPath = corpusPath

    def get_saveFilesWithStem(self):
        return self.saveFilesWithStem

    def get_saveFilesWithoutStem(self):
        return self.saveFilesWithStem

    def get_savedFileMainFolder(self):
        return self.savedFileMainFolder

    def set_savedFileMainFolder(self, path):
        self.savedFileMainFolder = path + "/WithStem"
        self.saveFilesWithStem = path+ "/WithStem"
        self.saveFilesWithoutStem = path + "/WithoutStem"
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except:
            pass
            #print("fail in creating main output folder")

    def set_toStem(self, bool):
        self.toStem = bool

    def get_spellingCorrection(self):
        return self.spellingCorrection

    def set_spellingCorrection(self, flag):
        self.spellingCorrection = flag

    def get_model_url(self):
        return self._model_url

    def get_download_model(self):
        return self._download_model

    def get_cut_by(self):
        return self.cutFreqBy

    def set_cut_by(self,num):
        self.cutFreqBy = num/6