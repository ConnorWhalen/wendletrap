import os.path
import struct


HEADER_CHUNK_ID = 0x4D546864
TRACK_CHUNK_ID = 0x4D54726B

NOTE_OFF_EVENT = 0x8
NOTE_ON_EVENT = 0x9
NOTE_AFTERTOUCH_EVENT = 0xA
CONTROLLER_EVENT = 0xB
PROGRAM_CHANGE_EVENT = 0xC
CHANNEL_AFTERTOUCH_EVENT = 0xD
PITCH_BEND_EVENT = 0xE
META_EVENT = 0xF
META_EVENT_CHANNEL = 0xFF

META_TEMPO_EVENT = 0x51
META_TIME_OFFSET_EVENT = 0x54
META_TIME_SIG_EVENT = 0x58

TICKS_PER_SECOND = 0
TICKS_PER_BEAT = 1

SM_NOTE_LANE_MAP = {
	# notes
	36: 0, 39: 1,
	42: 2, 45: 3,
	# hold notes
	37: 4, 40: 5,
	43: 6, 46: 7,
	# mash notes
	38: 8, 41: 9,
	44: 10, 47: 11,
}
SM_HOLD_NOTES = [37, 38, 40, 41, 43, 44, 46, 47]

CHART_NOTE_LANE_MAP = {
	# notes
	36: 7, 38: 0,
	40: 1, 42: 2,
	44: 3, 46: 4,
	# hold notes
	37: 7, 39: 0,
	41: 1, 43: 2,
	45: 3, 47: 4,
	# FX
	48: 5, 49: 6,
	50: 8
}
CHART_HOLD_NOTES = [37, 39, 41, 43, 45, 47, 50]


