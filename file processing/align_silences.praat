form Align silences
    sentence Input_folder ./2. First Normalization/
    sentence Output_folder ./3. Trim/
    positive Pre_onset_ms 100
    positive Total_duration_ms 2500
    positive Intensity_threshold_dB 50
endform

preOnset = pre_onset_ms / 1000
totalDuration = total_duration_ms / 1000

# Create output directory if necessary
createDirectory: output_folder$

# Get all WAV files
Create Strings as file list: "wavFiles", input_folder$ + "/*.wav"
fileList = selected("Strings")
nFiles = Get number of strings

for i from 1 to nFiles

    selectObject: fileList
    fileName$ = Get string: i

    # Read sound
    sound = Read from file: input_folder$ + "/" + fileName$
    endTime = Get total duration

    # Create intensity contour
    To Intensity: 75, 0, "yes"
    intensity = selected("Intensity")

    # Define onset threshold
	threshold = intensity_threshold_dB

    # Find first intensity frame above threshold
    nFrames = Get number of frames
    onset = undefined

    for j from 1 to nFrames
    		value = Get value in frame: j

    		if onset = undefined
        		if value <> undefined
            		if value >= threshold
                		onset = Get time from frame number: j
            		endif
        		endif
    		endif
	endfor

    if onset <> undefined

        # Keep 100 ms before detected onset
        startTime = onset - preOnset

        if startTime >= 0
            selectObject: sound
            Extract part: startTime, endTime, "rectangular", 1, "no"
            trimmed = selected("Sound")
        else
            # Original recording doesn't have a full 100 ms lead-in;
            # generate synthetic silence to pad it out so the result
            # always starts with exactly preOnset ms of silence.
            padDuration = preOnset - onset

            selectObject: sound
            Extract part: 0, endTime, "rectangular", 1, "no"
            clipped = selected("Sound")

            sampleRate = Get sampling frequency
            silence = Create Sound from formula: "silence", 1, 0, padDuration, sampleRate, "0"

            selectObject: silence, clipped
            Concatenate
            trimmed = selected("Sound")

            removeObject: silence, clipped
        endif

        # Ensure the file is always exactly totalDuration long by
        # padding with trailing silence or trimming the tail.
        selectObject: trimmed
        currentDuration = Get total duration

        if currentDuration < totalDuration
            padEnd = totalDuration - currentDuration
            sampleRate = Get sampling frequency

            silenceEnd = Create Sound from formula: "silenceEnd", 1, 0, padEnd, sampleRate, "0"

            selectObject: trimmed, silenceEnd
            Concatenate
            final = selected("Sound")

            removeObject: silenceEnd, trimmed
        elsif currentDuration > totalDuration
            selectObject: trimmed
            Extract part: 0, totalDuration, "rectangular", 1, "no"
            final = selected("Sound")

            removeObject: trimmed
        else
            final = trimmed
        endif

        selectObject: final
        Save as WAV file: output_folder$ + "/" + fileName$

        removeObject: final

    else
        printline fileName$, ": NO ONSET DETECTED"
    endif

    removeObject: intensity
    removeObject: sound

endfor

removeObject: fileList

printline "Done."