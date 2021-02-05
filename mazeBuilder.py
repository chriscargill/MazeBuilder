"""
Processes an image and stores the values along with the lua text in a file.
This file can then be added to the Roblox plugin for the plugin to create the image in a 3D space
"""
from PIL import Image
import sys
import time

args = sys.argv
image_name = args[1]
img_url = f"./{image_name}"

img = Image.open(img_url)
pix = list(img.getdata())
length, height = img.size

starting_length = round(length / 10)
starting_height = round(height / 10)

all_data = {}
all_data_to_be_popped = {}

column_index = 0
row_index = 0

saved_blocks = {}
adding_index = 0
index_dict = {}

def main():
    start_time = time.time()
    isCorrectDataType: bool
    isCorrectDataType = checkDataType()
    if isCorrectDataType:
        allDataToPython()
        biggestPossible(length, height)
        writeDataToFile()
    end_time = time.time()
    time_delta = end_time - start_time
    elapsed_time_in_minutes = round(time_delta / 60,2)
    print(f"Processed Image {img_url} in {elapsed_time_in_minutes} minutes.")

def allDataToPython():
    global row_index, column_index
    print("All data to python start")
    for R,G,B,*extra in pix:
        all_data[(row_index,column_index)] = (row_index,column_index,R,G,B)
        all_data_to_be_popped[(row_index,column_index)] = (row_index,column_index,R,G,B)
        if row_index == length - 1:
            column_index += 1
            row_index = 0
        else:
            row_index += 1
    print("All data to python ended")

def biggestPossible(length,height):
    global starting_height
    global starting_length
    # while the second array exists
    print(f"STARTING LENGTH: {starting_length} and STARTING HEIGHT: {starting_height} ")
    while starting_length != 0 and starting_height != 0:
        checkIfBlockSizeExists(starting_length,starting_height)
        if starting_length != 0:
            if starting_length == 1:
                starting_length -= 1
            else:
                subtract = round(starting_length / 10)
                if subtract == 0:
                    subtract = 1
                starting_length = starting_length - subtract
        if starting_height != 0:
            if starting_height == 1:
                starting_height -= 1
            else:
                subtract = round(starting_height / 10)
                if subtract == 0:
                    subtract = 1
                starting_height = starting_height - subtract
        print(f"starting_length: {starting_length}, height: {starting_height}")

def checkDataType():
    if img.format == "JPEG" or img.format =="PNG":
        if img.mode == "RGB" or img.mode == "RGBA":
            return True
        else:
            return False
    else: 
        return False

def checkIfBlockSizeExists(sizeX, sizeY):
    global index_dict
    global adding_index
    for current_indexer, values_list in all_data.items(): # this line??!?!?!
        isAllOneColor = True
            # Check to make sure that the value still EXISTS in the all_data_to_be_popped dictionary
        if current_indexer in all_data_to_be_popped.keys():
                # Check to make sure that the value in both dictionaries MATCH
            if all_data_to_be_popped[current_indexer] == values_list:
                    # if all points are still in the image bounds, then work on that data
                values_list_row, values_list_column, *rgb_Values = values_list
                if values_list_column + sizeY <= height and values_list_row + sizeX <= length:
                        # go through each row
                        # set the RGB values that we are looking for to be the RGB values of the first location in the box
                    current_row_index,current_column_index,current_R,current_G,current_B = all_data[(values_list_row,values_list_column)]
                    for y in range(0, sizeY):
                            # go through each column within the row
                        for x in range(0, sizeX):
                                # on the values within the image, check if they are all the same color
                            try:
                                    # grab the values of the current pixel
                                    # these x and y values are not the real x and y values, but only local to the box
                                    # we have to get the initial x and y values and then extrapolate the other values based on that
                                    # or find a way to convert each x and y to it's actual x and y
                                actual_x = values_list_row + x
                                actual_y = values_list_column + y
                                (row_index,column_index,R,G,B) = all_data_to_be_popped[(actual_x, actual_y)]

                                if R == current_R:
                                    if G == current_G:
                                        if B == current_B:
                                            try:
                                                    # Why am I using index_dict and not some other variable?
                                                index_dict[(actual_x,actual_y)] = [actual_x,actual_y,R,G,B]
                                                    # remove the data here, for this location and subsequent locations within the block
                                            except Exception as e:
                                                print(f"Huh? {e}")
                                        else:
                                                # If B is different:
                                            isAllOneColor = False
                                            index_dict = {}
                                            break
                                    else:
                                            #if G is different:
                                        isAllOneColor = False
                                        index_dict = {}
                                        break
                                else:
                                        # If R is different:
                                    isAllOneColor = False
                                    index_dict = {}
                                    break
                                if isAllOneColor == False:
                                    index_dict = {}
                                    break
                            except:
                                isAllOneColor = False
                                index_dict = {}
                                break
                        if isAllOneColor != True:
                                break
                else:
                    isAllOneColor = False
                if isAllOneColor and index_dict != {}:
                    for location in index_dict: # Process the block
                        if location == (values_list_row, values_list_column): # Get only the starting pixel location in the block
                            x,y = location
                            r_val,g_val,b_val,*etc_val = rgb_Values
                                # remove white space
                            if removeWhiteSpace(r_val,g_val,b_val):
                                print(f"White block found {location}, {sizeX} by {sizeY}")
                            else: # Save the data as a block
                                print(f"Storing block {location}, {sizeX} by {sizeY}")
                                saved_blocks[adding_index] = f"{{{x},{y},{r_val},{g_val},{b_val},{sizeX},{sizeY}}}"
                            # Remove all the block locations and values from the all_data_to_be_popped array
                        del all_data_to_be_popped[location]
                    index_dict = {}
                    adding_index += 1
                else:
                    pass
            else:
                pass # If the values in both dictionaries don't match
        else:
            pass # If the value does not exists in the all_data_to_be_popped dictionary

