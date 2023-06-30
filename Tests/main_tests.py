import unittest, os, dbfread, json

class Test(unittest.TestCase):
    
    def test_1_packages(self):
        print("Testing if required packages are present...", end='')
        self.assertEqual(1,1,"\ntesting if packages are present, need to update this test")
        print("Passed")

    def test_2_sanity_check_files_available(self):
        print("Testing if the ground truth of required files info is available to conduct proper tests...", end='')
        files_present = os.listdir("./")
        self.assertIn("files_expected.json", files_present, "'files_expected.json' is absent, place it at '/Tests'")
        self.assertIn("field_names.json", files_present,"'field_names.json' is absent, place it at '/Tests'")
        print("Passed")
    
    def test_3_folder_and_files_available(self):
        print("Testing if shapefiles folder is present...",end='')
        folders = os.listdir("../Objective_Criteria")
        self.assertIn("shapefiles", folders, "'shapfiles' folder is absent, place it at '/Objective_Criteria/'")
        print("Passed")
        
        with open("./files_expected.json") as f:
            files_expected = json.load(f)

        shpfiles_present = os.listdir("../Objective_Criteria/shapefiles")

        print("Testing if necessary folders and files are present...",end='')
        for shpfile in files_expected:
            ## checking if the necessary folders are present in the shapefiles folder
            self.assertIn(shpfile, shpfiles_present, f"'{shpfile}' subfolder is absent in Objective_Criteria/shapefiles folder")
            subfolder = os.listdir(f"../Objective_Criteria/shapefiles/{shpfile}")
            ## checking if the necessary shpfile extensions are present for each shapefile
            for f in files_expected[shpfile]:
                self.assertIn(f, subfolder, "'{shpfile}/{f}' is absent")
        print("Passed")

    def test_4_field_names(self):
        print("Testing if names of fields are as expected...", end='')
        with open("./field_names.json") as f:
            field_names = json.load(f)

        for f in field_names:
            fields = dbfread.DBF(f"../Objective_Criteria/shapefiles/{f}/{f}.dbf").field_names
            for x in field_names[f]:
                self.assertIn(x,fields, "field '{x}' is absent or named incorrectly in 'f'")
        print("Passed")

if __name__ == '__main__':
    unittest.main()