import midi_parser

NO_NOTE_CODE = 0
NOTE_CODE = 1
HOLD_NOTE_CODE = 2
HOLD_END_CODE = 3
ROLL_NOTE_CODE = 4
HOLD_NOTES = [4, 5, 6, 7]
ROLL_NOTES = [8, 9, 10, 11]
MEASURE_THRESHOLD = 1 - (1/284) # half a 192 note as buffer

hold_note_ends = [-1, -1, -1, -1]


def serialize_file(filename, file_data, charts_data):
	"""
		Write sm file to filename.

		file_data is:
		{
			title: str
			subtitle: str
			artist: str
			genre: str
			author: str
			banner_image: str
			background_image: str
			icon_image: str
			audio_file: str
			offset_secs: float
			sample_start_secs: float
			sample_length_secs: float
			display_bpm: str
		}

		charts_data is:
		[
			{
				author: str
				difficulty_name: str
				difficulty_number: int
				midi_filename: str
			}
		]
	"""
	print(f"writing stepfile {filename}...")
	with open(filename, "w") as file_:
		file_.write(f"#TITLE:{file_data['title']};\n")
		file_.write(f"#SUBTITLE:{file_data['subtitle']};\n")
		file_.write(f"#ARTIST:{file_data['artist']};\n")
		file_.write(f"#TITLETRANSLIT:;\n")
		file_.write(f"#SUBTITLETRANSLIT:;\n")
		file_.write(f"#ARTISTTRANSLIT:;\n")
		file_.write(f"#GENRE:{file_data['genre']};\n")
		file_.write(f"#CREDIT:{file_data['author']};\n")
		file_.write(f"#BANNER:{file_data['banner_image']};\n")
		file_.write(f"#BACKGROUND:{file_data['background_image']};\n")
		file_.write(f"#LYRICSPATH:;\n")
		file_.write(f"#CDTITLE:{file_data['icon_image']};\n")
		file_.write(f"#MUSIC:{file_data['audio_file']};\n")
		file_.write(f"#OFFSET:{file_data['offset_secs']};\n")
		file_.write(f"#SAMPLESTART:{file_data['sample_start_secs']};\n")
		file_.write(f"#SAMPLELENGTH:{file_data['sample_length_secs']};\n")
		file_.write(f"#SELECTABLE:YES;\n")
		if len(file_data['display_bpm']) > 0:
			file_.write(f"#DISPLAYBPM:{file_data['display_bpm']};\n")
		_, tempos, _ = midi_parser.parse_file(charts_data[0]["midi_filename"])
		bpms_line = "#BPMS:"
		for i in range(len(tempos)):
			tempo = tempos[i]
			bpms_line += f"{tempo[1]}={tempo[0]}"
			if i < len(tempos)-1:
				bpms_line += ",\n"
			else:
				bpms_line += ";\n"
		file_.write(bpms_line)

		file_.write(f"#STOPS:;\n")
		file_.write(f"#BGCHANGES:;\n")
		file_.write(f"#KEYSOUNDS:;\n")
		file_.write(f"#ATTACKS:;\n")

		for chart_data in charts_data:
			print(f"writing chart {chart_data['midi_filename']}...")
			note_starts, tempos, time_sigs = midi_parser.parse_file(chart_data["midi_filename"])
			write_chart(
				file_,
				chart_data["author"],
				chart_data["difficulty_name"],
				chart_data["difficulty_number"],
				note_starts,
				tempos,
				time_sigs
			)
			print(f"chart {chart_data['midi_filename']} complete!")
	print(f"stepfile {filename} complete!")