def parse_file(filename, type_="sm"):
	"""
		note_starts is:
		[
			[
				lane: int
				start_beat: int
				end_beat: int
			]
		]

		tempos is:
		[
			[
				bpm: float
				measure: float
			]
		]

		time_sigs is:
		[
			[
				beats_per_measure: float
				measure: float
			]
		]
	"""
	note_starts = []
	tempos = []
	time_sigs = []
	file_length = os.path.getsize(filename)
	if type_ == "sm":
		note_lane_map = SM_NOTE_LANE_MAP
		hold_notes = SM_HOLD_NOTES
	elif type_ == "chart":
		note_lane_map = CHART_NOTE_LANE_MAP
		hold_notes = CHART_HOLD_NOTES
	with open(filename, 'rb') as file_:
		# Header Chunk
		header_chunk_size = parse_chunk_id_and_length(file_, HEADER_CHUNK_ID)
		if header_chunk_size != 6:
			print(f"MIDI HEADER CHUNK SIZE MISMATCH! Expected {6} got {header_chunk_size}")
			return
		# read unsigned short
		file_type = read_short(file_)
		if file_type != 0 and file_type != 1:
			print(f"UNSUPPORTED MIDI FILE TYPE {file_type}")
			return
		track_count = read_short(file_)
		time_division_upper = read_byte(file_)
		time_division_lower = read_byte(file_)
		time_division_mode = TICKS_PER_SECOND
		frames_per_second = 0
		ticks_per_frame = 0
		ticks_per_beat = 0
		if time_division_upper > 127:
			# frames per second
			frames_per_second = float(time_division_upper - 128)
			ticks_per_frame = float(time_division_lower)
			time_division_mode = TICKS_PER_SECOND
		else:
			# ticks per beat
			ticks_per_beat = float(time_division_upper * 256 + time_division_lower)
			time_division_mode = TICKS_PER_BEAT

		# Track Chunk
		track_chunk_length = parse_chunk_id_and_length(file_, TRACK_CHUNK_ID)

		# print stuff
		# print("file_type: " + str(file_type))
		# print("track_count" + str(track_count))
		# print("Track chunk length: " + str(track_chunk_length))
		# if time_division_mode == TICKS_PER_BEAT:
		# 	print("Ticks per beat: " + str(ticks_per_beat))
		# else:
		# 	print("Frames per second: " + str(frames_per_second))
		# 	print("Ticks per frame: " + str(ticks_per_frame))

		event_type = 0
		event_channel = 0
		event_param_1 = 0
		current_beat = 0.0
		hold_note_starts = {37: 0, 39: 0, 42: 0, 44: 0, 49: 0, 51: 0, 54: 0, 56: 0, 34: 0, 46: 0}
		while file_.tell() < file_length-1:
			event_delta_time = float(parse_variable_length(file_))
			if time_division_mode == TICKS_PER_SECOND:
				current_beat += (event_delta_time / ticks_per_frame) / frames_per_second
			else: # time_division_mode == TICKS_PER_BEAT
				current_beat += event_delta_time / ticks_per_beat

			split_byte = read_byte(file_)
			if split_byte >= 0x80:
				event_type = int(split_byte / 16)
				event_channel = split_byte % 16
				event_param_1 = read_byte(file_)
			else:
				event_param_1 = split_byte
			if event_type == NOTE_OFF_EVENT:
				note_number = event_param_1
				velocity = read_byte(file_)
				if note_number in hold_notes:
					note_starts.append([note_lane_map[note_number], hold_note_starts[note_number], current_beat])
			elif event_type == NOTE_ON_EVENT:
				note_number = event_param_1
				velocity = read_byte(file_)
				if note_number in hold_notes:
					hold_note_starts[note_number] = current_beat
				else:
					note_starts.append([note_lane_map[note_number], current_beat, 0])
			elif event_type == NOTE_AFTERTOUCH_EVENT:
				note_number = event_param_1
				aftertouch_value = read_byte(file_)
			elif event_type == CONTROLLER_EVENT:
				controller_number = event_param_1
				controller_value = read_byte(file_)
			elif event_type == PROGRAM_CHANGE_EVENT:
				program_number = event_param_1
				_unused = read_byte(file_)
			elif event_type == CHANNEL_AFTERTOUCH_EVENT:
				aftertouch_value = event_param_1
				_unused = read_byte(file_)
			elif event_type == PITCH_BEND_EVENT:
				pitch_bend_lower = event_param_1
				pitch_bend_upper = read_byte(file_)
				pitch_bend_value = pitch_bend_upper * 256 + pitch_bend_lower
			elif event_type == META_EVENT:
				meta_event_type = event_param_1
				meta_event_length = parse_variable_length(file_)
				print(f"META EVENT {meta_event_type} of length {meta_event_length}")
				if meta_event_type == META_TEMPO_EVENT:
					if meta_event_length != 3:
						print("TEMPO PANIC " + str(meta_event_length))
					us_per_quarter = 0
					for i in range(3):
						us_per_quarter *= 256
						us_per_quarter += read_byte(file_)
					tempo = 60.0 * 1000 * 1000 / us_per_quarter
					if len(tempos) == 0:
						tempos.append([tempo, 0.0])
					else:
						tempos.append([tempo, current_beat])
				elif meta_event_type == META_TIME_SIG_EVENT:
					if meta_event_length != 4:
						print("TIME SIG PANIC " + str(meta_event_length))
					numerator = read_byte(file_)
					denominator = read_byte(file_) # only using numerator
					read_byte(file_)
					read_byte(file_)
					time_sigs.append([numerator, current_beat])
				else:
					for i in range(meta_event_length):
						meta_event_byte = read_byte(file_)
			else:
				print(f"UNRECOGNIZED EVENT TYPE {event_type}")
	return note_starts, tempos, time_sigs


def parse_chunk_id_and_length(file_, chunk_id):
	file_chunk_id = read_int(file_)
	if file_chunk_id != chunk_id:
		print(f"MIDI HEADER CHUNK ID MISMATCH! Expected {chunk_id} got {file_chunk_id}")
		return
	return read_int(file_)


def parse_variable_length(file_):
	val = 0x80
	total = 0
	while val >= 0x80:
		val = read_byte(file_)
		total *= 0x80
		total += val % 0x80
	return total

def read_byte(file_):
	return struct.unpack('>B', file_.read(1))[0]

def read_short(file_):
	return struct.unpack('>H', file_.read(2))[0]

def read_int(file_):
	return struct.unpack('>I', file_.read(4))[0]
