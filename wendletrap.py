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

from serializers.chart_serializer import serialize_file as serialize_chart, ChartChartData, ChartFileData
from serializers.sm_serializer import serialize_file as serialize_sm, SmChartData, SmFileData


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

		file_data = SmFileData(
			sm_filename=source_file_data["sm_filename"]
			title=source_file_data.get("title", ""),
			subtitle=source_file_data.get("subtitle", ""),
			artist=source_file_data.get("artist", ""),
			genre=source_file_data.get("genre", ""),
			author=source_file_data.get("author", ""),
			banner_image=source_file_data.get("banner_image", ""),
			background_image=source_file_data.get("background_image", ""),
			icon_image=source_file_data.get("icon_image", ""),
			audio_file=source_file_data["audio_file"],
			offset_secs=float(source_file_data.get("offset_secs", 0)),
			sample_start_secs=float(source_file_data.get("sample_start_secs", 0)),
			sample_length_secs=float(source_file_data.get("sample_length_secs", 30)),
			display_bpm=source_file_data.get("display_bpm", ""),
		)

		charts_data = [
			SmChartData(
				author=source_chart_data.get("author", ""),
				difficulty_name=source_chart_data.get("difficulty_name", ""),
				difficulty_number=int(source_chart_data.get("difficulty_number", 0)),
				midi_filename=source_chart_data["midi_filename"],
			) for source_chart_data in source_charts_data
		]

	serialize_sm(
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

		file_data = ChartFileData(
			title=source_file_data.get("title", ""),
			artist=source_file_data.get("artist", ""),
			genre=source_file_data.get("genre", ""),
			author=source_file_data.get("author", ""),
			offset_secs=float(source_file_data.get("offset_secs", 0)),
			sample_start_secs=float(source_file_data.get("sample_start_secs", 0)),
			album=source_file_data.get("album", ""),
			year=source_file_data.get("year", ""),
			song_length_secs=float(source_file_data.get("song_length_secs", 0)),
			difficulty_number=source_file_data.get("difficulty_number", ""),
		)

		chart_data = [
			ChartChartData(
				midi_filename=source_chart_data["midi_filename"]
			) for source_chart_data in source_charts_data
		]

	serialize_chart(
		file_data,
		charts_data
	)


if __name__ == '__main__':
    create()