def write_chart(file_, author, difficulty_name, difficulty_number, note_starts, tempos, time_sigs):
	file_.write("\n#NOTES:\n")
	file_.write("     dance-single:\n")
	file_.write(f"     {author}:\n")
	file_.write(f"     {difficulty_name}:\n")
	file_.write(f"     {difficulty_number}:\n")
	file_.write("     0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,"
					 "0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,"
					 "0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000:\n")
	current_measure = 0

	note_starts = beats_to_measures(note_starts, time_sigs)
	while len(note_starts) > 0:
		note_starts = write_measure(file_, note_starts, current_measure)
		if len(note_starts) > 0:
			file_.write(",\n")
		else:
			file_.write(";\n")
		current_measure += 1


def write_measure(file_, note_starts, current_measure):
	measure_notes = [note for note in note_starts if note[1] < current_measure + MEASURE_THRESHOLD]
	note_starts = [note for note in note_starts if note not in measure_notes]

	starts_in_measure = []
	ends_in_measure = [end for end in hold_note_ends if current_measure <= end < current_measure + MEASURE_THRESHOLD]
	for note in measure_notes:
		starts_in_measure.append(note[1])
		if (note[0] in HOLD_NOTES or note[0] in ROLL_NOTES) and note[2] < current_measure + MEASURE_THRESHOLD:
			ends_in_measure.append(note[2])

	items_in_measure = starts_in_measure + ends_in_measure
	items_in_measure = [int(item * 192 + 0.5) for item in items_in_measure]
	subdivision = 192 # 192 note is smallest subdivision
	for divisor in [3, 4, 6, 8, 12, 16, 24, 48]: # 64, 48, 32, 24, 16, 12, 8, and 4 notes
		# break if any times are not divisible
		if not any(item for item in items_in_measure if item % divisor != 0):
			subdivision = 192 / divisor

	lane_inputs = []
	for i in range(int(subdivision)):
		lane_inputs.append([NO_NOTE_CODE, NO_NOTE_CODE, NO_NOTE_CODE, NO_NOTE_CODE])
	for i in range(len(hold_note_ends)):
		if current_measure <= hold_note_ends[i] < current_measure + MEASURE_THRESHOLD:
			tick = int((hold_note_ends[i] - current_measure) * subdivision)
			lane_inputs[tick][i] = HOLD_END_CODE
	for note in measure_notes:
		start_tick = int((note[1] - current_measure) * subdivision + 0.5)
		if start_tick > subdivision - 1:
			print(f"START TICK {start_tick}")
			print(f"NOTE {note[1]}")
			print(f"SUBDIVISION {subdivision}")
		end_tick = int((note[2] - current_measure) * subdivision + 0.5)
		if note[0] in HOLD_NOTES or note[0] in ROLL_NOTES:
			if note[2] >= current_measure + 1:
				hold_note_ends[note[0] % 4] = note[2]
			else:
				lane_inputs[end_tick][note[0] % 4] = HOLD_END_CODE
			if note[0] in HOLD_NOTES:
				lane_inputs[start_tick][note[0] % 4] = HOLD_NOTE_CODE
			else: # note[0] in ROLL_NOTES
				lane_inputs[start_tick][note[0] % 4] = ROLL_NOTE_CODE
		else:
			lane_inputs[start_tick][note[0] % 4] = NOTE_CODE

	for lane_input in lane_inputs:
		file_.write(f"{lane_input[0]}{lane_input[1]}{lane_input[2]}{lane_input[3]}\n")

	return note_starts


def beats_to_measures(note_starts, time_sigs):
	for note in note_starts:
		note[1] = beat_to_measure(note[1], time_sigs)
		if note[0] in HOLD_NOTES or note[0] in ROLL_NOTES:
			note[2] = beat_to_measure(note[2], time_sigs)

	return note_starts


def beat_to_measure(beat_value, time_sigs):
	measure = 0
	beat = beat_value
	for i in range(len(time_sigs)):
		time_sig = time_sigs[i]
		if i == len(time_sigs) - 1 or beat_value < time_sigs[i+1][1]:
			measure += beat / time_sig[0]
			break
		else:
			measure += (time_sigs[i+1][1] - time_sig[1]) / time_sig[0]
			beat -= time_sigs[i+1][1] - time_sig[1]
	return measure