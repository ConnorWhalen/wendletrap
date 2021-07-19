# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                         #
#   __    __               _ _      _                     #
#  / / /\ \ \___ _ __   __| | | ___| |_ _ __ __ _ _ __    #
#  \ \/  \/ / _ \ '_ \ / _` | |/ _ \ __| '__/ _` | '_ \   #
#   \  /\  /  __/ | | | (_| | |  __/ |_| | | (_| | |_) |  #
#    \/  \/ \___|_| |_|\__,_|_|\___|\__|_|  \__,_| .__/   #
#                                               |_|       #
#                                                         #
#    For creating sm (stepmania) files from MIDI data.    #
#            Created by Connor July 10th 2021             #
#                                                         #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import os.path

import click

import sm_serializer

@click.command()
@click.option('--filename', help='input .wendle file.', prompt=True)
def create(filename):
	"""
		Creates an sm file from the provided .wendle file.
		Should be run in the folder with the .wendle file and all referenced assets.
	"""
	file_data = {}
	charts_data = []
	file_length = os.path.getsize(filename)
	with open(filename) as wendle_file:
		sm_filename = wendle_file.readline().rstrip()
		file_data["title"] = wendle_file.readline().rstrip()
		file_data["subtitle"] = wendle_file.readline().rstrip()
		file_data["artist"] = wendle_file.readline().rstrip()
		file_data["genre"] = wendle_file.readline().rstrip()
		file_data["author"] = wendle_file.readline().rstrip()
		file_data["banner_image"] = wendle_file.readline().rstrip()
		file_data["background_image"] = wendle_file.readline().rstrip()
		file_data["icon_image"] = wendle_file.readline().rstrip()
		file_data["audio_file"] = wendle_file.readline().rstrip()
		file_data["offset_secs"] = float(wendle_file.readline().rstrip())
		file_data["sample_start_secs"] = float(wendle_file.readline().rstrip())
		file_data["sample_length_secs"] = float(wendle_file.readline().rstrip())
		file_data["display_bpm"] = wendle_file.readline().rstrip()

		while wendle_file.tell() < file_length - 4:
			wendle_file.readline()
			chart_data = {}
			chart_data["author"] = wendle_file.readline().rstrip()
			chart_data["difficulty_name"] = wendle_file.readline().rstrip()
			chart_data["difficulty_number"] = int(wendle_file.readline().rstrip())
			chart_data["midi_filename"] = wendle_file.readline().rstrip()
			charts_data.append(chart_data)

	sm_serializer.serialize_file(
		sm_filename,
		file_data,
		charts_data
	)

if __name__ == '__main__':
    create()