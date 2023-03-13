import PySimpleGUI as gui
from PIL import Image
import re
import os

title = "DungeonFog Map Tile Assembler"
gui.theme("DarkAmber")

default_dir = os.getcwd()
default_text = default_dir

layout = [
	[gui.Text(title)],
	[],
	[gui.InputText(default_text, key="-INPUT-", size=(100, 1))],
	[gui.FolderBrowse("Browse", key="-DIRECTORY-", initial_folder=default_dir, enable_events=True)],
	[gui.Button("Start", key="-START-")],
	[gui.Text("", key="-OUTPUT-", text_color="red")],
	[gui.Multiline("", key="-FILE_LIST-", expand_x=True, horizontal_scroll=False, disabled=True, size=(0, 10))],
]

w = gui.Window(title, layout, resizable=True)

while True:
	event, values = w.read()
	if event in (gui.WIN_CLOSED, "Cancel"):
		break
	elif event == "-DIRECTORY-":
		w['-INPUT-'].Update(values['-DIRECTORY-'])
	elif event == "-START-":
		path = values['-INPUT-']
		if not os.path.isdir(path):
			w['-OUTPUT-'].Update("Path is not a directory.")
		else:
			failed = []
			assembled = []
			w['-OUTPUT-'].Update("")
			maps = {}
			pattern = re.compile("(.*)_tile_\d+_(\d+),(\d+)$")
			for f in os.listdir(path):
				name, ext = os.path.splitext(f)
				# print(name)
				matches = pattern.findall(name)
				if len(matches) == 0:
					print("No matches in filename '" + f + "'")
				else:
					matches = matches[0]
					# print(matches)
					map_name = matches[0]
					x = int(matches[1])
					y = int(matches[2])
					if not maps.keys().__contains__(map_name):
						maps[map_name] = []
					size = os.path.getsize(os.path.join(path, f))
					if size == 0:
						failed.append({ "filename": f, "reason": "size 0 bytes" })
					else:
						maps[map_name].append({ "x": x, "y": y, "filename": f, "name": name, "ext": ext })
			# print(maps)

			for map in maps:
				tiles = {}
				ext = None
				for tile in maps[map]:
					if ext is None:
						ext = tile['ext']
					image = Image.open(os.path.join(path, tile['filename']))
					tiles[(tile['x'],tile['y'])] = image
				print(tiles)
				max_x = max(x for x, y in tiles.keys())
				max_y = max(y for x, y in tiles.keys())
				width, height = tiles[(1, 1)].size
				print(width, height)

				total_width = width * max_x
				total_height = height * max_y
				print(total_width, total_height)
				assembled_map = Image.new("RGB", (total_width, total_height))
				for x in range(max_x + 1):
					for y in range(max_y + 1):
						image = tiles.get((x, y))
						if image is not None:
							x_pos = (x-1) * width
							y_pos = (y-1) * height
							assembled_map.paste(image, (x_pos, y_pos))
				output_path = os.path.join(path, "output")
				if not os.path.exists(output_path):
					os.mkdir(output_path)
				assembled_path = os.path.join(output_path, map + ext)
				assembled_map.save(assembled_path)
				assembled.append(assembled_path)
			output_text = "Assembled maps:\n" + "\n".join(assembled)
			if len(failed) > 0:
				s = "s"
				if len(failed) == 1:
					s = ""
				w['-OUTPUT-'].Update("Completed, but failed to load " + str(len(failed)) + " tile" + s + ".", text_color="red")
				output_text += "\n\nFailed tiles:\n"
				append_strings = []
				for fail in failed:
					append_strings.append(fail['filename'] + " (" + fail['reason'] + ")")
				output_text += "\n".join(append_strings)
			else:
				w['-OUTPUT-'].Update("Completed!", text_color="green")
			w['-FILE_LIST-'].Update(output_text)
