from copy import deepcopy
from dataclasses import dataclass
from typing import Any

import parsers.midi_parser as midi_parser


STAR_POWER_LANE = 8


@dataclass
class ChartFileData:
	title: str
	artist: str
	genre: str
	author: str
	offset_secs: float
	sample_start_secs: float

	album: str
	year: str

	song_length_secs: str
	difficulty_number: str


@dataclass
class ChartChartData:
	midi_filename: str


def serialize_file(file_data: ChartFileData, charts_data: list[ChartChartData]) -> None:
	print(f"writing chart file...")
	with open("notes.chart", "w") as file_:
		file_.write("[Song]\n")
		file_.write("{\n")
		file_.write(f"  Name = \"{file_data.title}\"\n")
		file_.write(f"  Artist = \"{file_data.artist}\"\n")
		file_.write(f"  Charter = \"{file_data.author}\"\n")
		file_.write(f"  Album = \"{file_data.album}\"\n")
		file_.write(f"  Year = \", {file_data.year}\"\n")
		file_.write("  Offset = 0\n")
		file_.write("  Resolution = 192\n")
		file_.write("  Player2 = bass\n")
		file_.write("  Difficulty = 0\n")
		file_.write("  PreviewStart = 0\n")
		file_.write("  PreviewEnd = 0\n")
		file_.write(f"  Genre = \"{file_data.genre}\"\n")
		file_.write("  MediaType = \"cd\"\n")
		file_.write("  MusicStream = \"song.ogg\"\n")
		file_.write("}\n")
		file_.write("[SyncTrack]\n")
		file_.write("{\n")

		note_starts, tempos, time_sigs = midi_parser.parse_file(charts_data[0].midi_filename, type_="chart")

		tempos_copy = deepcopy(tempos)
		time_sigs_copy = deepcopy(time_sigs)
		while len(tempos_copy) > 0 or len(time_sigs_copy) > 0:
			if len(tempos_copy) == 0:
				tempo_or_timesigb = False
			elif len(time_sigs_copy) == 0:
				tempo_or_timesigb = True
			elif tempos_copy[0][1] < time_sigs_copy[0][1]:
				tempo_or_timesigb = True
			else:
				tempo_or_timesigb = False

			if tempo_or_timesigb:
				tempo = tempos_copy.pop(0)
				tempo_bpm = tempo[0]
				tempo_measure = tempo[1]
				file_.write(f"  {write_measure_number(tempo_measure)} = B {write_3_decimal_number(tempo_bpm)}\n")
			else:
				time_sig = time_sigs_copy.pop(0)
				time_sig_value = time_sig[0]
				time_sig_measure = time_sig[1]
				file_.write(f"  {write_measure_number(time_sig_measure)} = TS {time_sig_value}\n")


		file_.write("}\n")
		file_.write("[Events]\n")
		file_.write("{\n")


		sections = []

		for section in sections:
			section_title = section[0]
			section_measure = section[1]
			file_.write(f"  {write_measure_number(section_measure)} = E \"section {section_title}\"\n")


		file_.write("}\n")
		file_.write("[ExpertSingle]\n")
		file_.write("{\n")

		for note_start in note_starts:
			note_lane = note_start[0]
			note_start_measure = note_start[1]
			note_end_measure = note_start[2]
			if note_end_measure > 0:
				note_length = float(note_end_measure) - float(note_start_measure)
			else:
				note_length = 0
			if note_lane == STAR_POWER_LANE:
				note_type = "S"
				note_lane = 2
			else:
				note_type = "N"
			file_.write(f"  {write_measure_number(note_start_measure)} = {note_type} {note_lane} {write_measure_number(note_length)}\n")

		file_.write("}\n")

	print(f"chart file complete!")

	print(f"writing ini file...")
	with open("song.ini", "w") as file_:
		file_.write("[song]\n")
		file_.write(f"name = {file_data.title}\n")
		file_.write(f"artist = {file_data.artist}\n")
		file_.write(f"album = {file_data.album}\n")
		file_.write(f"genre = {file_data.genre}\n")
		file_.write(f"year = {file_data.year}\n")
		file_.write(f"diff_band = -1\n")
		file_.write(f"diff_guitar = {file_data.difficulty_number}\n")
		file_.write("diff_bass = -1\n")
		file_.write("diff_drums = -1\n")
		file_.write("diff_keys = -1\n")
		file_.write("diff_guitarghl = -1\n")
		file_.write("diff_bassghl = -1\n")
		file_.write(f"preview_start_time = {write_3_decimal_number(file_data.sample_start_secs)}\n")
		file_.write("icon = \n")
		file_.write("album_track = 0\n")
		file_.write("playlist_track = 0\n")
		file_.write("video_start_time = 0\n")
		file_.write(f"charter = {file_data.author}\n")
		file_.write(f"delay = {-write_3_decimal_number(file_data.offset_secs)}\n")
		file_.write(f"song_length = {write_3_decimal_number(file_data.song_length_secs)}\n")

	print(f"ini file complete!")


def write_measure_number(number_str: str) -> int:
	return int(float(number_str)*192)


def write_3_decimal_number(number_str: str) -> int:
	return int(float(number_str)*1000)
