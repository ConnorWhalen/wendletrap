# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                         #
#   __    __               _ _      _                     #
#  / / /\ \ \___ _ __   __| | | ___| |_ _ __ __ _ _ __    #
#  \ \/  \/ / _ \ '_ \ / _` | |/ _ \ __| '__/ _` | '_ \   #
#   \  /\  /  __/ | | | (_| | |  __/ |_| | | (_| | |_) |  #
#    \/  \/ \___|_| |_|\__,_|_|\___|\__|_|  \__,_| .__/   #
#                                               |_|       #
#                                                         #
#   For creating sm (stepmania) and chart (clone hero)    #
#                files from MIDI data.                    #
#            Created by Connor July 10th 2021             #
#                                                         #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import click
import yaml

from serializers import chart_serializer, sm_serializer


@click.command()
@click.option('--filename', help='input .wendle file.', prompt=True)
@click.option('--filetype', help='output file type. (sm or chart)', prompt=True)
def create(filename, filetype):
	"""
		Creates an sm or chart file from the provided .wendle file.
		Should be run in the folder with the .wendle file and all referenced assets.
	"""
	if filetype == "sm":
		create_sm(filename)
	elif filetype == "chart":
		create_chart(filename)
	else:
		print("Filetype not recognized. Must be sm or chart.")


def create_sm(filename):
	file_data = {}
	charts_data = []
	with open(filename) as wendle_file:
		source_data = yaml.safe_load(wendle_file)

		source_file_data = source_data["file"]
		source_charts_data = source_data["sm_charts"]

		sm_filename = source_file_data["filename"]
		file_data["title"] = source_file_data.get("title", "")
		file_data["subtitle"] = source_file_data.get("subtitle", "")
		file_data["artist"] = source_file_data.get("artist", "")
		file_data["genre"] = source_file_data.get("genre", "")
		file_data["author"] = source_file_data.get("author", "")
		file_data["banner_image"] = source_file_data.get("banner_image", "")
		file_data["background_image"] = source_file_data.get("background_image", "")
		file_data["icon_image"] = source_file_data.get("icon_image", "")
		file_data["audio_file"] = source_file_data["audio_file"]
		file_data["offset_secs"] = float(source_file_data.get("offset_secs", 0))
		file_data["sample_start_secs"] = float(source_file_data.get("sample_start_secs", 0))
		file_data["sample_length_secs"] = float(source_file_data.get("sample_length_secs", 30))
		file_data["display_bpm"] = source_file_data.get("display_bpm", "")

		for source_chart_data in source_charts_data:
			chart_data = {}
			chart_data["author"] = source_chart_data.get("author", "")
			chart_data["difficulty_name"] = source_chart_data.get("difficulty_name", "")
			chart_data["difficulty_number"] = int(source_chart_data.get("difficulty_number", 0))
			chart_data["midi_filename"] = source_chart_data["midi_filename"]
			charts_data.append(chart_data)

	sm_serializer.serialize_file(
		sm_filename,
		file_data,
		charts_data
	)


def create_chart(filename):
	file_data = {}
	charts_data = []
	with open(filename) as wendle_file:
		source_data = yaml.safe_load(wendle_file)

		source_file_data = source_data["file"]
		source_charts_data = source_data["chart_charts"]

		file_data["title"] = source_file_data.get("title", "")
		file_data["artist"] = source_file_data.get("artist", "")
		file_data["genre"] = source_file_data.get("genre", "")
		file_data["author"] = source_file_data.get("author", "")
		file_data["offset_secs"] = float(source_file_data.get("offset_secs", 0))
		file_data["sample_start_secs"] = float(source_file_data.get("sample_start_secs", 0))

		file_data["album"] = source_file_data.get("album", "")
		file_data["year"] = source_file_data.get("year", "")

		file_data["song_length_secs"] = float(source_file_data.get("song_length_secs", 0))
		file_data["difficulty_number"] = source_file_data.get("difficulty_number", "")

		for source_chart_data in source_charts_data:
			chart_data = {}
			chart_data["midi_filename"] = source_chart_data["midi_filename"]
			charts_data.append(chart_data)

	chart_serializer.serialize_file(
		file_data,
		charts_data
	)


if __name__ == '__main__':
    create()