def removeWhiteSpace(r,g,b):
    if r == 255:
        if g == 255:
            if b == 255:
                return True
            else:
                return False
        else:
            return False
    else:
        return False
    
def writeDataToFile():
    f = open("blocks.txt", "w")
    f.write("{")
    for item in saved_blocks.values():
        f.write(f"{item},\n")
    f.write("}")
    f.close()
    a = open("all.txt", "w")
    for item in all_data.values():
        a.write(f"{item}\n")
    a.close()
    r = open("roblox_maze.txt", "w")
    a = """-- keep track of change the plugin does for them to be easily undone
local ChangeHistoryService = game:GetService("ChangeHistoryService")

-- Create a new toolbar section
local toolbar = plugin:CreateToolbar("Maze Builder")

-- Add a toolbar button
local newScriptButton = toolbar:CreateButton("Build the MazeKing!", "Let the plugin build the maze for you!", "rbxassetid://4458901886")
local myGUIWidget = DockWidgetPluginGuiInfo.new(
	Enum.InitialDockState.Float,
	true,
	true,
	100,
	100,
	150,
	150
)
local mazeWidget = plugin:CreateDockWidgetPluginGui("Scale", myGUIWidget)
mazeWidget.Title = "Maze Scaler"
script.Parent.SliderBG.Parent = mazeWidget




-- get the image data
local image_data = """
    b = """local function onNewScriptButtonClicked()
	print("Made you click")
	local scale = tonumber(mazeWidget.SliderBG.UserIn.Text)
	print("Scale is: ", scale)
	local image_folder =  Instance.new("Folder")
	image_folder.Parent = workspace
	image_folder.Name = "Maze Parts"
	local indexes = 0
	for i,v in pairs(image_data) do
		local x,y,r,g,b,l,w = unpack(v)
		local part = Instance.new("Part")
		part.Parent = image_folder
		part.Color = Color3.new(r, g, b)
		part.Position = Vector3.new(x*scale,0,y*scale)
		part.Size = Vector3.new(l*scale,25,w*scale)
		part.Name = "part"..x.."X"..y.."Y"..l.."L"..w.."W"
		part.Anchored = true
		indexes = indexes + 1
		if indexes == 20 then 
			wait(1)
			indexes = 0
		end
	end
	print("The maze has finished building!!!")
	ChangeHistoryService:SetWaypoint("Did something cool so we saved the progress")
end

-- Call the function once the button is clicked
newScriptButton.Click:Connect(onNewScriptButtonClicked)
    """
    r.write(a)
    r.write("{")
    for item in saved_blocks.values():
        r.write(f"{item},\n")
    r.write("}\n")
    r.write(b)
    r.close()

main()